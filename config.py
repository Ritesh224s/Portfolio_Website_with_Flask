import os

GITHUB_USERNAME = "Ritesh224s"

# Cache settings
CACHE_FILE = os.path.join("data", "cache.json")
CACHE_TTL_SECONDS = 60 * 60  # 1 hour

# Contact form storage (SQLite file created on first run)
DB_FILE = os.path.join("data", "messages.db")

# Featured repos to pin first (slug names)
PINNED = [
    "Portfolio_Website_with_Flask",
    "Data_Analysis_CSV_Files",
    "REST-API-With-Flask",
    "news-headline-scraper",
    "To_Do_list_Application",
    "Calculator_CLI_App",
    "Triton_Wars",
    "Guess-Master",
    "JARVIS-AI-Bot",
]