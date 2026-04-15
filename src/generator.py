"""Generate .mu pages for podcast listings and episode lists."""
from typing import List, Dict
from pathlib import Path
import math

class MuGenerator:
    def __init__(self, output_dir: str, page_size: int = 50):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page_size = page_size

    def generate_index(self, podcasts: List[Dict]) -> str:
        """Generate the main landing page with all podcasts."""
        lines = [
            "# Osedax-Cast Podcast Library",
            "",
            "## Available Podcasts",
            ""
        ]
        for pod in podcasts:
            title = pod.get("title", "Untitled")
            author = pod.get("author", "Unknown")
            description = pod.get("description", "")[:200]
            pod_id = pod.get("id")
            lines.append(f"### [{title}](/podcast/{pod_id}.mu)")
            lines.append(f"**Author:** {author}")
            lines.append(f"*{description}*")
            lines.append("")
        
        # Search box (NomadNet can handle form input, we'll just provide the endpoint)
        lines.extend([
            "---",
            "## Search",
            "`/search?q=query`",
            ""
        ])
        return "\n".join(lines)

    def generate_podcast_pages(self, podcast: Dict, episodes: List[Dict]) -> List[Path]:
        """Generate paginated episode listing for a single podcast."""
        podcast_id = podcast["id"]
        title = podcast.get("title", "Untitled")
        author = podcast.get("author", "Unknown")
        description = podcast.get("description", "")
        
        total_pages = math.ceil(len(episodes) / self.page_size)
        files_written = []
        
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * self.page_size
            end_idx = start_idx + self.page_size
            page_episodes = episodes[start_idx:end_idx]
            
            lines = [
                f"# {title}",
                f"**Author:** {author}",
                f"*{description}*",
                "",
                f"## Episodes (Page {page_num} of {total_pages})",
                ""
            ]
            
            for ep in page_episodes:
                ep_title = ep.get("title", "Untitled Episode")
                published = ep.get("publishedAt", "Unknown date")
                duration = self._format_duration(ep.get("duration", 0))
                ep_id = ep.get("id")
                # Link will trigger LXMF download request
                lines.append(f"### {ep_title}")
                lines.append(f"**Published:** {published} | **Duration:** {duration}")
                lines.append(f"[Download Opus](/download/{ep_id})")
                lines.append("")
            
            # Navigation
            nav = []
            if page_num > 1:
                nav.append(f"[Prev](/podcast/{podcast_id}_{page_num-1}.mu)")
            if page_num < total_pages:
                nav.append(f"[Next](/podcast/{podcast_id}_{page_num+1}.mu)")
            nav.append(f"[Podcast Home](/podcast/{podcast_id}.mu)")
            lines.append(" | ".join(nav))
            
            # Jump input
            lines.extend([
                "",
                "---",
                f"Jump to page: `/podcast/{podcast_id}_[page].mu`",
                f"Total episodes: {len(episodes)}"
            ])
            
            filename = f"{podcast_id}_{page_num}.mu" if page_num > 1 else f"{podcast_id}.mu"
            filepath = self.output_dir / filename
            filepath.write_text("\n".join(lines))
            files_written.append(filepath)
        
        return files_written

    def _format_duration(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        mins = seconds // 60
        secs = seconds % 60
        if mins < 60:
            return f"{mins}:{secs:02d}"
        hours = mins // 60
        mins = mins % 60
        return f"{hours}:{mins:02d}:{secs:02d}"
