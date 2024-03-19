import re
from typing import Any, Dict, List
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

_ANILIST_TRANSPORT = AIOHTTPTransport(url="https://graphql.anilist.co/")

_ANILIST_SEARCH_QUERY = gql(
    """
    query ($title: String) {
        Page(perPage: 10) {
            media(search: $title, type: ANIME) {
                id
		        title {
                    english
			        romaji
			        native
		        }
                description
                season
                seasonYear
                episodes
                duration
                coverImage {
                    medium
                }
                bannerImage
                genres
                averageScore
	        }
	    }
    }
    """
)

_HTML_RE = re.compile(r"<[^>]+>")


class AnilistEntry:
    """
    Data class for an entry on AniList.
    """

    def __init__(self, media: Dict[str, Any]):
        self.id: str = media["id"]
        self.english: str | None = media["title"]["english"]
        self.native: str = media["title"]["native"]
        self.romaji: str = media["title"]["romaji"]
        self.description: str = _HTML_RE.sub("", media["description"])
        self.season: str | None = (
            media["season"].capitalize() if media["season"] is not None else None
        )
        self.release: int | None = (
            int(float(media["seasonYear"])) if media["seasonYear"] is not None else None
        )
        self.episodes: int | None = (
            int(float(media["episodes"])) if media["episodes"] is not None else None
        )
        self.duration: int | None = (
            int(float(media["duration"])) if media["duration"] is not None else None
        )
        self.cover_image: str = media["coverImage"]["medium"]
        self.banner_image: str = media["bannerImage"]
        self.genres: List[str] = media["genres"]
        self.score: int | None = (
            int(float(media["averageScore"]))
            if media["averageScore"] is not None
            else None
        )


def clean_anilist_entries(entries: Dict[str, Any]) -> List[AnilistEntry]:
    return [AnilistEntry(entry) for entry in entries["Page"]["media"]]


class AnilistGraphQLClient:
    """
    An asynchronous GraphQL client for AniList.
    """

    def __init__(self):
        self.client = Client(transport=_ANILIST_TRANSPORT)

    async def search(self, title: str) -> List[AnilistEntry]:
        entries = await self.client.execute_async(
            _ANILIST_SEARCH_QUERY, variable_values={"title": title}
        )
        return clean_anilist_entries(entries)
