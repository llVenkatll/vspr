import tweepy
import time
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Twitter API credentials from GitHub Secrets
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# Email settings from GitHub Secrets
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") 
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

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

def send_email(summary):
    """Send the summary via email using SMTP."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("Email credentials not set. Skipping email.")
        return False
    
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"Twitter Feed Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Attach the summary as plain text
        msg.attach(MIMEText(summary, 'plain'))
        
        # Connect to Gmail SMTP server and send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"Email sent successfully to {EMAIL_RECEIVER}")
        return True
    
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_summary(summary):
    """Save the summary to a file and send it via email."""
    # Option 1: Save to file
    os.makedirs('summaries', exist_ok=True)
    filename = f"summaries/twitter_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"Summary saved to {filename}")
    
    # Option 2: Send email
    send_email(summary)
    
    return filename

def job():
    try:
        api = get_twitter_api()
        tweets = get_home_timeline(api)
        summary = summarize_tweets(tweets)
        send_summary(summary)
        print(f"Summary generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"Error: {e}")

# If running directly (not imported)
if __name__ == "__main__":
    # Run once immediately
    job()
