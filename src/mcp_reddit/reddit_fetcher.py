"""
Reddit Content API - Provides MCP tools for accessing and analyzing Reddit content
"""
import sys
import logging
import os
import importlib
from typing import Any, Dict, List, Optional, Union

import praw  # type: ignore
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from redditwarp.ASYNC import Client
from redditwarp.models.submission_ASYNC import GalleryPost, LinkPost, TextPost

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize MCP and Reddit clients (lectura)
mcp = FastMCP("Reddit Content API")
reddit_client = Client()

# Initialize authenticated Reddit client for posting (escritura)
authenticated_reddit = None 
try:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    refresh_token = os.getenv("REDDIT_REFRESH_TOKEN")
    
    if not client_id or not client_secret:
        logger.error("REDDIT_CLIENT_ID o REDDIT_CLIENT_SECRET no están configurados. Las funciones de escritura no estarán disponibles.")
    elif not refresh_token:
        logger.warning("REDDIT_REFRESH_TOKEN no configurado. Funciones de escritura no disponibles.")
        logger.warning("Ejecuta 'python -m mcp_reddit.auth_helper' para obtener un token de actualización.")
    else:
        logger.info("Attempting to initialize authenticated PRAW client...")
        authenticated_reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            user_agent="Reddit Content API:v0.1.0 (by u/jlcases-dev)",
        )
        try:
            logger.info("Verifying PRAW authentication...")
            user = authenticated_reddit.user.me()
            if user:
                logger.info(f"Successfully authenticated Reddit client as user: {user.name}")
            else:
                logger.error("Authenticated Reddit client, but could not retrieve user information.")
                authenticated_reddit = None 
        except Exception as auth_exc:
            logger.error(f"Failed to verify Reddit authentication after initialization: {auth_exc}", exc_info=True)
            authenticated_reddit = None 
            
except Exception as e:
    logger.error(f"Critical error during authenticated Reddit client PRAW initialization: {e}", exc_info=True)
    authenticated_reddit = None 

logger.info(f"Authenticated PRAW client initialized: {authenticated_reddit is not None}")

class ContentFormatters:
    """Helper class for formatting Reddit content"""
    
    @staticmethod
    def determine_content_type(submission: Any) -> str:
        if isinstance(submission, LinkPost):
            return 'external_link'
        elif isinstance(submission, TextPost):
            return 'text_post'
        elif isinstance(submission, GalleryPost):
            return 'image_gallery'
        return 'other'
    
    @staticmethod
    def extract_content_body(submission: Any) -> Optional[str]:
        if isinstance(submission, LinkPost):
            return f"External link: {submission.permalink}"
        elif isinstance(submission, TextPost):
            return submission.body or "No text content available"
        elif isinstance(submission, GalleryPost):
            return f"Gallery with multiple images: {submission.gallery_link}"
        return None
    
    @staticmethod
    def format_nested_comments(comment_tree_node: Any, level: int = 0) -> str:
        comment = comment_tree_node.value
        indent = "  " * level + "└─ " if level > 0 else ""
        formatted = (
            f"{indent}Comment by {comment.author_display_name or '[anonymous]'} "
            f"(votes: {comment.score})\n"
            f"{indent}{'  ' if level > 0 else ''}{comment.body}\n"
        )
        if comment_tree_node.children:
            for child in comment_tree_node.children:
                formatted += ContentFormatters.format_nested_comments(child, level + 1)
        return formatted

# Herramienta 1 - Hot Threads
@mcp.tool(name="fetch_reddit_hot_threads")
async def get_trending_posts(community: str, count: int = 10) -> str:
    """
    Retrieve trending posts from a specific Reddit community
    
    Args:
        community: The Reddit community/subreddit name
        count: Maximum number of posts to retrieve (default: 10)
        
    Returns:
        Formatted string with trending posts information
    """
    logger.info(f"Fetching {count} hot threads from r/{community}")
    try:
        results = []
        async for post in reddit_client.p.subreddit.pull.hot(community, count):
            post_type = ContentFormatters.determine_content_type(post)
            post_content = ContentFormatters.extract_content_body(post)
            post_details = [
                f"## {post.title}",
                f"* Upvotes: {post.score}",
                f"* Comments: {post.comment_count}",
                f"* Author: u/{post.author_display_name or '[deleted]'}",
                f"* Type: {post_type}",
                f"* Content: {post_content}",
                f"* Link: https://reddit.com{post.permalink}",
                "---"
            ]
            results.append("\n".join(post_details))
        if not results:
            return f"No trending posts found in r/{community}"
        return "\n\n".join(results)
    except Exception as e:
        error_msg = f"Failed to retrieve trending posts: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg
