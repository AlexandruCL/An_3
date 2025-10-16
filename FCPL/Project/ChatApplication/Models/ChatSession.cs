using System;
using System.Collections.Generic;
using System.Linq;

namespace ChatApplication.Models
{
    public class ChatSession
    {
        private List<ChatMessage> messages = new List<ChatMessage>();

        public void AddMessage(ChatMessage message)
        {
            messages.Add(message);
        }

        public List<ChatMessage> GetMessages()
        {
            return messages;
        }

        public string GetChatLog()
        {
            return string.Join(Environment.NewLine, messages.Select(m => m.ToString()));
        }

        public void Clear()
        {
            messages.Clear();
        }
    }
}