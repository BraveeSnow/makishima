from typing import List
import discord
from discord.ext import commands
from api.anilist import AnilistEntry, AnilistGraphQLClient, ExternalLink


class ExternalLinkView(discord.ui.View):
    def __init__(self, external_links: List[ExternalLink]):
        super().__init__(timeout=None)

        for source in external_links:
            self.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.url, label=source.name, url=source.url
                )
            )


class AnilistResultSelection(discord.ui.Select):
    def __init__(self, results: List[AnilistEntry]):
        super().__init__(
            placeholder="Select a title...",
            options=[
                discord.SelectOption(
                    label=(
                        result.english if result.english is not None else result.romaji
                    ),
                    value=str(i),
                )
                for i, result in enumerate(results)
            ],
        )

        self.results = results

    async def callback(self, interaction: discord.Interaction):
        selected = self.results[int(self.values[0])]
        await interaction.response.edit_message(
            content=f'Selected "{selected.english if selected.english is not None else selected.romaji}"',
            view=None,
        )

        embed = discord.Embed(
            title=selected.english if selected.english is not None else selected.romaji,
            url=f"https://anilist.co/anime/{selected.id}",
            description=selected.description[:2000],
            colour=0x3577FF,
        )
        embed.set_author(name=selected.native)
        embed.set_thumbnail(url=selected.cover_image)

        embed.add_field(
            name="Genres",
            value=", ".join(selected.genres) if len(selected.genres) > 0 else "N/A",
            inline=False,
        )
        embed.add_field(
            name="Average Score",
            value=(
                f"{selected.score}%" if selected.score is not None else "Not yet rated"
            ),
        )
        embed.add_field(
            name="Episodes",
            value=(
                f"{selected.episodes} ({selected.format})"
                if selected.episodes is not None and selected.format is not None
                else "N/A"
            ),
        )
        embed.add_field(
            name="Season",
            value=(
                f"{selected.season} {selected.release}"
                if selected.season is not None and selected.release is not None
                else "N/A"
            ),
        )

        embed.set_image(url=selected.banner_image)
        embed.set_footer(text="Provided by AniList")

        await interaction.followup.send(
            embed=embed, view=ExternalLinkView(selected.external_links)
        )


class AnilistResultView(discord.ui.View):
    def __init__(self, results: List[AnilistEntry]):
        super().__init__(timeout=None)
        self.add_item(AnilistResultSelection(results))


class Anilist(commands.GroupCog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.anilist = AnilistGraphQLClient()

    @discord.app_commands.command()
    @discord.app_commands.describe(title="The title to query.")
    async def search(self, interaction: discord.Interaction, title: str):
        """
        Searches for the given title on AniList.
        """
        res = await self.anilist.search(title)
        await interaction.response.send_message(
            view=AnilistResultView(res), ephemeral=True
        )


async def setup(makishima: commands.Bot):
    await makishima.add_cog(Anilist(makishima), guilds=makishima.guilds)
