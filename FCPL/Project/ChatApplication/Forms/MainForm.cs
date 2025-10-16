using System;
using System.Drawing;
using System.Net;
using System.Net.Sockets;
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
            
            // Ask user for their username
            string? inputUsername = null;
            while (string.IsNullOrWhiteSpace(inputUsername))
            {
                inputUsername = Microsoft.VisualBasic.Interaction.InputBox(
                    "Enter your username (max 20 characters):", 
                    "Username", 
                    "User");
                
                if (string.IsNullOrWhiteSpace(inputUsername))
                {
                    var retry = MessageBox.Show("Username cannot be empty. Try again?", 
                        "Error", MessageBoxButtons.YesNo, MessageBoxIcon.Warning);
                    if (retry == DialogResult.No)
                    {
                        Application.Exit();
                        return;
                    }
                }
                else if (inputUsername.Length > 20)
                {
                    MessageBox.Show("Username too long. Maximum 20 characters.", 
                        "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    inputUsername = null;
                }
            }

            userName = inputUsername;
            textBoxUsername.Text = userName;
            this.Text = $"Chat Application - {userName}";

            // Ask for port number (5000-5004 for up to 5 users)
            int userPort = 5000;
            bool portSelected = false;
            
            while (!portSelected)
            {
                var portDialog = new Form()
                {
                    Text = "Select Port",
                    Width = 300,
                    Height = 200,
                    StartPosition = FormStartPosition.CenterScreen,
                    FormBorderStyle = FormBorderStyle.FixedDialog,
                    MaximizeBox = false,
                    MinimizeBox = false
                };
                
                var label = new Label() { Text = "Select your port (5000-5004):", Left = 20, Top = 20, Width = 250 };
                var comboBox = new ComboBox() { Left = 20, Top = 50, Width = 240, DropDownStyle = ComboBoxStyle.DropDownList };
                comboBox.Items.AddRange(new object[] { "5000", "5001", "5002", "5003", "5004" });
                comboBox.SelectedIndex = 0;
                
                var okButton = new Button() { Text = "OK", Left = 100, Top = 100, Width = 75, DialogResult = DialogResult.OK };
                var cancelButton = new Button() { Text = "Cancel", Left = 180, Top = 100, Width = 75, DialogResult = DialogResult.Cancel };
                
                portDialog.Controls.Add(label);
                portDialog.Controls.Add(comboBox);
                portDialog.Controls.Add(okButton);
                portDialog.Controls.Add(cancelButton);
                portDialog.AcceptButton = okButton;
                portDialog.CancelButton = cancelButton;
                
                if (portDialog.ShowDialog() == DialogResult.OK)
                {
                    userPort = int.Parse(comboBox.SelectedItem.ToString());
                    
                    // Check if port is available
                    if (IsPortInUse(userPort))
                    {
                        var retry = MessageBox.Show(
                            $"Port {userPort} is already in use by another user.\n\nPlease select a different port.", 
                            "Port In Use", 
                            MessageBoxButtons.RetryCancel, 
                            MessageBoxIcon.Warning);
                        
                        if (retry == DialogResult.Cancel)
                        {
                            Application.Exit();
                            return;
                        }
                    }
                    else
                    {
                        portSelected = true;
                    }
                }
                else
                {
                    Application.Exit();
                    return;
                }
            }

            try
            {
                networkService = new NetworkService(userPort);
                Logger.LogMessage($"{userName} instance started on port {userPort}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to start network service: {ex.Message}", 
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Logger.LogError($"Failed to start network service on port {userPort}: {ex.Message}");
                Application.Exit();
                return;
            }

            chatSession = new ChatSession();
            fileService = new FileService(userName);
            printService = new PrintService();

            networkService.MessageReceived += OnMessageReceived;
            LoadChatHistory();
        }

        private bool IsPortInUse(int port)
        {
            try
            {
                TcpListener listener = new TcpListener(IPAddress.Loopback, port);
                listener.Start();
                listener.Stop();
                return false;
            }
            catch (SocketException)
            {
                return true;
            }
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
                networkService.BroadcastMessage(message);
                DisplayMessage(message);
                Logger.LogMessage($"[{textBoxUsername.Text}] SENT: {textBoxMessage.Text}");
                textBoxMessage.Clear();
                textBoxMessage.Focus();
            }
            else
            {
                MessageBox.Show("Please enter a message.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
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