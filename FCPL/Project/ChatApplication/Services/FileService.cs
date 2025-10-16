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