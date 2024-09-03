# PDF_Saver

## PDF_Saver is a Discord bot that gathers PDF attachments from text channels and saves their details to a CSV file. Follow the instructions below to set up and run the bot.

### Prerequisites

    Python 3.8 or higher


#### Install Dependencies:

```bash
pip install -r requirements.txt
```

### Run Helper Script

To set up your bot token, follow these steps to run the helper script:

#### Make the Script Executable:

Ensure that the token_reader.sh script is executable. You can do this by running the following command:

```bash
chmod +x token_reader.sh
```

Run the Script:

After making the script executable, run it with the following command:

```bash
./token_reader.sh
```
The script will prompt you to enter your bot token, handle the creation of the .env file if necessary, and update the .env file with your provided token.


Last Updated: 2024-09-03