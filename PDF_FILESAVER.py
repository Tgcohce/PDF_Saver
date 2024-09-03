import discord
from discord.ext import commands
import csv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.typing = False

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize data storage
data = []


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready.')


@bot.command()
async def gather_pdfs(ctx):
    try:
        print("Command received. Starting to gather PDFs...")
        row_id = 1  # Start the ID counter

        for channel in ctx.guild.text_channels:
            print(f"Checking channel: {channel.name}")
            permissions = channel.permissions_for(ctx.guild.me)
            if permissions.read_messages and permissions.read_message_history:
                async for message in channel.history(limit=None):
                    for attachment in message.attachments:
                        if attachment.filename.endswith(".pdf"):
                            # Replace '-' and '_' with spaces in filename for readability
                            human_readable_name = attachment.filename.replace(
                                '-', ' ').replace('_', ' ')
                            data.append([
                                row_id,  # ID
                                human_readable_name,  # Name
                                attachment.url,  # CDN
                                channel.name,  # Category
                                message.created_at.strftime(
                                    '%Y-%m-%d %H:%M:%S'),  # Date
                                message.author.name  # Author
                            ])
                            row_id += 1

        # Sort data by Date
        data.sort(key=lambda x: x[4])

        # Write data to CSV
        with open('pdf_links.csv', mode='w', newline='',
                  encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the CSV header
            csv_writer.writerow(
                ["ID", "Name", "CDN", "Category", "Date", "Author"])
            # Write the data rows
            csv_writer.writerows(data)

        await ctx.send(
            "PDF links have been gathered, sorted, and saved to pdf_links.csv."
        )
        print("PDF gathering completed. CSV file saved.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"Error: {e}")


# Run the bot with your token
bot.run('')
