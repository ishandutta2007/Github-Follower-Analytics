from collections import Counter
from dotenv import load_dotenv
import os
import requests
import time
import json
import pycountry

# Resolve cache paths relative to this file's directory (go up one level to root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLLOWERS_CACHE_FILE = os.path.join(BASE_DIR, "followers_cache.json")
USERS_CACHE_FILE = os.path.join(BASE_DIR, "users_cache.json")
CACHE_EXPIRY_24H = 24 * 60 * 60  # 24 hours in seconds

# Pre-compute country mappings for faster lookups
COUNTRIES = {c.name.lower(): c.name for c in pycountry.countries}
COUNTRY_CODES = {c.alpha_2.lower(): c.name for c in pycountry.countries}
# Special common cases not easily caught by pycountry or common variations
COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "uk": "United Kingdom",
    "uae": "United Arab Emirates",
    "russia": "Russian Federation",
    "korea": "Korea, Republic of",
    "vietnam": "Viet Nam",
}

# Mapping of major tech hubs/cities to countries
def load_city_to_country():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "city_to_country.json")
    return load_json_file(json_path, {})


CITY_TO_COUNTRY = load_city_to_country()


# Mapping of popular sirnames to countries
def load_sirname_to_country():
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sirname_to_country.json"
    )
    return load_json_file(json_path, {})


SIRNAME_TO_COUNTRY = load_sirname_to_country()

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


def load_json_file(file_path, default_value):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return default_value


def save_json_file(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if ADMIN_TOKEN and ADMIN_TOKEN != "your_personal_access_token_here":
        headers["Authorization"] = f"token {ADMIN_TOKEN}"
    return headers


def fetch_followers(username, followers_cache):
    current_time = time.time()

    if username in followers_cache:
        cached_data = followers_cache[username]
        if current_time - cached_data.get("timestamp", 0) < CACHE_EXPIRY_24H:
            return cached_data["data"], False

    followers = []
    page = 1
    url = f"https://api.github.com/users/{username}/followers"

    while True:
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=get_headers(), params=params)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        followers.extend(data)
        page += 1

    if followers:
        followers_cache[username] = {"timestamp": current_time, "data": followers}
        save_json_file(FOLLOWERS_CACHE_FILE, followers_cache)
    return followers, True


def fetch_user_details(username, follower_url, users_cache):
    if username in users_cache:
        return users_cache[username], False

    try:
        response = requests.get(follower_url, headers=get_headers())
        if response.status_code == 200:
            details = response.json()
            users_cache[username] = details
            return details, True
        elif response.status_code == 403:
            time.sleep(60)
            return fetch_user_details(username, follower_url, users_cache)
    except Exception as e:
        print(f"Error: {e}")
    return None, False


def normalize_location(text):
    """Deep cleaning and country detection from a text string."""
    if not text:
        return "Unknown"

    text_lower = text.lower().strip()

    # 1. Direct Alias Check
    if text_lower in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text_lower]

    # 2. City Mapping Check (e.g., "San Francisco" -> "United States")
    for city, country in CITY_TO_COUNTRY.items():
        if city in text_lower:
            return country

    # 3. Country Name Search (e.g., "Working in Germany")
    for country_lower, country_name in COUNTRIES.items():
        # Match only if it's a whole word to avoid things like "Indiana" matching "India"
        if f" {country_lower} " in f" {text_lower} " or text_lower == country_lower:
            return country_name

    # 4. Country Code Check (e.g., "London, UK")
    parts = [
        p.strip().strip("()[]{}")
        for p in text.replace(",", " ").replace(".", " ").split()
    ]
    for part in reversed(parts):
        part_lower = part.lower()
        if part_lower in COUNTRY_CODES:
            return COUNTRY_CODES[part_lower]
        if part_lower in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[part_lower]

    # 5. Sirname Mapping Check (e.g., "Aggarwal" -> "India")
    parts_lower = [p.lower() for p in parts]
    for sirname, country in SIRNAME_TO_COUNTRY.items():
        if sirname.lower() in parts_lower:
            return country

    return "Unknown"


def infer_country(details):
    """Infers country from user profile details (location and name)."""
    if not details:
        return "Unknown"

    location = details.get("location")
    name = details.get("name")

    # Priority 1: Location field
    if location:
        country = normalize_location(location)
        if country != "Unknown":
            return country

    # Priority 2: Name field (fallback)
    if name:
        country = normalize_location(name)
        if country != "Unknown":
            return country

    return "Unknown"


def get_analytics_generator(target_username):
    """Generator version that yields logs and final data."""
    followers_cache = load_json_file(FOLLOWERS_CACHE_FILE, {})
    users_cache = load_json_file(USERS_CACHE_FILE, {})

    yield {"type": "log", "message": f"🚀 Starting analytics for {target_username}..."}

    # 1. Fetch followers
    if target_username in followers_cache and (
        time.time() - followers_cache[target_username].get("timestamp", 0)
        < CACHE_EXPIRY_24H
    ):
        yield {
            "type": "log",
            "message": f"Using cached followers list for {target_username}...",
        }
    else:
        yield {
            "type": "log",
            "message": f"Fetching followers for {target_username} from GitHub API...",
        }

    followers_list, fetched_list_from_api = fetch_followers(
        target_username, followers_cache
    )

    if not followers_list:
        yield {
            "type": "error",
            "message": f"No followers found for {target_username} or API error.",
        }
        return

    yield {"type": "log", "message": f"Total followers found: {len(followers_list)}"}
    yield {"type": "log", "message": "Fetching and inferring follower demographics..."}

    results = []
    locations = []
    total = len(followers_list)

    for i, follower in enumerate(followers_list):
        login = follower["login"]
        url = follower["url"]

        # Yield progress for UI timers
        yield {"type": "progress", "current": i + 1, "total": total}

        details, fetched_from_api = fetch_user_details(login, url, users_cache)

        if details:
            loc = infer_country(details)
            name = details.get("name")
            locations.append(loc)
            source = "API" if fetched_from_api else "CACHE"
            results.append({"username": login, "location": loc, "source": source})
            rawloc = details.get("location")
            if loc == "Unknown" and rawloc != None:
                yield {
                    "type": "log",
                    "message": f" [{source}] {login} [{name}][{rawloc}]-> {loc}",
                }

        # Save users cache every 50 records
        if (i + 1) % 50 == 0:
            save_json_file(USERS_CACHE_FILE, users_cache)
            yield {
                "type": "log",
                "message": f"  --- Processed {i + 1}/{len(followers_list)} profiles (Cache saved) ---",
            }
        elif (i + 1) % 10 == 0:
            yield {
                "type": "log",
                "message": f"  --- Processed {i + 1}/{len(followers_list)} profiles ---",
            }

    save_json_file(USERS_CACHE_FILE, users_cache)

    location_counts = Counter(locations)

    final_data = {
        "target_username": target_username,
        "total_followers": len(followers_list),
        "location_stats": location_counts.most_common(),
        "details": results,
    }

    yield {"type": "data", "payload": final_data}


def get_analytics(target_username):
    """Sync version for CLI, consumes the generator."""
    final_data = None
    for item in get_analytics_generator(target_username):
        if item["type"] == "log":
            print(item["message"])
        elif item["type"] == "error":
            print(f"ERROR: {item['message']}")
        elif item["type"] == "data":
            final_data = item["payload"]
    return final_data
