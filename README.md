# PDF Gathering Discord Bot

This is a Discord bot written in Python that gathers PDF files from all accessible text channels in a Discord server, logs command usage, tracks bot metrics, and outputs PDF metadata to a CSV file. The bot also includes features such as tracking high-confidence duplicate PDFs, unauthorized access handling, and interaction with Google Sheets for storage. Created with [Zero_sum](https://github.com/ZeroSums)
# Features

    Gather PDFs: The bot scans all text channels for PDF attachments and logs information such as the name, CDN link, author, and category into a CSV file.
    Duplicate Detection: High-confidence duplicate PDFs are detected and excluded based on file size.
    Admin Commands: Only administrators can use key commands, with unauthorized access attempts logged and reported.
    Bot Metrics: The bot tracks command usage, uptime, and total size of all PDFs gathered.
    Google Sheets Integration: After gathering PDFs, the data is uploaded to a linked Google Sheets document.
    CSV Output: A pdf_links.csv file is generated with details about all gathered PDFs.

## Commands
### General Commands

    !gather_pdfs
    Gathers all PDF files from accessible text channels in the server and writes metadata to a CSV file. Requires admin privileges.

    !metrics [number|all]
    Displays recent command usage along with the total size of all PDFs gathered. Requires admin privileges.

    !servers
    Displays a list of all servers the bot is currently in.

    !uptime
    Shows how long the bot has been running since it was started.

## Admin Testing Commands

    !test_admin [spoof]
    Tests whether the user has admin privileges. If spoof is passed, simulates a non-admin access attempt.

## Installation
### Prerequisites

    Python 3.7+
    A Discord Bot Token (Get it from the Discord Developer Portal)
    requests, discord.py, dotenv

## Setup

Clone the repository to your local machine.

    git clone https://github.com/tgcohce/PDF_Saver.git  
    cd PDF_Saver

### Install dependencies.

    pip install -r requirements.txt

    Create a .env file in the root directory and add your Discord bot token:

    BOT_TOKEN=your-discord-bot-token

Run the bot.

    python bot.py

## CSV Output

After running the !gather_pdfs command, a file named pdf_links.csv will be created in the bot’s root directory. This file will contain the following columns:

    ID: A unique identifier for each PDF.
    Name: The human-readable name of the PDF.
    CDN: The link to the PDF file.
    Category: The name of the channel from which the PDF was gathered.
    Date: The date and time the PDF was posted.
    Author: The Discord username of the user who posted the PDF.
    Size (bytes): The size of the PDF in bytes.
    Last Updated: The timestamp when the scraping was completed.

## Google Sheets Integration

The bot includes a Bash script (send_to_google.sh) that can upload the CSV data to a linked Google Sheet. The Google Sheet URL is displayed after the !gather_pdfs command completes.
## Admin Privileges

Key commands like !gather_pdfs and !metrics require the user to have admin privileges. Unauthorized access attempts will be logged and reported to a designated admin channel.
## Logging and Error Handling

    Logs: Detailed logs are provided for debugging, including metrics like command usage and duplicate detection.
    Error Handling: The bot will catch and log any errors that occur, notifying the admin channel if needed.

## License

This project is licensed under the MIT License.
