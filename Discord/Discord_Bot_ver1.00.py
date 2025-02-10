import discord
from discord import app_commands
import os

TOKEN = os.getenv("Discord_Bot_TOKEN")

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)



@tree.command(name="ゲーム開始設定",description="スライドパズルゲームの開始時刻と終了時刻を設定します")
@app_commands.choices(genre=[
    discord.app_commands.Choice(name="地理", value="地理"),
    discord.app_commands.Choice(name="スポーツ", value="スポーツ"),
    discord.app_commands.Choice(name="理科", value="理科")
    ])
@app_commands.choices(difficulty=[
    discord.app_commands.Choice(name="めちゃむずレベル", value="専門家"),
    discord.app_commands.Choice(name="高校生レベル", value="高校生"),
    discord.app_commands.Choice(name="小学生レベル", value="小学生")
    ])
async def test_command(interaction: discord.Interaction,
                        start_min: int,
                        term_min: int,
                        genre: str,
                        difficulty: str):#デフォルト値を指定
    
    await interaction.response.send_message('ルーム作成を開始します',ephemeral=True)

    mes = '''まもなくゲームが開始されます。\n参加をご希望される皆さんはお急ぎください。'''
    embed = discord.Embed(title = '=== ゲーム開始 ' + str(start_min) + ' 分前 ===', color = 0x00ff00, description = mes)
    mes = '''aaa'''
    embed.add_field(name = 'ゲーム開始時刻',value = mes,inline=False)
    
    embed.set_footer(text="ゲーム開始予告")
    
    await interaction.channel.send(embed = embed)


@tree.command(name="稼働終了",description="Botを停止させる。管理者権限必須")
@app_commands.default_permissions(administrator=True)
async def test_command(interaction:discord.Interaction):
    await interaction.response.send_message("Botを停止します。",ephemeral=True)
    await client.close()




@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await tree.sync()

    print('起動')

    
    


client.run(TOKEN)