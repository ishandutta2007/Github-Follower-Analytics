from collections import Counter
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import requests
import time

GITHUB_USERNAME = 'ishandutta2007'  # Target username

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

def get_headers():
    """Returns headers with auth if token is provided."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if ADMIN_TOKEN and ADMIN_TOKEN != 'your_personal_access_token_here':
        headers['Authorization'] = f'token {ADMIN_TOKEN}'
    return headers

def get_followers(username):
    """Fetches all followers for a given user (handles pagination)."""
    followers = []
    page = 1
    url = f"https://api.github.com/users/{username}/followers"
    
    print(f"Fetching followers for {username}...")
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
        
    return followers

def get_user_details(follower_url):
    """Fetches detailed profile info for a single follower."""
    try:
        response = requests.get(follower_url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
             print("Rate limit hit! Sleeping for 60 seconds...")
             time.sleep(60)
             return get_user_details(follower_url) # Retry
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
    # Show top 10 locations, group the rest as "Other"
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
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.show()

def main():
    # 1. Get list of followers
    followers_list = get_followers(GITHUB_USERNAME)
    print(f"Total followers found: {len(followers_list)}")
    
    if not followers_list:
        return

    # 2. Fetch details for each follower to get 'location'
    # NOTE: This performs 1 API call per follower. 
    # If you have 1000+ followers, this will take time and eat rate limits.
    locations = []
    print("Fetching follower details (this may take a moment)...")
    
    for i, follower in enumerate(followers_list):
        details = get_user_details(follower['url'])
        if details:
            loc = clean_location(details.get('location'))
            locations.append(loc)
        
        # Progress bar
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(followers_list)} profiles...")

    # 3. Plot the data
    print("Plotting data...")
    plot_demographics(locations)

if __name__ == "__main__":
    main()
