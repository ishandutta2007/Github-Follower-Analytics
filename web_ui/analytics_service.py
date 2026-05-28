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
CITY_TO_COUNTRY = {
    "abu dhabi": "United Arab Emirates",
    "amsterdam": "Netherlands",
    "ankara": "Turkey",
    "austin": "United States",
    "bangalore": "India",
    "barcelona": "Spain",
    "beijing": "China",
    "bengaluru": "India",
    "berlin": "Germany",
    "berlin": "Germany",
    "bogota": "Colombia",
    "boston": "United States",
    "bucharest": "Romania",
    "budapest": "Hungary",
    "buenos aires": "Argentina",
    "cairo": "Egypt",
    "cambridge": "United Kingdom",
    "cape town": "South Africa",
    "chennai": "India",
    "chicago": "United States",
    "delhi": "India",
    "dubai": "United Arab Emirates",
    "geneva": "Switzerland",
    "gurgaon": "India",
    "hamburg": "Germany",
    "hamburg": "Germany",
    "helsinki": "Finland",
    "hyderabad": "India",
    "istanbul": "Turkey",
    "johannesburg": "South Africa",
    "krakow": "Poland",
    "kyiv": "Ukraine",
    "lagos": "Nigeria",
    "lima": "Peru",
    "london": "United Kingdom",
    "los angeles": "United States",
    "lyon": "France",
    "lyon": "France",
    "madrid": "Spain",
    "manchester": "United Kingdom",
    "melbourne": "Australia",
    "mexico city": "Mexico",
    "milan": "Italy",
    "montreal": "Canada",
    "moscow": "Russian Federation",
    "mountain view": "United States",
    "mumbai": "India",
    "munich": "Germany",
    "munich": "Germany",
    "nairobi": "Kenya",
    "new york": "United States",
    "osaka": "Japan",
    "oslo": "Norway",
    "palo alto": "United States",
    "paris": "France",
    "paris": "France",
    "prague": "Czech Republic",
    "pune": "India",
    "rio de janeiro": "Brazil",
    "riyadh": "Saudi Arabia",
    "rome": "Italy",
    "saint petersburg": "Russian Federation",
    "san francisco": "United States",
    "santiago": "Chile",
    "sao paulo": "Brazil",
    "seattle": "United States",
    "shanghai": "China",
    "shenzhen": "China",
    "singapore": "Singapore",
    "stockholm": "Sweden",
    "sydney": "Australia",
    "tehran": "Iran",
    "tel aviv": "Israel",
    "tokyo": "Japan",
    "toronto": "Canada",
    "vancouver": "Canada",
    "vienna": "Austria",
    "warsaw": "Poland",
    "zurich": "Switzerland",
}

