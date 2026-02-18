using System;

namespace ChatApplication.Models
{
    public class ChatMessage // Renamed from Message
    {
        public string Username { get; set; }
        public DateTime Timestamp { get; set; }
        public string Text { get; set; }

        public ChatMessage(string username, string text)
        {
            Username = username;
            Text = text;
            Timestamp = DateTime.Now;
        }

        public override string ToString()
        {
            return $"[{Timestamp:HH:mm:ss}] {Username}: {Text}";
        }
    }
}