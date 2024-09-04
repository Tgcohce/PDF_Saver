import csv
import os
import time
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from io import BytesIO

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Set up logging for verbose debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize global variables
command_usage = []
bot_start_time = time.time()
data = []
seen_files = set()
pdf_sizes_by_name = {}
total_size = 0
pdf_count = 0
high_confidence_duplicates_detected = 0
high_confidence_duplicates_removed = 0
unauthorized_channel_id = 1279251916550836335
# Helper function to convert bytes to a human-readable format
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 bytes"
    elif size_bytes < 1_048_576:
        return f"{size_bytes / 1_024:.2f} KB"
    elif size_bytes < 1_073_741_824:
        return f"{size_bytes / 1_048_576:.2f} MB"
    else:
        return f"{size_bytes / 1_073_741_824:.2f} GB"
def is_admin(ctx):
    """Check if the user has admin permissions."""
    return ctx.author.guild_permissions.administrator
    
# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.typing = False
bot = commands.Bot(command_prefix="!", intents=intents)

# Utility function to log and send errors
async def handle_error(ctx, error_message):
    await ctx.send(error_message)
    logging.error(error_message)

# Command to track command usage
@bot.event
async def on_command(ctx):
    # Track command usage with user, command, and timestamp
    command_usage.append((ctx.author.name, ctx.command.name, datetime.now()))


# Command to display bot metrics
@bot.command()
async def metrics(ctx, arg: str = '5'):
    # Check if the user has admin permissions
    if not is_admin(ctx):
        logging.warning(f"Unauthorized access attempt by {ctx.author.name} in server {ctx.guild.name}")
        message = f"Unauthorized access attempt by {ctx.author.mention} in server {ctx.guild.name}. Command: !metrics {arg}"
        # Send a notification to the admin channel
        unauthorized_channel = bot.get_channel(unauthorized_channel_id)
        if unauthorized_channel:
            await unauthorized_channel.send(message)
        else:
            logging.error("Error: Unauthorized channel not found.")
        await ctx.send("You do not have permission to use this command.")
        return

    try:
        if arg.lower() == 'all':
            # Show all commands if 'all' is passed
            recent_commands = command_usage
        else:
            # Otherwise, handle the number argument
            num = int(arg)
            if num <= 0:
                await ctx.send("Please provide a positive integer or 'all'.")
                return
            recent_commands = command_usage[-num:]

        # Format recent commands
        recent_commands_message = "\n".join([f"{user[0]} used '{user[1]}' at {user[2].strftime('%Y-%m-%d %H:%M:%S')}" for user in recent_commands])

        # Get total size of all PDFs gathered
        total_size_str = convert_size(total_size)

        response = (
            "```md\n"
            "### Bot Metrics\n\n"
            "**Recent Commands Used:**\n"
            f"{recent_commands_message}\n\n"
            f"**Total Size of All PDFs Gathered:** {total_size_str}\n"
            "```"
        )

        await ctx.send(response)

    except ValueError:
        await ctx.send("Invalid argument. Please provide a positive integer or 'all'.")


# Command to display bot servers
@bot.command()
async def servers(ctx):
    guilds = bot.guilds
    server_info = "\n".join([f"**{guild.name}** (ID: {guild.id})" for guild in guilds])
    response = (
        "```md\n"
        f"### Bot Servers\n\n"
        f"**Total Servers:** {len(guilds)}\n\n"
        f"{server_info}\n"
        "```"
    )
    await ctx.send(response)

# Command to display bot uptime
@bot.command()
async def uptime(ctx):
    uptime_seconds = time.time() - bot_start_time
    uptime_duration = str(timedelta(seconds=int(uptime_seconds)))
    response = (
        "```md\n"
        f"### Bot Uptime\n\n"
        f"**Uptime:** {uptime_duration}\n"
        "```"
    )
    await ctx.send(response)
@bot.command()
async def test_admin(ctx, *, arg=None):
    """Test if the current user is an admin or simulate an unauthorized access."""
    if arg == 'spoof':
        # Simulate a non-admin user trying to run a command
        user_is_admin = False
    else:
        # Check if the user has admin permissions
        user_is_admin = is_admin(ctx)

    if user_is_admin:
        response = "You are an admin."
    else:
        response = "You are not an admin."

        if arg == 'spoof':
            # Log unauthorized access attempt
            logging.warning(f"Non-admin user {ctx.author.name} (ID: {ctx.author.id}) attempted to run an admin-only command in server {ctx.guild.name}.")
            message = f"Debug Alert: Non-admin user {ctx.author.mention} tried to execute an admin-only command in server {ctx.guild.name}."

            # Send notification to the admin channel
            admin_channel_id = unauthorized_channel_id
            admin_channel = bot.get_channel(admin_channel_id)
            if admin_channel:
                await admin_channel.send(message)
            else:
                logging.error("Error: Admin notification channel not found.")

    await ctx.send(response)
    
