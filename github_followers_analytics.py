from web_ui.analytics_service import get_analytics
import matplotlib.pyplot as plt

GITHUB_USERNAME = 'ishandutta2007'  # Default target username

def plot_demographics(target_username, location_stats, total_followers):
    """Plots a pie chart of the location demographics using Matplotlib for CLI."""
    labels = []
    sizes = []
    
    top_n = 9
    other_count = 0
    
    for i, (loc, count) in enumerate(location_stats):
        if i < top_n:
            labels.append(f"{loc} ({count})")
            sizes.append(count)
        else:
            other_count += count
            
    if other_count > 0:
        labels.append(f"Other ({other_count})")
        sizes.append(other_count)

    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title(f"Follower Demographics (Location) for {target_username}\n(Sample Size: {total_followers})")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

def main():
    print(f"🚀 Starting CLI Analytics for {GITHUB_USERNAME}...")
    data = get_analytics(GITHUB_USERNAME)
    
    print(f"\n✅ Analysis Complete!")
    print(f"Total followers found: {data['total_followers']}")
    
    print("\n📊 Top Locations:")
    for loc, count in data['location_stats'][:10]:
        print(f"  - {loc}: {count}")

    print("\n📈 Plotting data...")
    plot_demographics(GITHUB_USERNAME, data['location_stats'], data['total_followers'])

if __name__ == "__main__":
    main()
