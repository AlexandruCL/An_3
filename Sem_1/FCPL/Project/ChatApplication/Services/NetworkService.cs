using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using ChatApplication.Models;
using ChatApplication.Utils;
using Newtonsoft.Json;

namespace ChatApplication.Services
{
    public class NetworkService
    {
        private TcpListener? _server;
        private List<TcpClient> _clients = new List<TcpClient>();
        private readonly int _listenPort;
        private bool _isRunning;
        private readonly int[] _allPorts = { 5000, 5001, 5002, 5003, 5004 };

        public event Action<ChatMessage>? MessageReceived;

        public NetworkService(int listenPort)
        {
            _listenPort = listenPort;
            StartServer();
            _ = Task.Run(async () => await ConnectToOtherUsersAsync());
        }

        private void StartServer()
        {
            try
            {
                _server = new TcpListener(IPAddress.Loopback, _listenPort);
                _server.Start();
                _isRunning = true;
                _ = Task.Run(async () => await ListenForClientsAsync());
                Logger.LogMessage($"Server started on port {_listenPort}");
            }
            catch (Exception ex)
            {
                Logger.LogError($"Server start error: {ex.Message}");
            }
        }

        private async Task ConnectToOtherUsersAsync()
        {
            await Task.Delay(2000);
            
            foreach (var port in _allPorts)
            {
                if (port == _listenPort) continue;
                
                try
                {
                    var client = new TcpClient();
                    await client.ConnectAsync(IPAddress.Loopback, port);
                    lock (_clients)
                    {
                        _clients.Add(client);
                    }
                    _ = Task.Run(async () => await ReceiveMessagesAsync(client));
                    Logger.LogMessage($"Connected to port {port}");
                }
                catch
                {
                    // Port not available, user not connected
                }
            }
        }

        private async Task ListenForClientsAsync()
        {
            while (_isRunning && _server != null)
            {
                try
                {
                    var client = await _server.AcceptTcpClientAsync();
                    lock (_clients)
                    {
                        _clients.Add(client);
                    }
                    _ = Task.Run(async () => await ReceiveMessagesAsync(client));
                    Logger.LogMessage($"Client connected on port {_listenPort}");
                }
                catch (Exception ex)
                {
                    Logger.LogError($"Listen error: {ex.Message}");
                }
            }
        }

        private async Task ReceiveMessagesAsync(TcpClient client)
        {
            NetworkStream? stream = null;
            try
            {
                stream = client.GetStream();
                byte[] buffer = new byte[4096];
                
                while (_isRunning && client.Connected)
                {
                    int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                    if (bytesRead > 0)
                    {
                        string json = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        var message = JsonConvert.DeserializeObject<ChatMessage>(json);
                        if (message != null)
                        {
                            MessageReceived?.Invoke(message);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.LogError($"Receive error: {ex.Message}");
            }
            finally
            {
                stream?.Close();
                lock (_clients)
                {
                    _clients.Remove(client);
                }
                client.Close();
            }
        }

        public async void BroadcastMessage(ChatMessage message)
        {
            string json = JsonConvert.SerializeObject(message);
            byte[] data = Encoding.UTF8.GetBytes(json);

            List<TcpClient> clientsCopy;
            lock (_clients)
            {
                clientsCopy = new List<TcpClient>(_clients);
            }

            foreach (var client in clientsCopy)
            {
                try
                {
                    if (client.Connected)
                    {
                        var stream = client.GetStream();
                        await stream.WriteAsync(data, 0, data.Length);
                    }
                }
                catch (Exception ex)
                {
                    Logger.LogError($"Broadcast error: {ex.Message}");
                }
            }
        }

        public void Stop()
        {
            _isRunning = false;
            
            lock (_clients)
            {
                foreach (var client in _clients)
                {
                    client.Close();
                }
                _clients.Clear();
            }
            
            _server?.Stop();
        }
    }
}