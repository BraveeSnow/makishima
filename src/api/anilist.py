import re
from typing import Any, Dict, List
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

_ANILIST_GQL_URL = "https://graphql.anilist.co/"
_ANILIST_TRANSPORT = AIOHTTPTransport(url=_ANILIST_GQL_URL)

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
                format
                description
                season
                seasonYear
                episodes
                coverImage {
                    extraLarge
                }
                bannerImage
                genres
                averageScore
                externalLinks {
				    url
					site
				}
	        }
	    }
    }
    """
)

_ANILIST_MEDIA_LIST_QUERY = gql(
    """
    query ($id: Int) {
        Media (id: $id, onList: true) {
            id
        }
    }
    """
)

_ANILIST_ANIME_LIKE_MUTATION = gql(
    """
    mutation ($id: Int) {
        ToggleFavourite (animeId: $id) {
            anime {
                nodes {
                    id
                }
            }
        }
    }
    """
)

_ANILIST_WATCH_LATER_MUTATION = gql(
    """
    mutation ($id: Int) {
        SaveMediaListEntry (mediaId: $id, status: PLANNING) {
            id
        }
    }
    """
)

_HTML_RE = re.compile(r"<[^>]+>")


class ExternalLink:
    def __init__(self, external_link: Dict[str, Any]):
        self.url: str | None = external_link["url"]
        self.name: str = external_link["site"]


class AnilistEntry:
    """
    Data class for an entry on AniList.
    """

    def __init__(self, media: Dict[str, Any]):
        self.id: str = media["id"]
        self.english: str | None = media["title"]["english"]
        self.native: str = media["title"]["native"]
        self.romaji: str = media["title"]["romaji"]
        self.format: str = media["format"].replace("_", " ")
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
        self.cover_image: str = media["coverImage"]["extraLarge"]
        self.banner_image: str = media["bannerImage"]
        self.genres: List[str] = media["genres"]
        self.score: int | None = (
            int(float(media["averageScore"]))
            if media["averageScore"] is not None
            else None
        )
        self.external_links: List[ExternalLink] = [
            ExternalLink(l) for l in media["externalLinks"]
        ]


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

    async def is_in_list(self, anime_id: int, anilist_token: str) -> bool:
        try:
            await self._build_auth_client(anilist_token).execute_async(_ANILIST_MEDIA_LIST_QUERY, {"id": anime_id})
            return True
        except TransportQueryError:
            # this is expected behavior when no entry is found
            return False

    async def favorite(self, anime_id: int, anilist_token: str) -> bool:
        auth_client = self._build_auth_client(anilist_token)
        favorites = [
            d["id"]
            for d in (
                await auth_client.execute_async(
                    _ANILIST_ANIME_LIKE_MUTATION, variable_values={"id": anime_id}
                )
            )["ToggleFavourite"]["anime"]["nodes"]
        ]
        return anime_id in favorites

    async def add_to_watch_later(self, anime_id: int, anilist_token: str):
        auth_client = self._build_auth_client(anilist_token)
        await auth_client.execute_async(_ANILIST_WATCH_LATER_MUTATION, {"id": anime_id})

    def _build_auth_client(self, auth_token: str) -> Client:
        return Client(
            transport=AIOHTTPTransport(
                _ANILIST_GQL_URL, {"Authorization": f"Bearer {auth_token}"}
            )
        )
