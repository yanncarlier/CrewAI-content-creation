"""
CrewAI Tool for posting content to X (Twitter) using Tweepy.

This tool uses OAuth 1.0a User Context with Read + Write permissions.

To get your credentials:
1. Go to https://developer.x.com/en/portal/dashboard
2. Create a project and app
3. Under "Keys and tokens" tab, generate:
   - API Key (Consumer Key) -> X_API_KEY
   - API Key Secret (Consumer Secret) -> X_API_SECRET
   - Access Token -> X_ACCESS_TOKEN
   - Access Token Secret -> X_ACCESS_TOKEN_SECRET
4. Add these to your .env file

Environment Variables Required:
- X_API_KEY: Your X.com API Key (Consumer Key)
- X_API_SECRET: Your X.com API Key Secret (Consumer Secret)
- X_ACCESS_TOKEN: Your X.com Access Token
- X_ACCESS_TOKEN_SECRET: Your X.com Access Token Secret
"""

import os
from typing import Any, Optional
import tweepy
from crewai import _BaseTool


class PostToX(_BaseTool):
    """CrewAI tool for posting content to X (Twitter)."""

    name: str = "post_to_x"
    description: str = (
        "Posts text content to X (Twitter) using the authenticated user's account. "
        "Returns success message with tweet URL or error details. "
        "Requires environment variables: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET."
    )
    env_vars: list[dict] = [
        {"name": "X_API_KEY", "description": "X.com API Key (Consumer Key)"},
        {"name": "X_API_SECRET", "description": "X.com API Key Secret (Consumer Secret)"},
        {"name": "X_ACCESS_TOKEN", "description": "X.com Access Token"},
        {"name": "X_ACCESS_TOKEN_SECRET", "description": "X.com Access Token Secret"}
    ]

    def _get_client(self) -> Optional[tweepy.Client]:
        """Create and return a Tweepy client using OAuth 1.0a User Context."""
        try:
            # Get credentials from environment variables
            api_key = os.environ.get("X_API_KEY")
            api_secret = os.environ.get("X_API_SECRET")
            access_token = os.environ.get("X_ACCESS_TOKEN")
            access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

            if not all([api_key, api_secret, access_token, access_token_secret]):
                missing = []
                if not api_key:
                    missing.append("X_API_KEY")
                if not api_secret:
                    missing.append("X_API_SECRET")
                if not access_token:
                    missing.append("X_ACCESS_TOKEN")
                if not access_token_secret:
                    missing.append("X_ACCESS_TOKEN_SECRET")
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

            # Create OAuth 1.0a User Context client
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            return client

        except Exception as e:
            raise RuntimeError(f"Failed to create X.com client: {str(e)}")

    def _run(self, content: str) -> str:
        """
        Post content to X (Twitter).

        Args:
            content: The text content to post. Will be truncated to 280 characters if needed.

        Returns:
            str: Success message with tweet URL or error message.
        """
        try:
            # Validate content
            if not content or not isinstance(content, str):
                return "Error: Content must be a non-empty string."

            # Truncate to 280 characters (X's limit for regular tweets)
            content = content.strip()
            if len(content) > 280:
                content = content[:277] + "..."

            # Get authenticated client
            client = self._get_client()

            # Post the tweet
            response = client.create_tweet(text=content)

            if response and hasattr(response, 'data') and response.data:
                tweet_id = response.data.get('id')
                tweet_text = response.data.get('text', content)
                tweet_url = f"https://x.com/i/web/status/{tweet_id}"
                return f"Successfully posted to X! Tweet URL: {tweet_url}"
            else:
                return "Error: Unexpected response from X API. Tweet may not have been posted."

        except tweepy.TweepyException as e:
            error_msg = str(e)
            if "Unauthorized" in error_msg or "401" in error_msg:
                return "Error: Authentication failed. Please check your X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, and X_ACCESS_TOKEN_SECRET."
            elif "Forbidden" in error_msg or "403" in error_msg:
                return "Error: Permission denied. Ensure your app has Read + Write permissions."
            elif "Bad Request" in error_msg or "400" in error_msg:
                return f"Error: Invalid request. Details: {error_msg}"
            else:
                return f"Error: X API error: {error_msg}"

        except ValueError as e:
            return f"Error: {str(e)}"

        except Exception as e:
            return f"Error: Failed to post to X: {str(e)}"


# Create an instance for CrewAI to use
post_to_x_tool = PostToX()
