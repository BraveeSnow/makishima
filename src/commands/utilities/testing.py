import discord
from discord.ext import commands


class Testing(commands.Cog):
    """
    Tools for testing Makishima during development.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """
        Tests if Makishima properly replies.
        """
        try:
            await interaction.response.send_message("Pong!")
        except discord.HTTPException as err:
            print(err)


async def setup(makishima: commands.Bot):
    await makishima.add_cog(Testing(makishima), guilds=makishima.guilds)