# Mapping of popular sirnames to countries
SIRNAME_TO_COUNTRY = {
    "Abaspahic": "Balkans",
    "Abbas": "Middle East",
    "Abdullayev": "Russia",
    "AbdulMuheez": "Spain",
    "Abid": "Middle East",
    "Abramov": "Russia",
    "Adedapo": "Latin America",
    "Aggarwal": "India",
    "Ahmad": "Middle East",
    "Ahmed": "Egypt",
    "Ahmed": "Middle East",
    "Aich": "Balkans",
    "Akegbeyale": "China",
    "AL-Zadjali": "China",
    "Albacino": "Latin America",
    "Alferov": "Russia",
    "Alharazin": "Russia",
    "Ali": "Egypt",
    "Allahverdiyev": "Russia",
    "Alves": "Spain",
    "alwin": "Russia",
    "Alyson": "Scandinavia",
    "Amin": "Russia",
    "Amireddy": "India",
    "Anand": "India",
    "Anderson": "Scandinavia",
    "Aquino": "Latin America",
    "Armstrong": "China",
    "Asadov": "Russia",
    "athawale": "China",
    "Attia": "Latin America",
    "Aung": "China",
    "Ayodele": "China",
    "Bachhamba": "Middle East",
    "Baez": "Spain",
    "Bahin": "Russia",
    "Banerjee": "India",
    "Baning": "China",
    "Bashir": "Middle East",
    "Becker": "Germany",
    "Benson": "Scandinavia",
    "Benyahia": "Latin America",
    "Bermejo": "Latin America",
    "Bernard": "France",
    "Bhuin": "Russia",
    "Bianchi": "Italy",
    "Bidali": "China",
    "Blázquez": "Latin America",
    "Boev": "Russia",
    "Borges": "Spain",
    "Borkowski": "Russia",
    "Bralli": "China",
    "Bulsho": "Latin America",
    "Caceres": "Spain",
    "Castelli": "China",
    "Cetin": "Russia",
    "Challapalli": "China",
    "Chatterjee": "India",
    "Chaudhary": "India",
    "Chen": "China",
    "Cheng": "China",
    "Choi": "Korea, Republic of",
    "Christiano": "Latin America",
    "Civalski": "Russia",
    "Cleves": "Spain",
    "Colvin": "Russia",
    "Crises": "Spain",
    "Cuong": "China",
    "Dadhich": "Balkans",
    "Dansoko": "Latin America",
    "Das": "India",
    "Delfin": "Russia",
    "Dennison": "Scandinavia",
    "Dev": "India",
    "Difeng": "China",
    "Ding": "China",
    "Domanov": "Russia",
    "Domingo": "Latin America",
    "Dong": "China",
    "Dubnov": "Russia",
    "Duong": "China",
    "Dũng": "China",
    "Elele": "China",
    "ElHafez": "Latin America",
    "Epili": "China",
    "Ermolaev": "Russia",
    "Esin": "Russia",
    "Esposito": "Italy",
    "Eynali": "China",
    "Ezpain": "Russia",
    "Faccioli": "China",
    "Fadili": "China",
    "Fatima": "Middle East",
    "Faustino": "Latin America",
    "Feng": "China",
    "Fernandes": "Spain",
    "Fernandez": "Spain",
    "Fernández": "Spain",
    "Fernández-Fuertes": "Spain",
    "Ferrari": "Italy",
    "Fischer": "Germany",
    "Flores": "Spain",
    "Forlin": "Russia",
    "Fortin": "Russia",
    "Franklin": "Russia",
    "Freires": "Latin America",
    "Fuentes": "Spain",
    "Fuertes": "Spain",
    "Games": "Spain",
    "Garcia": "Spain",
    "Garrison": "Scandinavia",
    "Geminic": "Balkans",
    "Ghiyosov": "Russia",
    "Ghogale": "China",
    "Gibson": "Scandinavia",
    "Gleizes": "Spain",
    "Gofurjonov": "Russia",
    "Gomes": "Spain",
    "Gomez": "Spain",
    "Gong": "China",
    "Gonzalez": "Spain",
    "González": "Spain",
    "Gonçalves": "Spain",
    "Graves": "Spain",
    "Grayson": "Scandinavia",
    "Guimaraães": "Spain",
    "Gupta": "India",
    "Gutiérrez": "Spain",
    "Habeebuddin": "Russia",
    "Harrison": "Scandinavia",
    "Hasnain": "Russia",
    "Hassan": "Egypt",
    "Hassan": "Middle East",
    "Hernandez": "Spain",
    "Hoffmann": "Germany",
    "Hosen": "Scandinavia",
    "Hossain": "Russia",
    "hossain": "Russia",
    "Hossen": "Scandinavia",
    "Hristov": "Russia",
    "Htet": "China",
    "Huang": "China",
    "Hughes": "Spain",
    "Hunain": "Russia",
    "Hung": "China",
    "Husain": "Russia",
    "Hussain": "Russia",
    "Hussein": "Russia",
    "Huynh": "Viet Nam",
    "Ibrahim": "Egypt",
    "Iglesia": "Latin America",
    "Inang": "China",
    "Industries": "Spain",
    "Inomjonov": "Russia",
    "Islam": "Middle East",
    "Ito": "Japan",
    "Ivanov": "Russian Federation",
    "Izzatullaev": "Russia",
    "İncili": "China",
    "Jacobson": "Scandinavia",
    "Jain": "India",
    "Jalili": "China",
    "Jang": "China",
    "Jeong": "China",
    "Jimenez": "Spain",
    "Johnson": "Scandinavia",
    "Jones": "Spain",
    "Jordacevic": "Balkans",
    "Jumaniyozov": "Russia",
    "Jung": "Korea, Republic of",
    "Kabali": "China",
    "Kali": "China",
    "Kang": "China",
    "Kavlakov": "Russia",
    "Kevin": "Russia",
    "Khabalov": "Russia",
    "Khaing": "China",
    "Khan": "Middle East",
    "khoa": "China",
    "Khylkouski": "Russia",
    "Kim": "Korea, Republic of",
    "Kipsang": "China",
    "Kiselev": "Russia",
    "Kitirueangsang": "China",
    "Ko": "Latin America",
    "Kokalovic": "Balkans",
    "Kolendowski": "Russia",
    "Kostukovic": "Balkans",
    "Kowalczyk": "Poland",
    "Kowalski": "Poland",
    "Koçanlı": "China",
    "Krishnavinayak": "India",
    "Kuang": "China",
    "Kucierski": "Russia",
    "Kumar": "India",
    "Kunshin": "Russia",
    "Kurmanbaev": "Russia",
    "Kuznetsov": "Russian Federation",
    "Lamaimuang": "China",
    "Le": "China",
    "Lee": "Korea, Republic of",
    "Lewin": "Russia",
    "Li": "China",
    "Lin": "Russia",
    "Ling": "China",
    "Liu": "China",
    "Lopes": "Spain",
    "Lopez": "Spain",
    "Lukin": "Russia",
    "Lunganlung": "China",
    "Lárez": "Spain",
    "Mahankali": "China",
    "Maksakov": "Russia",
    "Mali": "China",
    "Mangas": "Latin America",
    "Manzoli": "China",
    "Marques": "Spain",
    "Martin": "Russia",
    "Martinez": "Spain",
    "Martínez": "Spain",
    "Mason": "Scandinavia",
    "Mendeleïev": "Russia",
    "Mendes": "Spain",
    "Mendez": "Spain",
    "Meneses": "Spain",
    "Meng": "China",
    "Meshchain": "Russia",
    "Mishra": "India",
    "Morrison": "Scandinavia",
    "Moses": "Spain",
    "Mueller": "Germany",
    "Muhandisin": "Russia",
    "Mukherjee": "India",
    "Muller": "Germany",
    "Nair": "India",
    "Namdev": "Russia",
    "Nayak": "India",
    "Nelson": "Scandinavia",
    "Neto": "Latin America",
    "Nevarez": "Spain",
    "Neves": "Spain",
    "Nguyen": "Viet Nam",
    "Nikitin": "Russia",
    "Nithin": "Russia",
    "Novaes": "Spain",
    "Novak": "Poland",
    "Oguntimehin": "Russia",
    "Olivares": "Spain",
    "Oliveira": "Brazil",
    "OpenSources": "Spain",
    "Osali": "China",
    "Otieno": "Latin America",
    "Paes": "Spain",
    "Paixao": "Latin America",
    "Park": "Korea, Republic of",
    "Patel": "India",
    "Pedro": "Latin America",
    "Pekin": "Russia",
    "Penkov": "Russia",
    "Perez": "Spain",
    "Peterson": "Scandinavia",
    "Petit": "France",
    "Petrov": "Russian Federation",
    "Pham": "Viet Nam",
    "Phong": "China",
    "Pires": "Spain",
    "Pochanov": "Russia",
    "Popov": "Russian Federation",
    "Rabin": "Russia",
    "Radojicic": "Balkans",
    "Rafiqhuddin": "Russia",
    "Ramirez": "Spain",
    "Ramírez": "Spain",
    "Razali": "China",
    "Reddy": "India",
    "Reyes": "Spain",
    "Robert": "France",
    "Robertson": "Scandinavia",
    "Rodrigo": "Latin America",
    "Rodrigues": "Brazil",
    "Rodriguez": "Spain",
    "Rodríguez": "Spain",
    "Romano": "Latin America",
    "Romero": "Latin America",
    "Rosales": "Spain",
    "Rossi": "Italy",
    "Rusdiyanto": "Latin America",
    "Russo": "Italy",
    "Sahin": "Russia",
    "Sales": "Spain",
    "Samiyev": "Russia",
    "Sanchez": "Latin America",
    "Santos": "Brazil",
    "Sato": "Japan",
    "Savin": "Russia",
    "Schmidt": "Germany",
    "Schneider": "Germany",
    "Schulz": "Germany",
    "Sen": "India",
    "Sergeev": "Russia",
    "Shafranski": "Russia",
    "Shao-ming": "China",
    "Sharma": "India",
    "Shin": "Russia",
    "Shylenko": "Latin America",
    "Sigolo": "Latin America",
    "Silva": "Brazil",
    "Singh": "India",
    "Sinhorelli": "China",
    "Smarason": "Scandinavia",
    "Smirnov": "Russian Federation",
    "Soares": "Spain",
    "Sokolov": "Russian Federation",
    "Son": "Scandinavia",
    "Song": "China",
    "Souza": "Brazil",
    "Spurlin": "Russia",
    "Sreypich": "Balkans",
    "Stanojkovski": "Russia",
    "Stinson": "Scandinavia",
    "Stokes": "Spain",
    "Susenkova": "Russia",
    "Suzuki": "Japan",
    "SWAIN": "Russia",
    "Swain": "Russia",
    "Sánchez": "Spain",
    "Sánchez-Herrero": "Latin America",
    "Sáng": "China",
    "Tabares": "Spain",
    "Takahashi": "Japan",
    "Tanaka": "Japan",
    "Tang": "China",
    "Tavares": "Spain",
    "Technologies": "Spain",
    "Thomas": "France",
    "Thompson": "Scandinavia",
    "To'ychiyev": "Russia",
    "Tomicic": "Balkans",
    "Tommaso": "Latin America",
    "Toole": "China",
    "Torquato": "Latin America",
    "Torres": "Spain",
    "Tran": "Viet Nam",
    "Truong": "China",
    "Tsyganov": "Russia",
    "Tuhin": "Russia",
    "Tursunov": "Russia",
    "Uddin": "Russia",
    "Vang": "China",
    "Vasilev": "Russia",
    "Vasquez": "Latin America",
    "Velasquez": "Spain",
    "Ventures": "Spain",
    "Volkov": "Russian Federation",
    "Vova": "Russia",
    "Vásquez": "Spain",
    "Vương": "China",
    "Wagner": "Germany",
    "Waites": "Spain",
    "Wali": "China",
    "Wang": "China",
    "Watanabe": "Japan",
    "Weber": "Germany",
    "Wibisono": "Latin America",
    "Wilson": "Scandinavia",
    "Wisniewski": "Poland",
    "Wojcik": "Poland",
    "Wondoson": "Scandinavia",
    "Xing": "China",
    "Yadav": "India",
    "Yang": "China",
    "Yasin": "Russia",
    "yong": "China",
    "Young": "China",
    "Zemlyakov": "Russia",
    "Zhang": "China",
    "Zheng": "China",
    "Zhong": "China",
    "Zimin": "Russia",
    "Çerin": "Russia",
    "đăng": "China",
    "Кasimov": "Russia",
}

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
            yield {"type": "log", "message": f"  [{source}] {login} [{name}]-> {loc}"}

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
