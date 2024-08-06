#!/usr/bin/env python3

import os
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class MakishimaClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__("./", intents=intents)

        self.db = (
            Session(create_engine(os.getenv("MAKISHIMA_DB")))
            if "MAKISHIMA_DB" in os.environ
            else None
        )


async def load_commands(command_path: os.PathLike):
    for entry in os.scandir(command_path):
        name: str = entry.name

        if entry.is_dir():
            await load_commands(Path(os.path.join(command_path, name)))
            continue

        if not name.endswith(".py"):
            continue

        # continue with command import
        print(f"Loading commands from {name}")
        await makishima.load_extension(
            f"commands.{Path(command_path).name.replace('/', '.')}.{name[:-3]}"
        )


async def on_ready():
    activity = discord.CustomActivity("Reading classical literature")
    await makishima.change_presence(
        activity=activity, status=discord.Status.do_not_disturb
    )

    # load commands
    await load_commands(Path("src/commands"))

    for guild in makishima.guilds:
        print(f"Synced commands in guild with ID {guild.id}")
        await makishima.tree.sync(guild=guild)

    print("Loading commands completed")


if __name__ == "__main__":
    load_dotenv()

    makishima = MakishimaClient()
    makishima.add_listener(on_ready)
    makishima.run(os.environ["MAKISHIMA_TOKEN"])
