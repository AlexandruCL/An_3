using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ChatApplication.Models;

namespace ChatApplication.Services
{
    public class FileService
    {
        private readonly string _filePath;

        public FileService(string userName)
        {
            string appDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ChatApplication");
            Directory.CreateDirectory(appDirectory);
            _filePath = Path.Combine(appDirectory, $"chat_log_{userName.Replace(" ", "_")}.txt");
        }

        public void SaveMessages(List<ChatMessage> messages)
        {
            var lines = messages.Select(m => $"{m.Timestamp:yyyy-MM-dd HH:mm:ss}|{m.Username}|{m.Text}");
            File.WriteAllLines(_filePath, lines);
        }

        // NEW METHOD for saving conversations to project root/SavedChats folder
        public void SaveConversation(List<ChatMessage> messages, string userName)
        {
            // Get the project root directory (goes up from bin\Debug\net8.0-windows to project root)
            string projectRoot = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, @"..\..\..\"));
            string savedChatsDirectory = Path.Combine(projectRoot, "SavedChats");
            Directory.CreateDirectory(savedChatsDirectory);
            
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string fileName = $"conversation_{userName.Replace(" ", "_")}_{timestamp}.txt";
            string filePath = Path.Combine(savedChatsDirectory, fileName);

            var lines = new List<string>
            {
                $"=== Chat Conversation ===",
                $"User: {userName}",
                $"Saved: {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
                $"Messages: {messages.Count}",
                $"========================\n"
            };

            foreach (var msg in messages)
            {
                lines.Add($"[{msg.Timestamp:yyyy-MM-dd HH:mm:ss}] {msg.Username}: {msg.Text}");
            }

            File.WriteAllLines(filePath, lines);
        }

        public List<ChatMessage> LoadMessages()
        {
            var messages = new List<ChatMessage>();

            if (!File.Exists(_filePath))
                return messages;

            try
            {
                var lines = File.ReadAllLines(_filePath);
                foreach (var line in lines)
                {
                    var parts = line.Split('|');
                    if (parts.Length == 3)
                    {
                        var message = new ChatMessage(parts[1], parts[2])
                        {
                            Timestamp = DateTime.Parse(parts[0])
                        };
                        messages.Add(message);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Load error: {ex.Message}");
            }

            return messages;
        }
    }
}