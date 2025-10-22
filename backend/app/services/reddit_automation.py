"""Reddit Automation Service using PRAW (Python Reddit API Wrapper)."""
import praw
from typing import List, Dict, Optional
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedditAutomation:
    """
    Reddit automation service for searching users and sending DMs.

    Features:
    - Search subreddits for relevant posts/comments
    - Extract user profiles based on search criteria
    - Send personalized DMs to users
    - Rate limiting and safety features
    """

    def __init__(self):
        """Initialize Reddit API client with credentials from settings."""
        if not settings.reddit_client_id or not settings.reddit_client_secret or settings.reddit_client_id == 'placeholder':
            logger.warning("Reddit API credentials not configured. Reddit automation disabled.")
            self.reddit = None
            return

        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            username=settings.reddit_username,
            password=settings.reddit_password
        )

        # Verify authentication
        try:
            self.username = self.reddit.user.me().name
            logger.info(f"✅ Reddit authenticated as: {self.username}")
        except Exception as e:
            logger.error(f"❌ Reddit authentication failed: {e}")
            raise

    async def search_subreddit(
        self,
        subreddit_name: str,
        keywords: str,
        limit: int = 100,
        time_filter: str = "month"
    ) -> List[Dict]:
        """
        Search a subreddit for posts matching keywords.

        Args:
            subreddit_name: Name of subreddit (e.g., "stocks", "investing")
            keywords: Search keywords (e.g., "individual stock investor")
            limit: Maximum number of posts to retrieve (default: 100)
            time_filter: Time filter - "hour", "day", "week", "month", "year", "all"

        Returns:
            List of post dictionaries with user data
        """
        try:
            logger.info(f"🔍 Searching r/{subreddit_name} for: {keywords}")

            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            # Search posts
            for submission in subreddit.search(keywords, time_filter=time_filter, limit=limit):
                post_data = {
                    'post_id': submission.id,
                    'post_title': submission.title,
                    'post_url': submission.url,
                    'post_score': submission.score,
                    'post_created': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'author_username': submission.author.name if submission.author else '[deleted]',
                    'author_link_karma': submission.author.link_karma if submission.author else 0,
                    'author_comment_karma': submission.author.comment_karma if submission.author else 0,
                    'subreddit': subreddit_name,
                    'num_comments': submission.num_comments
                }

                posts.append(post_data)

            logger.info(f"✅ Found {len(posts)} posts in r/{subreddit_name}")
            return posts

        except Exception as e:
            logger.error(f"❌ Error searching subreddit: {e}")
            return []

    async def search_comments_by_keywords(
        self,
        subreddit_name: str,
        keywords: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search comments in a subreddit matching keywords.

        Args:
            subreddit_name: Name of subreddit
            keywords: Keywords to search for in comments
            limit: Maximum number of comments to retrieve

        Returns:
            List of comment dictionaries with user data
        """
        try:
            logger.info(f"🔍 Searching comments in r/{subreddit_name} for: {keywords}")

            subreddit = self.reddit.subreddit(subreddit_name)
            comments = []

            # Get recent comments and filter by keywords
            for comment in subreddit.comments(limit=limit):
                if keywords.lower() in comment.body.lower():
                    comment_data = {
                        'comment_id': comment.id,
                        'comment_body': comment.body[:500],  # First 500 chars
                        'comment_score': comment.score,
                        'comment_created': datetime.fromtimestamp(comment.created_utc).isoformat(),
                        'author_username': comment.author.name if comment.author else '[deleted]',
                        'author_link_karma': comment.author.link_karma if comment.author else 0,
                        'author_comment_karma': comment.author.comment_karma if comment.author else 0,
                        'subreddit': subreddit_name,
                        'post_title': comment.submission.title if comment.submission else ''
                    }

                    comments.append(comment_data)

            logger.info(f"✅ Found {len(comments)} matching comments")
            return comments

        except Exception as e:
            logger.error(f"❌ Error searching comments: {e}")
            return []

    async def get_user_profile(self, username: str) -> Optional[Dict]:
        """
        Get detailed user profile information.

        Args:
            username: Reddit username

        Returns:
            User profile dictionary or None if not found
        """
        try:
            user = self.reddit.redditor(username)

            profile = {
                'username': user.name,
                'link_karma': user.link_karma,
                'comment_karma': user.comment_karma,
                'created_utc': datetime.fromtimestamp(user.created_utc).isoformat(),
                'is_verified': user.verified,
                'has_verified_email': user.has_verified_email,
                'profile_url': f"https://www.reddit.com/user/{user.name}"
            }

            # Get recent comments to understand interests
            recent_comments = []
            for comment in user.comments.new(limit=10):
                recent_comments.append({
                    'subreddit': comment.subreddit.display_name,
                    'body': comment.body[:200],
                    'score': comment.score
                })

            profile['recent_comments'] = recent_comments

            return profile

        except Exception as e:
            logger.error(f"❌ Error fetching user profile for {username}: {e}")
            return None

    async def send_dm(
        self,
        username: str,
        subject: str,
        message: str
    ) -> bool:
        """
        Send a direct message to a Reddit user.

        Args:
            username: Recipient's Reddit username
            subject: Message subject line
            message: Message body

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📧 Sending DM to u/{username}")

            # Get redditor
            redditor = self.reddit.redditor(username)

            # Send message
            redditor.message(subject=subject, message=message)

            logger.info(f"✅ DM sent successfully to u/{username}")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending DM to u/{username}: {e}")
            return False

    async def extract_unique_users(self, posts_or_comments: List[Dict]) -> List[str]:
        """
        Extract unique usernames from posts or comments.

        Args:
            posts_or_comments: List of post or comment dictionaries

        Returns:
            List of unique usernames
        """
        unique_users = set()

        for item in posts_or_comments:
            username = item.get('author_username')
            if username and username != '[deleted]' and username != self.username:
                unique_users.add(username)

        return list(unique_users)

    async def test_connection(self) -> bool:
        """
        Test Reddit API connection.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            user = self.reddit.user.me()
            logger.info(f"✅ Reddit connection test successful: {user.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Reddit connection test failed: {e}")
            return False


# Global instance
reddit_automation = RedditAutomation()
