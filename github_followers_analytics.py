from collections import Counter
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import requests
import time
import json

GITHUB_USERNAME = 'ishandutta2007'  # Target username
FOLLOWERS_CACHE_FILE = 'followers_cache.json'
USERS_CACHE_FILE = 'users_cache.json'
CACHE_EXPIRY_24H = 24 * 60 * 60  # 24 hours in seconds

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

def load_json_file(file_path, default_value):
    """Utility to load a JSON file with a default value on failure."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return default_value

def save_json_file(file_path, data):
    """Utility to save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def get_headers():
    """Returns headers with auth if token is provided."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if ADMIN_TOKEN and ADMIN_TOKEN != 'your_personal_access_token_here':
        headers['Authorization'] = f'token {ADMIN_TOKEN}'
    return headers

def get_followers(username, followers_cache):
    """Fetches followers with a 24-hour time-based cache."""
    current_time = time.time()
    
    if username in followers_cache:
        cached_data = followers_cache[username]
        # Check if cache is still valid (less than 24 hours old)
        if current_time - cached_data.get('timestamp', 0) < CACHE_EXPIRY_24H:
            print(f"Using cached followers list for {username} (fetched recently)...")
            return cached_data['data']
        else:
            print(f"Cached followers list for {username} is older than 24h. Refreshing...")

    followers = []
    page = 1
    url = f"https://api.github.com/users/{username}/followers"
    
    print(f"Fetching followers for {username} from GitHub API...")
    while True:
        params = {'per_page': 100, 'page': page}
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code != 200:
            print(f"Error fetching followers: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        if not data:
            break
            
        followers.extend(data)
        print(f"  Found {len(data)} followers on page {page}...")
        page += 1
        
    if followers:
        followers_cache[username] = {
            "timestamp": current_time,
            "data": followers
        }
        save_json_file(FOLLOWERS_CACHE_FILE, followers_cache)

    return followers

def get_user_details(username, follower_url, users_cache):
    """Fetches detailed profile info with idempotent caching by username."""
    if username in users_cache:
        print(f"  [CACHE] {username}")
        return users_cache[username]

    print(f"  [API] {username}...")
    try:
        response = requests.get(follower_url, headers=get_headers())
        if response.status_code == 200:
            details = response.json()
            users_cache[username] = details
            return details
        elif response.status_code == 403:
             print("Rate limit hit! Sleeping for 60 seconds...")
             time.sleep(60)
             return get_user_details(username, follower_url, users_cache) # Retry
    except Exception as e:
        print(f"Error: {e}")
    return None

def clean_location(location):
    """Normalizes location strings."""
    if not location:
        return "Unknown"
    
    # Basic cleanup (remove extraneous spaces, handle case)
    loc = location.strip().title()
    
    # Simple normalization examples (expand as needed)
    if "United States" in loc or "Usa" in loc or "Us" == loc:
        return "United States"
    if "China" in loc or "Cn" == loc:
        return "China"
    if "India" in loc:
        return "India"
    if "London" in loc or "Uk" == loc:
        return "United Kingdom"
    
    return loc

def plot_demographics(locations):
    """Plots a pie chart of the location demographics."""
    # Count occurrences
    counts = Counter(locations)
    
    # Sort and separate top locations from "Other"
    total_followers = sum(counts.values())
    sorted_locs = counts.most_common()
    
    labels = []
    sizes = []
    
    top_n = 9
    other_count = 0
    
    for i, (loc, count) in enumerate(sorted_locs):
        if i < top_n:
            labels.append(f"{loc} ({count})")
            sizes.append(count)
        else:
            other_count += count
            
    if other_count > 0:
        labels.append(f"Other ({other_count})")
        sizes.append(other_count)

    # Plotting
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title(f"Follower Demographics (Location) for {GITHUB_USERNAME}\n(Sample Size: {total_followers})")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

def main():
    # 0. Load caches
    followers_cache = load_json_file(FOLLOWERS_CACHE_FILE, {})
    users_cache = load_json_file(USERS_CACHE_FILE, {})

    # 1. Get list of followers
    followers_list = get_followers(GITHUB_USERNAME, followers_cache)
    print(f"Total followers found: {len(followers_list)}")
    
    if not followers_list:
        return

    # 2. Fetch details for each follower to get 'location'
    locations = []
    print("Fetching follower details (using idempotent cache where available)...")
    
    for i, follower in enumerate(followers_list):
        login = follower['login']
        url = follower['url']
        
        details = get_user_details(login, url, users_cache)
        if details:
            loc = clean_location(details.get('location'))
            locations.append(loc)
        
        # Save users cache every 50 records to prevent data loss
        if (i + 1) % 50 == 0:
            save_json_file(USERS_CACHE_FILE, users_cache)
            print(f"  Processed {i + 1}/{len(followers_list)} profiles (Cache saved)...")
        elif (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(followers_list)} profiles...")

    # Final cache save
    save_json_file(USERS_CACHE_FILE, users_cache)

    # 3. Plot the data
    print("Plotting data...")
    plot_demographics(locations)

if __name__ == "__main__":
    main()
