import discord
import json
import rcon
import os
from discord_components import Button, ButtonStyle, InteractionType, DiscordComponents
from discord.ext import commands

with open("config.json", "r") as f:
    config = json.load(f)

prefix = config["prefix"]
bot = commands.Bot(command_prefix=prefix, help_command=None)

@bot.event
async def on_ready():
    DiscordComponents(bot)
    print("Logged in")

@bot.command()
async def panel(panel):
    if panel.author.guild_permissions.administrator:
        panel_embed = discord.Embed(title="行う操作を選んでください", description="ボタンでサーバーの操作を行うことができます")
        panel_embed.add_field(name="起動", value="サーバーを起動させます")
        panel_embed.add_field(name="停止", value="サーバーを停止させます")
        panel_embed.add_field(name="コンソール", value="コンソールコマンドを実行できます")
        await panel.send(
            embed=panel_embed,
            components = [
                Button(label="起動", style=ButtonStyle.green, custom_id="on"),
                Button(label="停止", style=ButtonStyle.red, custom_id="off"),
                Button(label="コンソール", style=ButtonStyle.blue, custom_id="console"),
            ],
        )
        button_interaction = await bot.wait_for("button_click", timeout=10)
        if button_interaction.component.custom_id == "on":
            filename = config["ps1"]
            os.system('powershell -Command' + ' ' +\
                f'powershell -ExecutionPolicy RemoteSigned .\\{filename}')
            await button_interaction.respond(
                type=InteractionType.ChannelMessageWithSource,
                content="サーバーの起動を行います。"
            )
        elif button_interaction.component.custom_id == "off":
            address = config["rcon"][0]["address"]
            port = config["rcon"][0]["port"]
            password = config["rcon"][0]["password"]
            with rcon.Client(f"{address}", int(port), passwd=f"{password}") as client:
                client.run("stop")
            await button_interaction.respond(
                type=InteractionType.ChannelMessageWithSource,
                content="サーバーの停止を行います。"
            )
        elif button_interaction.component.custom_id == "console":
            try:
                console_command = await bot.wait_for("message", timeout=30)
            except TimeoutError:
                await panel.send("30秒以内にコマンドが実行されなかったためキャンセルされました。")
            address = config["rcon"][0]["address"]
            port = config["rcon"][0]["port"]
            password = config["rcon"][0]["password"]
            with rcon.Client(f"{address}", int(port), passwd=f"{password}") as client:
                response = client.run(f"{console_command}")
            await button_interaction.respond(
                type=InteractionType.ChannelMessageWithSource,
                content=f"{response}"
            )
    else:
        return