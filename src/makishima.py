#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

makishima = commands.Bot("./", intents=intents)


@makishima.event
async def on_ready():
    activity = discord.CustomActivity("Reading classical literature")
    makishima.change_presence(activity=activity, status=discord.Status.do_not_disturb)


makishima.run(os.environ["MAKISHIMA_TOKEN"])
