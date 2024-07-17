import os
import re
import sqlite3
from typing import List
import discord
from discord.app_commands import Choice, errors
from discord.ext import commands

BOOKS = {
    "Genesis": "GEN",
    "Exodus": "EXO",
    "Leviticus": "LEV",
    "Numbers": "NUM",
    "Deuteronomy": "DEU",
    "Joshua": "JOS",
    "Judges": "JDG",
    "Ruth": "RUT",
    "1 Samuel": "1SA",
    "2 Samuel": "2SA",
    "1 Kings": "1KI",
    "2 Kings": "2KI",
    "1 Chronicles": "1CH",
    "2 Chronicles": "2CH",
    "Ezra": "EZR",
    "Nehemiah": "NEH",
    "Esther": "EST",
    "Job": "JOB",
    "Psalms": "PSA",
    "Proverbs": "PRO",
    "Ecclesiastes": "ECC",
    "Song of Solomon": "SNG",
    "Isaiah": "ISA",
    "Jeremiah": "JER",
    "Lamentations": "LAM",
    "Ezekiel": "EZK",
    "Daniel": "DAN",
    "Hosea": "HOS",
    "Joel": "JOL",
    "Amos": "AMO",
    "Obadiah": "OBA",
    "Jonah": "JON",
    "Micah": "MIC",
    "Nahum": "NAM",
    "Habakkuk": "HAB",
    "Zephaniah": "ZEP",
    "Haggai": "HAG",
    "Zechariah": "ZEC",
    "Malachi": "MAL",
    "Matthew": "MAT",
    "Mark": "MRK",
    "Luke": "LUK",
    "John": "JHN",
    "Acts": "ACT",
    "Romans": "ROM",
    "1 Corinthians": "1CO",
    "2 Corinthians": "2CO",
    "Galatians": "GAL",
    "Ephesians": "EPH",
    "Philippians": "PHP",
    "Colossians": "COL",
    "1 Thessalonians": "1TH",
    "2 Thessalonians": "2TH",
    "1 Timothy": "1TI",
    "2 Timothy": "2TI",
    "Titus": "TIT",
    "Philemon": "PHM",
    "Hebrews": "HEB",
    "James": "JAS",
    "1 Peter": "1PE",
    "2 Peter": "2PE",
    "1 John": "1JN",
    "2 John": "2JN",
    "3 John": "3JN",
    "Jude": "JUD",
    "Revelation": "REV",
}


async def _book_autocomplete(_: discord.Interaction, content: str) -> List[Choice[str]]:
    return [
        Choice(name=k, value=k)
        for k in BOOKS.keys()
        if k.lower().startswith(content.lower())
    ][:25]


class Bible(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.db = sqlite3.connect(os.getenv("BIBLE_DB"))

    @discord.app_commands.command()
    @discord.app_commands.describe(book="The book to look into.")
    @discord.app_commands.describe(
        verse="The verse(s) to look up. Must be in the format of 1:1 for a single verse or 1:2-3 for multiple."
    )
    @discord.app_commands.autocomplete(book=_book_autocomplete)
    async def verse(self, interaction: discord.Interaction, book: str, verse: str):
        """
        Searches a verse or list of verses from one of the books of the bible.
        """
        if re.match(r"^\d+:(\d+-\d+|\d+)$", verse) is None:
            await interaction.response.send_message(
                "Verse selection is incorrectly formatted."
            )
            return

        finalized_text = []
        chapter_split = verse.split(":")
        verse_split = chapter_split[1].split("-")

        if len(verse_split) == 1:
            verse_split.append(verse_split[0])

        verses = self.db.execute(
            f"SELECT text FROM verse WHERE version_id = ? AND BOOK = ? AND chapter = ? AND start_verse >= ? AND start_verse <= ?",
            (
                "eng-kjv",
                BOOKS[book],
                int(chapter_split[0]),
                int(verse_split[0]),
                int(verse_split[1]),
            ),
        )

        for verse_num, text in zip(
            range(int(verse_split[0]), int(verse_split[1]) + 1), verses
        ):
            finalized_text.append(f"[{verse_num}] {text[0].removeprefix('¶').strip()}")

        try:
            await interaction.response.send_message(
                "> " + "\n> ".join(finalized_text) + f"\n*{book} {verse}*"
            )
        except errors.CommandInvokeError as err:
            await interaction.response.send_message("There appears to be too much text for me to send at once.")


async def setup(makishima: commands.Bot):
    if "BIBLE_DB" not in os.environ:
        print(
            'Environment variable "BIBLE_DB" is undefined. The bible command group will be disabled.'
        )
        return

    await makishima.add_cog(Bible(makishima), guilds=makishima.guilds)