# Main command to gather PDFs from all text channels
@bot.command()
async def gather_pdfs(ctx):
    # Check if the user has admin permissions
    if not is_admin(ctx):
        logging.warning(f"Unauthorized access attempt by {ctx.author.name} in server {ctx.guild.name}")
        message = f"Unauthorized access attempt by {ctx.author.mention} in server {ctx.guild.name}. Command: !gather_pdfs"
        # Send a notification to the admin channel
        unauthorized_channel = bot.get_channel(unauthorized_channel_id)
        if unauthorized_channel:
            await unauthorized_channel.send(message)
        else:
            logging.error("Error: Unauthorized channel not found.")
        await ctx.send("You do not have permission to use this command.")
        return

    await ctx.send("Gathering PDFs! Please wait...")
    global total_size, pdf_count, high_confidence_duplicates_detected, high_confidence_duplicates_removed
    start_time = time.time()

    try:
        scrape_start_time = time.time()
        row_id = 1
        current_time = datetime.now().strftime('%d-%m-%Y %H:%M')
        for channel in ctx.guild.text_channels:
            if channel.permissions_for(ctx.guild.me).read_messages and channel.permissions_for(ctx.guild.me).read_message_history:
                async for message in channel.history(limit=None):
                    for attachment in message.attachments:
                        if attachment.filename.endswith(".pdf"):
                            human_readable_name = attachment.filename.replace('-', ' ').replace('_', ' ')
                            file_identifier = (human_readable_name, attachment.url)
                            if file_identifier in seen_files:
                                logging.debug(f"Duplicate found: {human_readable_name} in channel: {channel.name}")
                                continue
                            seen_files.add(file_identifier)

                            try:
                                response = requests.get(attachment.url)
                                response.raise_for_status()
                                pdf_size = len(response.content)
                                pdf_size_bytes = len(response.content)
                                pdf_size_mb = pdf_size_bytes / 1_048_576
                                is_duplicate = False
                                if human_readable_name in pdf_sizes_by_name:
                                    for size in pdf_sizes_by_name[human_readable_name]:
                                        if abs(size - pdf_size) <= 100:
                                            is_duplicate = True
                                            high_confidence_duplicates_detected += 1
                                            break
                                if not is_duplicate:
                                    if human_readable_name not in pdf_sizes_by_name:
                                        pdf_sizes_by_name[human_readable_name] = []
                                    pdf_sizes_by_name[human_readable_name].append(pdf_size)
                                    total_size += pdf_size
                                    data.append([
                                        row_id,
                                        human_readable_name,
                                        attachment.url,
                                        channel.name.title(),
                                        message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                                        message.author.name.title(),
                                        pdf_size_mb,
                                        current_time
                                    ])
                                    row_id += 1
                                    pdf_count += 1
                                    logging.debug(f"Found PDF: {human_readable_name} in channel: {channel.name}")
                                else:
                                    high_confidence_duplicates_removed += 1
                                    logging.debug(f"Duplicate PDF skipped: {human_readable_name} with size {pdf_size} bytes")
                            except Exception as e:
                                await handle_error(ctx, f"Error downloading PDF '{human_readable_name}': {e}")
            else:
                logging.warning(f"Missing permissions in channel '{channel.name}'")
                await ctx.send(f"Warning: Missing permissions in channel '{channel.name}'")

        data.sort(key=lambda x: x[4])
        with open('pdf_links.csv', mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["ID", 
                                 "Name", 
                                 "CDN", 
                                 "Category", 
                                 "Date", 
                                 "Author", 
                                 "Size (bytes)",
                                 "Last Updated"])
            csv_writer.writerows(data)
            logging.info("CSV file 'pdf_links.csv' has been written.")

        average_size = total_size / pdf_count if pdf_count > 0 else 0
        total_size_str = convert_size(total_size)
        average_size_str = convert_size(average_size)

        try:
            script_path = './send_to_google.sh'
            logging.debug(f"Running Bash script: {script_path}")
            result = subprocess.run(['bash', script_path], capture_output=True, text=True)
            logging.info(f"Bash script output: {result.stdout}")
            if result.stderr:
                logging.error(f"Bash script error output: {result.stderr}")
        except Exception as e:
            await handle_error(ctx, f"An error occurred while running the Bash script: {str(e)}")

        scrape_end_time = time.time()
        scrape_duration = scrape_end_time - scrape_start_time
        total_runtime = time.time() - start_time

        log_message = (
            "```md\n"
            "### PDF Scraping Report\n\n"
            "**PDF Scraping Completed!**\n\n"
            f"**Total PDFs Scraped:** {pdf_count}\n"
            f"**Total Size of All PDFs:** {total_size_str}\n"
            f"**Average Size per PDF:** {average_size_str}\n"
            "\n"
            f"**High Confidence Duplicates:**\n"
            f"  - Detected: {high_confidence_duplicates_detected}\n"
            f"  - Removed: {high_confidence_duplicates_removed}\n"
            "\n"
            f"**Total Unique PDFs Added:** {pdf_count - high_confidence_duplicates_removed}\n"
            "\n"
            f"**Time to Scrape All Channels:** {scrape_duration:.2f} seconds\n"
            f"**Total Script Runtime:** {total_runtime:.2f} seconds\n"
            f"**Average Runtime per PDF:** {(total_runtime / pdf_count if pdf_count > 0 else 0):.2f} seconds\n"
            "\n"
            "**Google Sheets URL:**\n"
            "GOOGLE SHEET URL"
            "```"
        )

        logging.info(log_message)
        channel_id = 1279251916550836335
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(log_message)
        else:
            logging.error("Error: Channel not found")

    except FileNotFoundError as e:
        await handle_error(ctx, f"File not found: {str(e)}")
    except Exception as e:
        await handle_error(ctx, f"An error occurred: {str(e)}")

# Retrieve the bot token from an environment variable
bot_token = os.getenv('BOT_TOKEN')
if bot_token is None:
    logging.critical("No BOT_TOKEN environment variable found.")
    raise ValueError("No BOT_TOKEN environment variable found.")

# Run the bot with the token from the environment variable
bot.run(bot_token)
