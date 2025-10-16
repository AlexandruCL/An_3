using System;
using System.Drawing;
using System.Drawing.Printing;
using System.Windows.Forms;

namespace ChatApplication.Services
{
    public class PrintService
    {
        private string? _textToPrint;

        public void PrintChat(string chatLog)
        {
            _textToPrint = chatLog;

            PrintDocument printDocument = new PrintDocument();
            printDocument.PrintPage += PrintDocument_PrintPage;

            PrintPreviewDialog previewDialog = new PrintPreviewDialog
            {
                Document = printDocument,
                Width = 800,
                Height = 600
            };

            if (previewDialog.ShowDialog() == DialogResult.OK)
            {
                printDocument.Print();
            }
        }

        private void PrintDocument_PrintPage(object sender, PrintPageEventArgs e)
        {
            if (e.Graphics != null && _textToPrint != null)
            {
                Font printFont = new Font("Arial", 10);
                float yPos = 0;
                int count = 0;
                float leftMargin = e.MarginBounds.Left;
                float topMargin = e.MarginBounds.Top;
                string[] lines = _textToPrint.Split('\n');

                foreach (string line in lines)
                {
                    yPos = topMargin + (count * printFont.GetHeight(e.Graphics));
                    e.Graphics.DrawString(line, printFont, Brushes.Black, leftMargin, yPos, new StringFormat());
                    count++;
                }
            }
        }
    }
}