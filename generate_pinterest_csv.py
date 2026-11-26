import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

# ================= CONFIGURATION =================
GITHUB_USERNAME = "ArkadebMisra"
REPO_NAME = "pintrest_poster"
BRANCH = "main"
REPO_SUBFOLDER = "wallpapers"

IMAGE_FOLDER = r"D:\ComfyUI_windows_portable\ComfyUI\output\z-image_foodzz\prompt_creator\generated_wallpapers\pintrest_poster\wallpapers"
PINTEREST_BOARD_NAME = "Wallpapers"  # Must match your exact Pinterest board name
DEFAULT_DESCRIPTION = "Download high-res 9:16 mobile wallpapers! #wallpaper #phonewallpaper #aesthetic"
DESTINATION_LINK = ""  # Optional: e.g., your Ko-fi URL
KEYWORDS = "mobile wallpaper, phone background, aesthetic wallpaper"

INTERVAL_MINUTES = 5
# =================================================

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CSV_HEADERS = [
    "Title",
    "Media URL",
    "Pinterest board",
    "Thumbnail",
    "Description",
    "Link",
    "Publish date",
    "Keywords"
]


def format_title(filename):
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").strip()[:100]


def main():
    folder = Path(IMAGE_FOLDER)
    if not folder.exists():
        print(f"Error: Folder not found -> {IMAGE_FOLDER}")
        return

    images = sorted([
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not images:
        print("No images found in folder.")
        return

    # Start scheduling 30 minutes from current UTC time; timedelta automatically rolls into next day(s)
    schedule_time = datetime.now(timezone.utc) + timedelta(minutes=30)

    batch_size = 200
    for batch_idx in range(0, len(images), batch_size):
        batch = images[batch_idx:batch_idx + batch_size]
        part_num = (batch_idx // batch_size) + 1
        csv_filename = folder.parent / f"pinterest_bulk_upload_part{part_num}.csv"

        with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

            for img in batch:
                title = format_title(img.name)
                encoded_name = quote(img.name)
                prefix = f"{REPO_SUBFOLDER.strip('/')}/" if REPO_SUBFOLDER.strip("/") else ""
                media_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/{prefix}{encoded_name}"
                publish_date_str = schedule_time.strftime("%Y-%m-%dT%H:%M:%S")

                writer.writerow([
                    title,
                    media_url,
                    PINTEREST_BOARD_NAME,
                    "",
                    f"{title} - {DEFAULT_DESCRIPTION}",
                    DESTINATION_LINK,
                    publish_date_str,
                    KEYWORDS
                ])
                schedule_time += timedelta(minutes=INTERVAL_MINUTES)

        print(f"Created {csv_filename.name} with {len(batch)} pins (ends at {schedule_time.strftime('%Y-%m-%d %H:%M UTC')}).")


if __name__ == "__main__":
    main()