import re
from time import strptime, time
import discord
from discord.ext import commands


class Time(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.time_pattern = re.compile(r"\d{1,2}:\d{2}")

    @discord.app_commands.command()
    @discord.app_commands.describe(
        user_time="A relative time formatted as HH:MM, +HH:MM or -HH:MM."
    )
    async def time(self, interaction: discord.Interaction, user_time: str):
        re_match = self.time_pattern.search(user_time)

        if re_match is None:
            await interaction.response.send_message(
                "An invalid time was passed", ephemeral=True
            )
            return

        interval = strptime(user_time[re_match.start() :], "%H:%M")
        difference = interval.tm_hour * 3600 + interval.tm_hour * 60
        await interaction.response.send_message(
            f"<t:{int(time()) - difference if user_time[0] == '-' else int(time()) + difference}:R>"
        )


async def setup(makishima: commands.Bot):
    await makishima.add_cog(Time(makishima), guilds=makishima.guilds)