mcp.tool(name="mcp_reddit_content_api_fetch_reddit_hot_threads")(get_trending_posts)

# Herramienta 2 - Post Content
@mcp.tool(name="fetch_reddit_post_content")
async def analyze_reddit_discussion(thread_id: str, max_comments: int = 20, 
                                  comment_tree_depth: int = 3) -> str:
    """
    Analyze a specific Reddit discussion thread with comments
    
    Args:
        thread_id: The Reddit post identifier
        max_comments: Maximum number of top-level comments to include (default: 20)
        comment_tree_depth: How deep to traverse the comment tree (default: 3)
        
    Returns:
        Detailed analysis of the post and its discussion
    """
    logger.info(f"Fetching content for post {thread_id} (comments: {max_comments}, depth: {comment_tree_depth})")
    try:
        post = await reddit_client.p.submission.fetch(thread_id)
        post_type = ContentFormatters.determine_content_type(post)
        post_content = ContentFormatters.extract_content_body(post)
        post_analysis = [
            f"# Discussion Analysis: {post.title}",
            f"* Upvotes: {post.score}",
            f"* Author: u/{post.author_display_name or '[deleted]'}",
            f"* Content type: {post_type}",
            f"* Content: {post_content}",
            "\n## Discussion Overview"
        ]
        discussion = await reddit_client.p.comment_tree.fetch(
            thread_id, 
            sort='top', 
            limit=max_comments, 
            depth=comment_tree_depth
        )
        if discussion.children:
            post_analysis.append("### Top Comments:")
            for comment_node in discussion.children:
                post_analysis.append(ContentFormatters.format_nested_comments(comment_node))
        else:
            post_analysis.append("No comments found in this discussion.")
        return "\n".join(post_analysis)
    except Exception as e:
        error_msg = f"Failed to analyze discussion: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg
mcp.tool(name="mcp_reddit_content_api_fetch_reddit_post_content")(analyze_reddit_discussion)

