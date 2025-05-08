import tweepy
import os
from datetime import datetime

# Twitter API credentials from GitHub Secrets
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

def get_twitter_api():
    # Create a v2 client
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    return client

def get_tweets(client, query="python", max_results=10):
    # Use search query instead of timeline - available in free API
    tweets = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=['created_at', 'public_metrics', 'author_id']
    )
    return tweets.data

def summarize_tweets(tweets):
    if not tweets or len(tweets) == 0:
        return "No tweets found matching the search criteria."
    
    summary = f"Twitter Feed Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # Add search results
    summary += "Recent Tweets:\n"
    for i, tweet in enumerate(tweets):
        summary += f"{i+1}. Tweet ID: {tweet.id}\n"
        summary += f"   Content: {tweet.text[:100]}...\n"
        if hasattr(tweet, 'public_metrics'):
            metrics = tweet.public_metrics
            summary += f"   Likes: {metrics.get('like_count', 0)}, Retweets: {metrics.get('retweet_count', 0)}\n"
        summary += "\n"
    
    return summary

def save_summary(summary):
    # Save to file in summaries directory
    os.makedirs('summaries', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"summaries/twitter_summary_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)
    
    return filename

def main():
    try:
        print("Starting Twitter summary generation...")
        client = get_twitter_api()
        # You can customize this search query
        tweets = get_tweets(client, query="python", max_results=10)
        summary = summarize_tweets(tweets)
        filename = save_summary(summary)
        print(f"Summary saved to {filename}")
    except Exception as e:
        print(f"Error generating summary: {e}")

if __name__ == "__main__":
    main()
