import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.typing = False

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Open or create the CSV file and set up the CSV writer
csv_file = open('pdf_links.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# Write the CSV header
csv_writer.writerow(["Name", "CDN", "Category", "Date"])

@bot.event
async def on_ready():
    """Event triggered when the bot has successfully connected."""
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready.')

@bot.command()
async def gather_pdfs(ctx):
    """
    Command to gather all PDF attachments from all text channels in the server
    and save their details (filename, URL, channel name, and message timestamp) to a CSV file.
    """
    try:
        # Iterate through each text channel in the guild (server)
        for channel in ctx.guild.text_channels:
            # Get the permissions of the bot in the current channel
            permissions = channel.permissions_for(ctx.guild.me)

            # Check if the bot has permissions to read messages and message history
            if permissions.read_messages and permissions.read_message_history:
                # Iterate through all messages in the channel
                async for message in channel.history(limit=None):
                    # Check each attachment in the message
                    for attachment in message.attachments:
                        # If the attachment is a PDF (ends with ".pdf")
                        if attachment.filename.lower().endswith(".pdf"):
                            # Write the details of the PDF to the CSV file
                            csv_writer.writerow([
                                attachment.filename,  # The filename of the PDF
                                attachment.url,  # The URL to the PDF
                                channel.name,  # The name of the channel where the PDF was found
                                message.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Timestamp of when the message was created
                            ])
            else:
                # Notify the user about the lack of permissions
                await ctx.send(
                    f"Bot does not have the necessary permissions to access messages or history in the channel '{channel.name}'.")
                print(f"Warning: Missing permissions in channel '{channel.name}'.")

        # Close the CSV file after writing all the PDF details
        csv_file.close()

        # Inform the user that the process is complete and the CSV file has been created
        await ctx.send("PDF links have been gathered and saved to pdf_links.csv.")

    except Exception as e:
        # Handle any exceptions that occur and send an error message to the user
        await ctx.send(f"An error occurred: {str(e)}")
        # Print the error details to the console for debugging
        print(f"Error: {e}")

# Retrieve the bot token from an environment variable
bot_token = os.getenv('BOT_TOKEN')

if bot_token is None:
    raise ValueError("No BOT_TOKEN environment variable found.")

# Run the bot with the token from the environment variable
bot.run(bot_token)
