# Chat Application

This project is a simple chat application that allows bidirectional communication between two instances. It features a user-friendly interface for sending and receiving messages, as well as options for saving and printing conversations.

## Project Structure

- **Forms**
  - `MainForm.cs`: Contains the main logic for the chat application, including UI initialization and message handling.
  - `MainForm.Designer.cs`: Auto-generated file that defines the layout and properties of the UI components.
  - `MainForm.resx`: Contains resources such as strings and images used in the UI.

- **Models**
  - `Message.cs`: Defines the `ChatMessage` class, representing a chat message with properties for the user's name, timestamp, and message text.
  - `ChatSession.cs`: Manages the conversation history, including methods for adding messages and retrieving the chat log.

- **Services**
  - `NetworkService.cs`: Handles TCP/IP communication between instances, including methods for sending and receiving messages.
  - `FileService.cs`: Responsible for saving and loading chat logs to and from a text file (`chat_log.txt`).
  - `PrintService.cs`: Implements printing functionality for the conversation using `PrintDocument` and displays a `PrintPreviewDialog`.

- **Utils**
  - `Logger.cs`: Provides logging functionality for error handling and debugging.

- **Properties**
  - `AssemblyInfo.cs`: Contains assembly-level attributes for version information and company details.
  - `Settings.Designer.cs`: Auto-generated file containing application settings.

- **Configuration**
  - `App.config`: Contains configuration settings for the application, such as connection strings.

- **Entry Point**
  - `Program.cs`: The entry point of the application that initializes and starts the main form.

## Features

- Bidirectional communication between two instances of the application.
- Save chat logs to a text file and load them for future reference.
- Print conversations directly from the application.
- User-friendly interface for easy interaction.

## Setup Instructions

1. Clone the repository or download the project files.
2. Open the project in your preferred C# development environment.
3. Build the project to restore dependencies.
4. Run the application and connect two instances to start chatting.

## Usage Guidelines

- Enter your name in the designated field before sending messages.
- Use the "Send" button to transmit your message.
- Access the "Save" option to store the conversation log.
- Use the "Print" option to print the current chat session.

Feel free to contribute to the project by adding features or improving existing functionality!