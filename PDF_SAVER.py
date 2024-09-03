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

# Open or create the CSV file and set up the CSV writer
csv_file = open('pdf_links.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# Write the CSV header
csv_writer.writerow(["Name", "CDN", "Category", "Date"])

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready.')

@bot.command()
async def gather_pdfs(ctx):
    try:
        for channel in ctx.guild.text_channels:
            permissions = channel.permissions_for(ctx.guild.me)
            if permissions.read_messages and permissions.read_message_history:
                async for message in channel.history(limit=None):
                    for attachment in message.attachments:
                        if attachment.filename.endswith(".pdf"):
                            csv_writer.writerow([
                                attachment.filename,
                                attachment.url,
                                channel.name,
                                message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            ])
        csv_file.close()
        await ctx.send("PDF links have been gathered and saved to pdf_links.csv.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"Error: {e}")

# Run the bot with your token
bot.run()
