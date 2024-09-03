"""
PDF Saver Module

This module contains functionality to gather PDF attachments from Discord
channels and save their details to a CSV file.
"""

import csv
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import time

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
    start_time = time.time()  # Start time for total script runtime
    pdf_count = 0  # Initialize PDF count

    try:
        scrape_start_time = time.time()  # Start time for scraping

        with open('pdf_links.csv', mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Name", "CDN", "Category", "Date"])

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
                                    message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                    # Timestamp of when the message was created
                                ])
                                pdf_count += 1  # Increment the PDF count

        scrape_end_time = time.time()  # End time for scraping
        scrape_duration = scrape_end_time - scrape_start_time  # Time taken to scrape

        # Calculate total script runtime
        total_runtime = time.time() - start_time

        # Prepare the log message
        log_message = (
            f"PDF scraping completed!\n"
            f"Total PDFs scraped: {pdf_count}\n"
            f"Time to scrape all channels: {scrape_duration:.2f} seconds\n"
            f"Total script runtime: {total_runtime:.2f} seconds"
        )

        channel_id = 1279251916550836335
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(log_message)
        else:
            print("Error: Channel not found")

    except FileNotFoundError as e:
        await ctx.send(f"File not found: {str(e)}")
        print(f"Error: {e}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"Error: {e}")


# Retrieve the bot token from an environment variable
bot_token = os.getenv('BOT_TOKEN')

if bot_token is None:
    raise ValueError("No BOT_TOKEN environment variable found.")

# Run the bot with the token from the environment variable
bot.run(bot_token)
