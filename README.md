# Reddit Content API - Setup and Usage Guide

[![GitHub stars](https://img.shields.io/github/stars/jlcases/mcp-reddit?style=social)](https://github.com/jlcases/mcp-reddit/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/jlcases/mcp-reddit?style=social)](https://github.com/jlcases/mcp-reddit/network/members)

This project provides MCP (Model Context Protocol) tools for interacting with Reddit through Claude and Cursor.

## Features

- Reading trending posts from subreddits
- Analyzing Reddit discussions with comments
- Creating posts on Reddit
- Adding comments to posts or replies to existing comments
- Voting on posts and comments

## Requirements

- Python 3.10+
- A Reddit account
- A registered Reddit application (to obtain client_id and client_secret)
- Virtual environment (venv or similar)
- Claude Desktop and/or Cursor (optional but recommended)

## Installation from Scratch

Follow these steps carefully to avoid import and configuration issues:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mcp-reddit.git
cd mcp-reddit

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies (WITHOUT installing the package in editable mode)
pip install -r requirements.txt

# 4. Configure environment variables (see below)
# Create and edit the .env file
```

> ⚠️ **IMPORTANT**: DO NOT install the package in editable mode (`pip install -e .`) 
> as it can cause module import problems.

## Environment Configuration

1. Create a `.env` file in the project root with the following variables:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_REFRESH_TOKEN=your_refresh_token
```

2. To obtain a refresh token, run:

```bash
python -m mcp_reddit.auth_helper
```

Follow the instructions to authorize the application. The token will be automatically saved to the `.env` file.

## Project Structure

```
mcp-reddit/
│
├── src/
│   └── mcp_reddit/
│       ├── __init__.py
│       ├── main.py           # Entry point for the MCP server
│       ├── reddit_fetcher.py # Implementation of Reddit tools
│       └── auth_helper.py    # Helper for generating authentication tokens
│
├── .env                      # Environment variables (create manually)
├── requirements.txt
├── setup.py
└── README.md
```

## Running the Server Directly

To run manually (useful for development and testing):

```bash
cd /path/to/mcp-reddit
.venv/bin/python src/mcp_reddit/main.py
```

You should see logs indicating:
- Server initialization
- Reddit authentication verification
- Registration of 10 tools (5 original + 5 with prefix)
- "Running MCP server..."

## Claude Desktop Configuration

1. Locate the configuration file:
   - On macOS: `/Users/your-username/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the configuration for reddit-content-api:

```json
"reddit-content-api": {
  "command": "/full/path/to/mcp-reddit/.venv/bin/python",
  "args": [
    "-m",
    "mcp_reddit.main",
    "--stdio"
  ],
  "cwd": "/full/path/to/mcp-reddit",
  "env": {
    "PYTHONPATH": "/full/path/to/mcp-reddit/src:/full/path/to/mcp-reddit",
    "DEBUG": "true"
  }
}
```

> ⚠️ **EXTREMELY IMPORTANT**: `PYTHONPATH` must include both the `src` directory and the project root, in that order, separated by `:` (on Unix/macOS) or `;` (on Windows)

## Cursor Configuration

1. Locate the configuration file:
   - On macOS: `/Users/your-username/.cursor/mcp.json`
   - On Windows: `%USERPROFILE%\.cursor\mcp.json`

2. Add the same configuration as in Claude, adjusting paths as necessary.

## Troubleshooting Common Issues

### Issue: Only 2 tools appear instead of the expected 10

**Symptoms**: When running the server, only 2 tools appear instead of the expected 10.

**Possible causes and solutions**:

1. **Import problem**: Python is importing an installed version from `site-packages` instead of the local code in `src/`.

   **Solution**: 
   - Make sure NOT to install the package in editable mode (`pip install -e .`)
   - Explicitly add `src` to the beginning of `PYTHONPATH` in the configurations
   - If you've already installed it, use `pip uninstall reddit-content-api` to remove it

2. **Python cache**: Old `.pyc` files can cause problems.

   **Solution**:
   - Remove all `__pycache__` directories from the project

3. **Version conflicts**: Different versions of the same library.

   **Solution**:
   - Reinstall dependencies with `pip install -r requirements.txt`

### Issue: "Cannot create post: Reddit authentication is not configured properly"

**Cause**: The refresh token is invalid or has expired.

**Solution**: Regenerate the token by running `python -m mcp_reddit.auth_helper` and make sure it's saved in `.env`.

### Issue: Tools don't appear in Claude/Cursor

**Cause**: Incorrect configuration in the configuration files.

**Solution**: 
- Check paths and especially `PYTHONPATH` in the configuration files
- Completely restart Claude/Cursor after modifying the configuration

## Using the Tools in Claude/Cursor

Once configured, you can use the following tools:

1. `mcp_reddit_content_api_fetch_reddit_hot_threads` - Get trending posts
2. `mcp_reddit_content_api_fetch_reddit_post_content` - Analyze a post and its comments
3. `mcp_reddit_content_api_create_reddit_post` - Create a new post
4. `mcp_reddit_content_api_add_reddit_comment` - Add a comment
5. `mcp_reddit_content_api_vote_on_reddit_content` - Vote on content

### Examples

**Getting trending posts**:
```
Subreddit: python
Number of posts: 5
```

**Creating a post**:
```
Subreddit: test
Title: Test from MCP
Content type: text
Content: This is a test from the Reddit Content API using MCP.
```

## Contributions

If you find issues or have improvements, please create an issue or submit a pull request.

## License

[MIT](LICENSE)

## Support This Project

If you find this project useful in your work or research, please consider:

- ⭐ Starring the repository to show your support
- 🔄 Following the repository for updates on new features and improvements
- 🐛 Opening issues for bugs or feature requests
- 🛠️ Contributing with pull requests if you have improvements to share

Your support helps make this project better for everyone!