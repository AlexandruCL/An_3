using System;
using System.IO;
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
        private TcpClient? _client;
        private NetworkStream? _stream;
        private readonly int _listenPort;
        private readonly int _connectPort;
        private bool _isRunning;

        public event Action<ChatMessage>? MessageReceived;

        public NetworkService(int listenPort, int connectPort)
        {
            _listenPort = listenPort;
            _connectPort = connectPort;
            StartServer();
            _ = Task.Run(async () => await ConnectToServerAsync());
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
                Console.WriteLine($"Server start error: {ex.Message}");
            }
        }

        private async Task ConnectToServerAsync()
        {
            await Task.Delay(2000);
            
            for (int i = 0; i < 10; i++)
            {
                try
                {
                    _client = new TcpClient();
                    await _client.ConnectAsync(IPAddress.Loopback, _connectPort);
                    _stream = _client.GetStream();
                    _ = Task.Run(async () => await ReceiveMessagesAsync());
                    Logger.LogMessage($"Connected to port {_connectPort}");
                    Console.WriteLine($"Connected to port {_connectPort}");
                    break;
                }
                catch
                {
                    await Task.Delay(1000);
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
                    _client = client;
                    _stream = client.GetStream();
                    _ = Task.Run(async () => await ReceiveMessagesAsync());
                    Console.WriteLine($"Client connected on port {_listenPort}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Listen error: {ex.Message}");
                }
            }
        }

        private async Task ReceiveMessagesAsync()
        {
            byte[] buffer = new byte[4096];
            
            while (_isRunning && _stream != null)
            {
                try
                {
                    int bytesRead = await _stream.ReadAsync(buffer, 0, buffer.Length);
                    if (bytesRead > 0)
                    {
                        string json = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        var message = JsonConvert.DeserializeObject<ChatMessage>(json);
                        if (message != null)
                        {
                            Logger.LogMessage($"Message received from {message.Username}: {message.Text}");
                            MessageReceived?.Invoke(message);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Logger.LogError($"Receive error: {ex.Message}");
                    Console.WriteLine($"Receive error: {ex.Message}");
                    break;
                }
            }
        }

        public async void SendMessage(ChatMessage message)
        {
            if (_stream != null && _stream.CanWrite)
            {
                try
                {
                    string json = JsonConvert.SerializeObject(message);
                    byte[] data = Encoding.UTF8.GetBytes(json);
                    await _stream.WriteAsync(data, 0, data.Length);
                    Logger.LogMessage($"Message sent by {message.Username}: {message.Text}");
                }
                catch (Exception ex)
                {
                    Logger.LogError($"Send error: {ex.Message}");
                    Console.WriteLine($"Send error: {ex.Message}");
                }
            }
        }

        public void Stop()
        {
            _isRunning = false;
            _stream?.Close();
            _client?.Close();
            _server?.Stop();
        }
    }
}