# Herramienta 3 - Create Post
@mcp.tool(name="create_reddit_post")
def create_reddit_post(subreddit: str, title: str, content_type: str = "text", 
                      content: str = "", url: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """
    Create a new post on a subreddit
    
    Args:
        subreddit: Name of the subreddit to post to
        title: Title of the post
        content_type: Type of post to create ("text", "link")
        content: Text content for text posts
        url: URL for link posts
        ctx: MCP context object (automatically provided)
        
    Returns:
        URL of the created post or error message
    """
    if ctx:
        ctx.info(f"Attempting to create a {content_type} post in r/{subreddit}")
    if not authenticated_reddit:
        return "Cannot create post: Reddit authentication is not configured properly or failed to initialize."
    try:
        if not authenticated_reddit.user or not authenticated_reddit.user.me():
             return "Cannot create post: Reddit client is not authenticated. Please check credentials or run auth_helper."
        target_subreddit = authenticated_reddit.subreddit(subreddit)
        if content_type.lower() == "text":
            submission = target_subreddit.submit(title=title, selftext=content)
        elif content_type.lower() == "link":
            if not url:
                return "Cannot create link post: URL is required"
            submission = target_subreddit.submit(title=title, url=url)
        else:
            return f"Unsupported content type: {content_type}. Supported types are 'text' and 'link'"
        post_url = f"https://reddit.com{submission.permalink}"
        if ctx:
            ctx.info(f"Successfully created post: {post_url}")
        return f"Post created successfully: {post_url}"
    except Exception as e:
        logger.error(f"Error during post creation: {e}", exc_info=True) 
        return f"Failed to create Reddit post: {str(e)}"
mcp.tool(name="mcp_reddit_content_api_create_reddit_post")(create_reddit_post)

# Herramienta 4 - Add Comment
@mcp.tool(name="add_reddit_comment")
def add_reddit_comment(post_id: str = "", comment_text: str = "", 
                     reply_to_comment_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """
    Add a comment to a Reddit post or reply to an existing comment
    
    Args:
        post_id: ID of the Reddit post to comment on (required unless replying to a comment)
        comment_text: Content of the comment
        reply_to_comment_id: ID of the comment to reply to (optional)
        ctx: MCP context object (automatically provided)
        
    Returns:
        URL of the created comment or error message
    """
    if ctx:
        action = f"reply to comment {reply_to_comment_id}" if reply_to_comment_id else f"comment on post {post_id}"
        ctx.info(f"Attempting to {action}")
    if not authenticated_reddit:
        return "Cannot add comment: Reddit authentication is not configured properly or failed to initialize."
    try:
        if not authenticated_reddit.user or not authenticated_reddit.user.me():
             return "Cannot add comment: Reddit client is not authenticated. Please check credentials or run auth_helper."
        if reply_to_comment_id:
            target_comment = authenticated_reddit.comment(reply_to_comment_id)
            new_comment = target_comment.reply(comment_text)
            comment_url = f"https://reddit.com{new_comment.permalink}"
            if ctx:
                ctx.info(f"Successfully replied to comment: {comment_url}")
            return f"Comment reply created successfully: {comment_url}"
        elif post_id:
            submission = authenticated_reddit.submission(id=post_id)
            new_comment = submission.reply(comment_text)
            comment_url = f"https://reddit.com{new_comment.permalink}"
            if ctx:
                ctx.info(f"Successfully commented on post: {comment_url}")
            return f"Comment created successfully: {comment_url}"
        else:
             return "Error: Must provide either post_id or reply_to_comment_id"
    except Exception as e:
        logger.error(f"Error during comment creation: {e}", exc_info=True)
        return f"Failed to create Reddit comment: {str(e)}"
mcp.tool(name="mcp_reddit_content_api_add_reddit_comment")(add_reddit_comment)

# Herramienta 5 - Vote
@mcp.tool(name="vote_on_reddit_content")
def vote_on_reddit_content(content_id: str = "", vote_direction: str = "", content_type: str = "post", ctx: Optional[Context] = None) -> str:
    """
    Vote on a Reddit post or comment
    
    Args:
        content_id: ID of the Reddit post or comment to vote on
        vote_direction: Direction of vote ("up", "down", or "neutral")
        content_type: Type of content to vote on ("post" or "comment")
        ctx: MCP context object (automatically provided)
        
    Returns:
        Status message confirming vote action
    """
    if ctx:
        ctx.info(f"Attempting to {vote_direction}vote on {content_type} {content_id}")
    if not authenticated_reddit:
        return "Cannot vote: Reddit authentication is not configured properly or failed to initialize."
    try:
        if not authenticated_reddit.user or not authenticated_reddit.user.me():
             return "Cannot vote: Reddit client is not authenticated. Please check credentials or run auth_helper."
        if content_type.lower() == "post":
            target = authenticated_reddit.submission(id=content_id)
        elif content_type.lower() == "comment":
            target = authenticated_reddit.comment(id=content_id)
        else:
            return f"Unsupported content type: {content_type}. Supported types are 'post' and 'comment'"
        if vote_direction.lower() == "up":
            target.upvote()
            status = "upvoted"
        elif vote_direction.lower() == "down":
            target.downvote()
            status = "downvoted"
        elif vote_direction.lower() == "neutral":
            target.clear_vote()
            status = "vote cleared"
        else:
            return f"Unsupported vote direction: {vote_direction}. Supported directions are 'up', 'down', and 'neutral'"
        if ctx:
            ctx.info(f"Successfully {status} {content_type}: {content_id}")
        return f"Successfully {status} the {content_type}"
    except Exception as e:
        logger.error(f"Error during voting: {e}", exc_info=True)
        return f"Failed to vote on Reddit content: {str(e)}"
mcp.tool(name="mcp_reddit_content_api_vote_on_reddit_content")(vote_on_reddit_content)

logger.info("Finished loading reddit_fetcher.py")