#!/usr/bin/env python3

import os
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

makishima = commands.Bot("./", intents=intents)


async def load_commands(command_path: os.PathLike):
    for entry in os.scandir(command_path):
        name: str = entry.name

        if entry.is_dir():
            await load_commands(os.path.join(command_path, name))
            continue

        if not name.endswith(".py"):
            continue

        # continue with command import
        print(f"Loading commands from {name}")
        await makishima.load_extension(f"commands.{Path(command_path).name.replace("/", ".")}.{name[:-3]}")

@makishima.event
async def on_ready():
    activity = discord.CustomActivity("Reading classical literature")
    await makishima.change_presence(activity=activity, status=discord.Status.do_not_disturb)

    # load commands
    await load_commands("src/commands")

    for guild in makishima.guilds:
        print(f"Synced commands in guild with ID {guild.id}")
        await makishima.tree.sync(guild=guild)

    print("Loading commands completed")


if __name__ == "__main__":
    load_dotenv()
    makishima.run(os.environ["MAKISHIMA_TOKEN"])
