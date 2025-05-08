import tweepy
import os
from datetime import datetime

# Twitter API credentials from GitHub Secrets
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

def get_twitter_api():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)

def get_home_timeline(api, count=100):
    return api.home_timeline(count=count)

def summarize_tweets(tweets):
    summary = f"Twitter Feed Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # Group tweets by topic/user/etc
    users = {}
    topics = {}
    
    for tweet in tweets:
        # Group by user
        username = tweet.user.screen_name
        if username not in users:
            users[username] = []
        users[username].append(tweet.text)
        
        # Extract hashtags for topics
        hashtags = [tag['text'] for tag in tweet.entities['hashtags']]
        for tag in hashtags:
            if tag not in topics:
                topics[tag] = []
            topics[tag].append(tweet.text)
    
    # Add most active users
    summary += "Most Active Users:\n"
    for user, tweets in sorted(users.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        summary += f"- @{user} ({len(tweets)} tweets)\n"
    
    # Add trending topics
    if topics:
        summary += "\nTrending Topics:\n"
        for topic, tweets in sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            summary += f"- #{topic} ({len(tweets)} tweets)\n"
    
    # Add sample of recent tweets
    summary += "\nRecent Highlights:\n"
    for tweet in tweets[:5]:
        summary += f"- @{tweet.user.screen_name}: {tweet.text[:100]}...\n"
    
    return summary

def save_summary(summary):
    # Save to file in summaries directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"summaries/twitter_summary_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)
    
    # Also save latest summary
    with open("summaries/latest_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    
    return filename

def main():
    try:
        print("Starting Twitter summary generation...")
        api = get_twitter_api()
        tweets = get_home_timeline(api)
        summary = summarize_tweets(tweets)
        filename = save_summary(summary)
        print(f"Summary saved to {filename}")
    except Exception as e:
        print(f"Error generating summary: {e}")

if __name__ == "__main__":
    main()
