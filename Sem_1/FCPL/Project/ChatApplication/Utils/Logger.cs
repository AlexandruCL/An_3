using System;
using System.IO;

namespace ChatApplication.Utils
{
    public static class Logger
    {
        private static readonly string logFilePath = Path.Combine(
            Directory.GetCurrentDirectory(),
            "chat_application_log.txt"
        );

        static Logger()
        {
            // Normalize the path
            string normalizedPath = Path.GetFullPath(logFilePath);
            
            // Create directory if it doesn't exist
            string? directory = Path.GetDirectoryName(normalizedPath);
            if (directory != null && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }

        public static void LogMessage(string message)
        {
            try
            {
                string normalizedPath = Path.GetFullPath(logFilePath);
                using (StreamWriter writer = new StreamWriter(normalizedPath, true))
                {
                    writer.WriteLine($"{DateTime.Now}: {message}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error logging message: {ex.Message}");
            }
        }

        public static void LogError(string errorMessage)
        {
            try
            {
                string normalizedPath = Path.GetFullPath(logFilePath);
                using (StreamWriter writer = new StreamWriter(normalizedPath, true))
                {
                    writer.WriteLine($"{DateTime.Now} [ERROR]: {errorMessage}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error logging error: {ex.Message}");
            }
        }

        public static string GetLogFilePath()
        {
            return Path.GetFullPath(logFilePath);
        }
    }
}