"""Audiobookshelf API client for fetching podcasts and episodes."""
import requests
from typing import List, Dict, Optional

class AudiobookshelfClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_all_podcasts(self) -> List[Dict]:
        """Fetch all podcast libraries."""
        resp = requests.get(f"{self.base_url}/api/libraries", headers=self.headers)
        resp.raise_for_status()
        libraries = resp.json().get("libraries", [])
        podcasts = []
        for lib in libraries:
            if lib.get("mediaType") == "podcast":
                items = self._get_library_items(lib["id"])
                podcasts.extend(items)
        return podcasts

    def _get_library_items(self, library_id: str) -> List[Dict]:
        resp = requests.get(
            f"{self.base_url}/api/libraries/{library_id}/items",
            headers=self.headers
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    def get_podcast_episodes(self, podcast_id: str) -> List[Dict]:
        """Fetch all episodes for a given podcast."""
        resp = requests.get(
            f"{self.base_url}/api/items/{podcast_id}/episodes",
            headers=self.headers
        )
        resp.raise_for_status()
        return resp.json().get("episodes", [])

    def download_episode_audio(self, episode_id: str, dest_path: str):
        """Download the original audio file for an episode."""
        # First get the audio file URL
        resp = requests.get(
            f"{self.base_url}/api/episodes/{episode_id}",
            headers=self.headers
        )
        resp.raise_for_status()
        audio_url = resp.json().get("audioFile", {}).get("url")
        if not audio_url:
            raise ValueError("No audio file URL found")
        
        full_url = f"{self.base_url}{audio_url}"
        with requests.get(full_url, headers=self.headers, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
