#!/usr/bin/env python3
"""Osedax-Cast: Audiobookshelf to LXMF podcast bridge."""
import argparse
import time
import schedule
from pathlib import Path
import tomli

from audiobookshelf import AudiobookshelfClient
from converter import OpusConverter
from generator import MuGenerator

def load_config(config_path: str) -> dict:
    with open(config_path, "rb") as f:
        return tomli.load(f)

def poll_and_update(config: dict):
    """Main update cycle."""
    print("Polling Audiobookshelf...")
    client = AudiobookshelfClient(
        config["audiobookshelf"]["url"],
        config["audiobookshelf"]["api_key"]
    )
    converter = OpusConverter(
        config["content"]["library_path"],
        config["content"]["opus_bitrate"]
    )
    generator = MuGenerator(
        config["content"]["library_path"] + "/mu",
        config["content"]["page_size"]
    )

    podcasts = client.get_all_podcasts()
    print(f"Found {len(podcasts)} podcasts")
    
    for podcast in podcasts:
        episodes = client.get_podcast_episodes(podcast["id"])
        print(f"  {podcast['title']}: {len(episodes)} episodes")
        
        # Convert new episodes
        for ep in episodes:
            ep_id = ep["id"]
            audio_path = Path(config["content"]["library_path"]) / "original" / f"{ep_id}.mp3"
            if not audio_path.exists():
                # Download original if not cached
                client.download_episode_audio(ep_id, str(audio_path))
            converter.convert_to_opus(str(audio_path), ep_id)
        
        # Generate .mu pages
        generator.generate_podcast_pages(podcast, episodes)
    
    # Generate index page
    index_path = Path(config["content"]["library_path"]) / "mu" / "index.mu"
    index_content = generator.generate_index(podcasts)
    index_path.write_text(index_content)
    
    print("Update complete.")

def main():
    parser = argparse.ArgumentParser(description="Osedax-Cast")
    parser.add_argument("-c", "--config", default="config.toml", help="Config file path")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    config = load_config(args.config)
    
    if args.once:
        poll_and_update(config)
        return

    # Schedule hourly updates
    interval = config["audiobookshelf"].get("poll_interval_minutes", 60)
    schedule.every(interval).minutes.do(poll_and_update, config)
    poll_and_update(config)  # Initial run
    
    print(f"Scheduler started. Polling every {interval} minutes.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
