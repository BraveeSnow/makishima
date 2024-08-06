from typing import List
import discord
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.orm import Session
from makishima import MakishimaClient
from api.anilist import AnilistEntry, AnilistGraphQLClient
from models import AnilistUser


class AnlistResultActions(discord.ui.View):
    def __init__(
        self, entry: AnilistEntry, database: Session, gql_client: AnilistGraphQLClient
    ):
        super().__init__(timeout=None)

        self.entry = entry
        self.db = database
        self.gql_client = gql_client

        like_btn = discord.ui.Button(
            style=discord.ButtonStyle.red, label="Like", emoji="🖤"
        )
        watch_later_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="Watch Later", emoji="⌚"
        )

        like_btn.callback = self._like_callback
        watch_later_btn.callback = self._watch_later_callback

        self.add_item(like_btn)
        self.add_item(watch_later_btn)

    async def _like_callback(self, interaction: discord.Interaction):
        result: AnilistUser | None = self.db.scalar(
            select(AnilistUser).where(AnilistUser.user_id == str(interaction.user.id))
        )

        if result is None:
            await self._send_login_message(interaction)
            return

        added = await self.gql_client.favorite(self.entry.id, result.access_token)
        await interaction.response.send_message(
            f"I've {'added \"' + self.entry.english + '\" to' if added else 'removed \"' + self.entry.english + '\" from'} your favorites list accordingly.",
            ephemeral=True,
        )

    async def _watch_later_callback(self, interaction: discord.Interaction):
        result: AnilistUser | None = self.db.scalar(
            select(AnilistUser).where(AnilistUser.user_id == str(interaction.user.id))
        )

        if result is None:
            await self._send_login_message(interaction)
            return

        if await self.gql_client.is_in_list(self.entry.id, result.access_token):
            await interaction.response.send_message(
                "This anime is already included in your list.", ephemeral=True
            )
            return

        await self.gql_client.add_to_watch_later(self.entry.id, result.access_token)
        await interaction.response.send_message(
            f'I\'ve added "{self.entry.english}" to your watch later list.',
            ephemeral=True,
        )

    async def _send_login_message(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "You haven't connected your AniList account yet! "
            + "Head over to [our website](https://makishima.snows.world), "
            + "log in with your Discord account and connect your AniList account."
        )


class AnilistResultView(discord.ui.View):
    def __init__(
        self,
        makishima: MakishimaClient,
        gql_client: AnilistGraphQLClient,
        results: List[AnilistEntry],
    ):
        super().__init__(timeout=None)
        self.makishima = makishima
        self.gql_client = gql_client
        self.results = results

        self.selection = discord.ui.Select(
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

        self.selection.callback = self._selection_callback
        self.add_item(self.selection)

    async def _selection_callback(self, interaction: discord.Interaction):
        selected = self.results[int(self.selection.values[0])]
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
            embed=embed,
            view=(
                AnlistResultActions(selected, self.makishima.db, self.gql_client)
                if self.makishima.db is not None
                else discord.utils.MISSING
            ),
        )


class Anilist(commands.GroupCog):
    def __init__(self, client: MakishimaClient):
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
            view=AnilistResultView(self.client, self.anilist, res), ephemeral=True
        )


async def setup(makishima: MakishimaClient):
    if makishima.db is None:
        print(
            "No connection to the database is present. Some functionality is disabled."
        )

    await makishima.add_cog(Anilist(makishima), guilds=makishima.guilds)
