"""
Main entry point for the Reddit Content API
"""
import logging
import sys

from mcp_reddit.reddit_fetcher import mcp, get_trending_posts, analyze_reddit_discussion, create_reddit_post, add_reddit_comment, vote_on_reddit_content

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Reddit Content API server...")
    logger.info("Available tools should include:")
    logger.info("1. fetch_reddit_hot_threads (alias for get_trending_posts)")
    logger.info("2. fetch_reddit_post_content (alias for analyze_reddit_discussion)")
    logger.info("3. create_reddit_post")
    logger.info("4. add_reddit_comment")
    logger.info("5. vote_on_reddit_content")
    
    try:
        # Start the server
        logger.info("Running MCP server...")
        mcp.run()
        logger.info("Server running. Press Ctrl+C to stop.")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1) 