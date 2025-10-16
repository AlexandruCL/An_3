using System;
using System.Drawing;
using System.Windows.Forms;
using ChatApplication.Models;
using ChatApplication.Services;
using ChatApplication.Utils;

namespace ChatApplication.Forms
{
    public partial class MainForm : Form
    {
        private ChatSession chatSession;
        private NetworkService networkService;
        private FileService fileService;
        private PrintService printService;
        private string userName;

        public MainForm()
        {
            InitializeComponent();
            
            // Ask user to choose their role
            var result = MessageBox.Show("Are you User A?\n\nClick 'Yes' for User A\nClick 'No' for User B", 
                "Select User", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            
            if (result == DialogResult.Yes)
            {
                userName = "User A";
                textBoxUsername.Text = "User A";
                this.Text = "Chat Application - User A";
                networkService = new NetworkService(5000, 5001);
                Logger.LogMessage("User A instance started");
            }
            else
            {
                userName = "User B";
                textBoxUsername.Text = "User B";
                this.Text = "Chat Application - User B";
                networkService = new NetworkService(5001, 5000);
                Logger.LogMessage("User B instance started");
            }

            chatSession = new ChatSession();
            fileService = new FileService(userName);
            printService = new PrintService();

            networkService.MessageReceived += OnMessageReceived;
            LoadChatHistory();
        }

        private void LoadChatHistory()
        {
            var messages = fileService.LoadMessages();
            foreach (var msg in messages)
            {
                chatSession.AddMessage(msg);
                DisplayMessage(msg);
            }
            Logger.LogMessage($"{userName}: Loaded {messages.Count} messages from history");
        }

        private void ButtonSend_Click(object sender, EventArgs e)
        {
            if (!string.IsNullOrWhiteSpace(textBoxMessage.Text) && !string.IsNullOrWhiteSpace(textBoxUsername.Text))
            {
                var message = new ChatMessage(textBoxUsername.Text, textBoxMessage.Text);
                chatSession.AddMessage(message);
                networkService.SendMessage(message);
                DisplayMessage(message);
                Logger.LogMessage($"[{textBoxUsername.Text}] SENT: {textBoxMessage.Text}");
                textBoxMessage.Clear();
                textBoxMessage.Focus();
            }
            else
            {
                MessageBox.Show("Please enter both username and message.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                Logger.LogError($"{userName}: Attempted to send empty message");
            }
        }

        private void OnMessageReceived(ChatMessage message)
        {
            if (richTextBoxChat.InvokeRequired)
            {
                richTextBoxChat.Invoke(new Action(() => OnMessageReceived(message)));
                return;
            }

            chatSession.AddMessage(message);
            DisplayMessage(message);
            Logger.LogMessage($"[{message.Username}] RECEIVED: {message.Text}");
        }

        private void DisplayMessage(ChatMessage message)
        {
            richTextBoxChat.SelectionStart = richTextBoxChat.TextLength;
            richTextBoxChat.SelectionLength = 0;

            richTextBoxChat.SelectionColor = Color.Gray;
            richTextBoxChat.AppendText($"[{message.Timestamp:HH:mm:ss}] ");

            richTextBoxChat.SelectionColor = message.Username == textBoxUsername.Text ? Color.Blue : Color.Green;
            richTextBoxChat.AppendText($"{message.Username}: ");

            richTextBoxChat.SelectionColor = Color.Black;
            richTextBoxChat.AppendText($"{message.Text}\n");
        }

        private void ButtonSave_Click(object sender, EventArgs e)
        {
            try
            {
                fileService.SaveMessages(chatSession.GetMessages());
                MessageBox.Show("Conversation saved successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                Logger.LogMessage($"{userName}: Conversation saved with {chatSession.GetMessages().Count} messages");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error saving conversation: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Logger.LogError($"{userName}: Error saving conversation - {ex.Message}");
            }
        }

        private void ButtonPrint_Click(object sender, EventArgs e)
        {
            try
            {
                printService.PrintChat(chatSession.GetChatLog());
                Logger.LogMessage($"{userName}: Chat printed");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error printing conversation: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Logger.LogError($"{userName}: Error printing conversation - {ex.Message}");
            }
        }

        private void ButtonClear_Click(object sender, EventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to clear the chat?", "Confirm", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (result == DialogResult.Yes)
            {
                chatSession.Clear();
                richTextBoxChat.Clear();
                Logger.LogMessage($"{userName}: Chat cleared");
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            base.OnFormClosing(e);
            networkService.Stop();
            Logger.LogMessage($"{userName}: Application closed");
        }
    }
}