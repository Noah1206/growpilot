"""Twitter/X.com Automation Service using Tweepy."""
import os
import tweepy
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TwitterAutomation:
    """
    Twitter/X.com automation service for searching users and sending DMs.

    Features:
    - Search tweets by keywords and hashtags
    - Extract user profiles based on tweet content
    - Send personalized DMs to users
    - Rate limiting and safety features
    """

    def __init__(self):
        """Initialize Twitter API client with credentials from .env."""
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')

        if not api_key or not api_secret:
            logger.warning("Twitter API credentials not configured. Twitter automation disabled.")
            self.api = None
            self.client = None
            return

        # OAuth 1.0a Authentication
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )

        # Create API v1.1 client (for DMs and some user data)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        # Create API v2 client (for modern search)
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )

        # Verify authentication
        try:
            user = self.api.verify_credentials()
            self.username = user.screen_name
            logger.info(f"✅ Twitter authenticated as: @{self.username}")
        except Exception as e:
            logger.error(f"❌ Twitter authentication failed: {e}")
            raise

    async def search_tweets(
        self,
        keywords: str,
        max_results: int = 100,
        language: str = "en"
    ) -> List[Dict]:
        """
        Search recent tweets matching keywords using Twitter API v2.

        Args:
            keywords: Search query (e.g., "stock investing" or "#investing")
            max_results: Maximum number of tweets to retrieve (default: 100, max: 100 per request)
            language: Language code (default: "en")

        Returns:
            List of tweet dictionaries with user data
        """
        try:
            logger.info(f"🔍 Searching tweets for: {keywords}")

            # Build search query
            query = f"{keywords} -is:retweet lang:{language}"

            # Search tweets using API v2
            tweets_data = []
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang', 'context_annotations'],
                user_fields=['username', 'name', 'description', 'public_metrics', 'verified'],
                expansions=['author_id']
            )

            if not response.data:
                logger.info("No tweets found")
                return []

            # Map user data
            users = {user.id: user for user in response.includes['users']}

            # Process tweets
            for tweet in response.data:
                user = users.get(tweet.author_id)
                if not user:
                    continue

                tweet_data = {
                    'tweet_id': tweet.id,
                    'tweet_text': tweet.text,
                    'tweet_created': tweet.created_at.isoformat() if tweet.created_at else None,
                    'tweet_likes': tweet.public_metrics.get('like_count', 0),
                    'tweet_retweets': tweet.public_metrics.get('retweet_count', 0),
                    'tweet_replies': tweet.public_metrics.get('reply_count', 0),
                    'author_id': user.id,
                    'author_username': user.username,
                    'author_name': user.name,
                    'author_bio': user.description,
                    'author_followers': user.public_metrics.get('followers_count', 0),
                    'author_following': user.public_metrics.get('following_count', 0),
                    'author_tweets': user.public_metrics.get('tweet_count', 0),
                    'author_verified': user.verified,
                    'author_url': f"https://twitter.com/{user.username}"
                }

                tweets_data.append(tweet_data)

            logger.info(f"✅ Found {len(tweets_data)} tweets")
            return tweets_data

        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ Twitter API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error searching tweets: {e}")
            return []

    async def get_user_profile(self, username: str) -> Optional[Dict]:
        """
        Get detailed user profile information.

        Args:
            username: Twitter username (without @)

        Returns:
            User profile dictionary or None if not found
        """
        try:
            logger.info(f"📊 Fetching profile for @{username}")

            # Get user data using API v2
            user = self.client.get_user(
                username=username,
                user_fields=['description', 'created_at', 'public_metrics', 'verified', 'url', 'location']
            )

            if not user.data:
                logger.warning(f"User @{username} not found")
                return None

            u = user.data

            profile = {
                'user_id': u.id,
                'username': u.username,
                'name': u.name,
                'bio': u.description,
                'location': u.location,
                'url': u.url,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'verified': u.verified,
                'followers_count': u.public_metrics.get('followers_count', 0),
                'following_count': u.public_metrics.get('following_count', 0),
                'tweet_count': u.public_metrics.get('tweet_count', 0),
                'profile_url': f"https://twitter.com/{u.username}"
            }

            # Get recent tweets
            recent_tweets = self.client.get_users_tweets(
                id=u.id,
                max_results=10,
                tweet_fields=['created_at', 'public_metrics']
            )

            if recent_tweets.data:
                profile['recent_tweets'] = [
                    {
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'likes': tweet.public_metrics.get('like_count', 0)
                    }
                    for tweet in recent_tweets.data
                ]
            else:
                profile['recent_tweets'] = []

            return profile

        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ Twitter API error fetching @{username}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching profile @{username}: {e}")
            return None

    async def send_dm(
        self,
        username: str,
        message: str
    ) -> bool:
        """
        Send a direct message to a Twitter user.

        Note: You can only send DMs to users who follow you or have enabled
        receiving messages from anyone.

        Args:
            username: Recipient's Twitter username (without @)
            message: Message content (max 10,000 characters)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📧 Sending DM to @{username}")

            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                logger.error(f"User @{username} not found")
                return False

            recipient_id = user.data.id

            # Send DM using API v1.1
            self.api.send_direct_message(
                recipient_id=recipient_id,
                text=message
            )

            logger.info(f"✅ DM sent successfully to @{username}")
            return True

        except tweepy.errors.Forbidden as e:
            logger.error(f"❌ Cannot send DM to @{username}: User doesn't accept DMs or you're not allowed. Error: {e}")
            return False
        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ Twitter API error sending DM to @{username}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending DM to @{username}: {e}")
            return False

    async def extract_unique_users(self, tweets: List[Dict]) -> List[str]:
        """
        Extract unique usernames from tweets.

        Args:
            tweets: List of tweet dictionaries

        Returns:
            List of unique usernames
        """
        unique_users = set()

        for tweet in tweets:
            username = tweet.get('author_username')
            if username and username != self.username:
                unique_users.add(username)

        return list(unique_users)

    async def test_connection(self) -> bool:
        """
        Test Twitter API connection.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            user = self.api.verify_credentials()
            logger.info(f"✅ Twitter connection test successful: @{user.screen_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Twitter connection test failed: {e}")
            return False


# Global instance
twitter_automation = TwitterAutomation()
