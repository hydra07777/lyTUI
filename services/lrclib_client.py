import httpx

LRCLIB_SEARCH_URL = "https://lrclib.net/api/search"


async def search(track_name: str, artist_name: str | None = None) -> list[dict]:
    params = {"track_name": track_name}
    if artist_name:
        params["artist_name"] = artist_name

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(LRCLIB_SEARCH_URL, params=params)
        response.raise_for_status()
        return response.json()
