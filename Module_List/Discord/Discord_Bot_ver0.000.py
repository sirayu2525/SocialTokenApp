import discord
from discord.ext import commands

# Intents（必要な権限を有効化）
intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を取得するために必要

# BOTのプレフィックス（コマンドの呼び出し文字）を設定
bot = commands.Bot(command_prefix="/", intents=intents)

# BOTが起動したときの処理
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# メッセージを受け取ったときの処理
@bot.event
async def on_message(message):
    if message.author == bot.user:  # BOT自身のメッセージには反応しない
        return

    if message.content.lower() == "hello":
        await message.channel.send("こんにちは！")

    if message.content.lower() == "embed":
        embed = discord.Embed(title="埋め込みメッセージ",
                              description="これはサンプルの埋め込みメッセージです。",
                              color=discord.Color.blue())
        embed.add_field(name="フィールド1", value="これはフィールドの内容です", inline=False)
        embed.add_field(name="フィールド2", value="2つ目のフィールドです", inline=False)
        embed.set_footer(text="これはフッターです")
        await message.channel.send(embed=embed)

    await bot.process_commands(message)  # コマンドも処理するために必要

# コマンドの作成
@bot.command()
async def ping(ctx):
    """Pingを返すコマンド"""
    await ctx.send("Pong! 🏓")

@bot.command()
async def info(ctx):
    """EmbedでBOTの情報を送信"""
    embed = discord.Embed(title="BOTの情報",
                          description="このBOTはPythonで作成されました。",
                          color=discord.Color.green())
    embed.add_field(name="作成者", value="あなたの名前", inline=False)
    embed.set_footer(text="質問があればどうぞ！")
    await ctx.send(embed=embed)

# BOTを起動
TOKEN = "YOUR_BOT_TOKEN_HERE"  # ここにBOTのトークンを記入
bot.run(TOKEN)
