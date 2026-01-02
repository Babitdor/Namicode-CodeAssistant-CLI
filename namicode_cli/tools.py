"""Custom tools for the CLI agent.

This module provides additional tools beyond the filesystem and shell tools,
enabling the agent to interact with external services and the web:

Key Tools:
- http_request(): Make HTTP requests to APIs and web services
- fetch_url(): Fetch web pages and convert HTML to markdown
- web_search(): Search the web using Tavily API

These tools are registered with the agent and allow it to:
- Fetch data from REST APIs
- Scrape web content and convert to readable markdown
- Search for current information online
- Handle various HTTP methods (GET, POST, PUT, DELETE, etc.)

Dependencies:
- requests: HTTP client library
- markdownify: HTML to markdown conversion
- tavily: Web search API client

The Tavily client is initialized if TAVILY_API_KEY is available in settings.
"""

import difflib
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Literal

import requests
from markdownify import markdownify
from tavily import TavilyClient

from namicode_cli.config import settings

# Initialize Tavily client if API key is available
tavily_client = TavilyClient(api_key=settings.tavily_api_key) if settings.has_tavily else None


def http_request(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: str | dict | None = None,
    params: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Make HTTP requests to APIs and web services.

    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        headers: HTTP headers to include
        data: Request body data (string or dict)
        params: URL query parameters
        timeout: Request timeout in seconds

    Returns:
        Dictionary with response data including status, headers, and content
    """
    try:
        kwargs = {"url": url, "method": method.upper(), "timeout": timeout}

        if headers:
            kwargs["headers"] = headers
        if params:
            kwargs["params"] = params
        if data:
            if isinstance(data, dict):
                kwargs["json"] = data
            else:
                kwargs["data"] = data

        response = requests.request(**kwargs)

        try:
            content = response.json()
        except:
            content = response.text

        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": content,
            "url": response.url,
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status_code": 0,
            "headers": {},
            "content": f"Request timed out after {timeout} seconds",
            "url": url,
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": 0,
            "headers": {},
            "content": f"Request error: {e!s}",
            "url": url,
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "headers": {},
            "content": f"Error making request: {e!s}",
            "url": url,
        }


def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Search the web using Tavily for current information and documentation.

    This tool searches the web and returns relevant results. After receiving results,
    you MUST synthesize the information into a natural, helpful response for the user.

    Args:
        query: The search query (be specific and detailed)
        max_results: Number of results to return (default: 5)
        topic: Search topic type - "general" for most queries, "news" for current events
        include_raw_content: Include full page content (warning: uses more tokens)

    Returns:
        Dictionary containing:
        - results: List of search results, each with:
            - title: Page title
            - url: Page URL
            - content: Relevant excerpt from the page
            - score: Relevance score (0-1)
        - query: The original search query

    IMPORTANT: After using this tool:
    1. Read through the 'content' field of each result
    2. Extract relevant information that answers the user's question
    3. Synthesize this into a clear, natural language response
    4. Cite sources by mentioning the page titles or URLs
    5. NEVER show the raw JSON to the user - always provide a formatted response
    """
    if tavily_client is None:
        return {
            "error": "Tavily API key not configured. Please set TAVILY_API_KEY environment variable.",
            "query": query,
        }

    try:
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    except Exception as e:
        return {"error": f"Web search error: {e!s}", "query": query}


def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch content from a URL and convert HTML to markdown format.

    This tool fetches web page content and converts it to clean markdown text,
    making it easy to read and process HTML content. After receiving the markdown,
    you MUST synthesize the information into a natural, helpful response for the user.

    Args:
        url: The URL to fetch (must be a valid HTTP/HTTPS URL)
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Dictionary containing:
        - success: Whether the request succeeded
        - url: The final URL after redirects
        - markdown_content: The page content converted to markdown
        - status_code: HTTP status code
        - content_length: Length of the markdown content in characters

    IMPORTANT: After using this tool:
    1. Read through the markdown content
    2. Extract relevant information that answers the user's question
    3. Synthesize this into a clear, natural language response
    4. NEVER show the raw markdown to the user unless specifically requested
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DeepAgents/1.0)"},
        )
        response.raise_for_status()

        # Convert HTML content to markdown
        markdown_content = markdownify(response.text)

        return {
            "url": str(response.url),
            "markdown_content": markdown_content,
            "status_code": response.status_code,
            "content_length": len(markdown_content),
        }
    except Exception as e:
        return {"error": f"Fetch URL error: {e!s}", "url": url}


# def run_code(
#     code: str,
#     language: Literal["python", "javascript", "bash", "shell"] = "python",
#     timeout: int = 30,
# ) -> dict[str, Any]:
#     """Execute code snippets in a safe, isolated environment.

#     This tool runs code and returns the output, useful for testing snippets,
#     running scripts, or validating solutions.

#     Args:
#         code: The code to execute
#         language: Programming language ("python", "javascript", "bash", "shell")
#         timeout: Maximum execution time in seconds (default: 30)

#     Returns:
#         Dictionary containing:
#         - success: Whether execution succeeded
#         - output: Standard output from the code
#         - error: Standard error (if any)
#         - exit_code: Process exit code
#         - language: The language used

#     Examples:
#         # Python
#         run_code('print("Hello")', language="python")

#         # JavaScript/Node
#         run_code('console.log("Hello")', language="javascript")

#         # Shell
#         run_code('echo "Hello"', language="bash")
#     """
#     try:
#         # Create temporary file for code
#         suffix_map = {
#             "python": ".py",
#             "javascript": ".js",
#             "bash": ".sh",
#             "shell": ".sh",
#         }
#         suffix = suffix_map.get(language, ".txt")

#         with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
#             f.write(code)
#             temp_file = f.name

#         try:
#             # Determine command to run
#             if language == "python":
#                 cmd = ["python", temp_file]
#             elif language == "javascript":
#                 cmd = ["node", temp_file]
#             elif language in ["bash", "shell"]:
#                 cmd = ["bash", temp_file]
#             else:
#                 return {"error": f"Unsupported language: {language}", "success": False}

#             # Run the code
#             result = subprocess.run(
#                 cmd,
#                 capture_output=True,
#                 text=True,
#                 timeout=timeout,
#             )

#             return {
#                 "success": result.returncode == 0,
#                 "output": result.stdout,
#                 "error": result.stderr if result.stderr else None,
#                 "exit_code": result.returncode,
#                 "language": language,
#             }

#         finally:
#             # Clean up temp file
#             Path(temp_file).unlink(missing_ok=True)

#     except subprocess.TimeoutExpired:
#         return {
#             "success": False,
#             "error": f"Code execution timed out after {timeout} seconds",
#             "exit_code": -1,
#             "language": language,
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": f"Execution error: {e!s}",
#             "exit_code": -1,
#             "language": language,
#         }


# def file_diff(
#     file1_path: str,
#     file2_path: str,
#     context_lines: int = 3,
# ) -> dict[str, Any]:
#     """Compare two files and show their differences.

#     This tool generates a unified diff between two files, useful for reviewing
#     changes, comparing versions, or understanding modifications.

#     Args:
#         file1_path: Path to the first file (original)
#         file2_path: Path to the second file (modified)
#         context_lines: Number of context lines to show (default: 3)

#     Returns:
#         Dictionary containing:
#         - success: Whether comparison succeeded
#         - diff: Unified diff output
#         - files_identical: Whether files are identical
#         - file1: Path to first file
#         - file2: Path to second file
#         - changes: Number of changed lines

#     Examples:
#         file_diff("old_config.py", "new_config.py")
#         file_diff("v1/api.py", "v2/api.py", context_lines=5)
#     """
#     try:
#         file1 = Path(file1_path)
#         file2 = Path(file2_path)

#         if not file1.exists():
#             return {
#                 "success": False,
#                 "error": f"File not found: {file1_path}",
#                 "file1": file1_path,
#                 "file2": file2_path,
#             }

#         if not file2.exists():
#             return {
#                 "success": False,
#                 "error": f"File not found: {file2_path}",
#                 "file1": file1_path,
#                 "file2": file2_path,
#             }

#         # Read file contents
#         with file1.open() as f:
#             file1_lines = f.readlines()
#         with file2.open() as f:
#             file2_lines = f.readlines()

#         # Generate unified diff
#         diff_lines = list(
#             difflib.unified_diff(
#                 file1_lines,
#                 file2_lines,
#                 fromfile=file1_path,
#                 tofile=file2_path,
#                 n=context_lines,
#                 lineterm="",
#             )
#         )

#         files_identical = len(diff_lines) == 0

#         if files_identical:
#             return {
#                 "success": True,
#                 "files_identical": True,
#                 "diff": "(Files are identical)",
#                 "file1": file1_path,
#                 "file2": file2_path,
#                 "changes": 0,
#             }

#         diff_output = "\n".join(diff_lines)
#         change_count = sum(1 for line in diff_lines if line.startswith("+") or line.startswith("-"))

#         return {
#             "success": True,
#             "files_identical": False,
#             "diff": diff_output,
#             "file1": file1_path,
#             "file2": file2_path,
#             "changes": change_count,
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "error": f"Diff error: {e!s}",
#             "file1": file1_path,
#             "file2": file2_path,
#         }


# def git_command(
#     command: str,
#     directory: str = ".",
# ) -> dict[str, Any]:
#     """Execute git commands and return the output.

#     This tool runs git commands and captures their output, useful for checking
#     repository status, viewing history, or managing branches.

#     Args:
#         command: Git command to run (without 'git' prefix)
#                 Examples: "status", "log --oneline -10", "diff HEAD~1"
#         directory: Directory to run the command in (default: current directory)

#     Returns:
#         Dictionary containing:
#         - success: Whether command succeeded
#         - output: Command output
#         - error: Error message (if any)
#         - command: The full git command that was run

#     Examples:
#         git_command("status")
#         git_command("log --oneline -5")
#         git_command("diff main..feature-branch")
#         git_command("branch -a")

#     Common Commands:
#         - git_command("status") - Show working tree status
#         - git_command("log --oneline -10") - Show recent commit history
#         - git_command("diff") - Show unstaged changes
#         - git_command("diff --staged") - Show staged changes
#         - git_command("branch") - List branches
#         - git_command("show HEAD") - Show latest commit
#     """
#     try:
#         full_command = f"git {command}"

#         # Run git command
#         result = subprocess.run(
#             full_command,
#             shell=True,
#             capture_output=True,
#             text=True,
#             cwd=directory,
#             timeout=30,
#         )

#         return {
#             "success": result.returncode == 0,
#             "output": result.stdout,
#             "error": result.stderr if result.stderr else None,
#             "command": full_command,
#         }

#     except subprocess.TimeoutExpired:
#         return {
#             "success": False,
#             "error": "Git command timed out after 30 seconds",
#             "command": f"git {command}",
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": f"Git command error: {e!s}",
#             "command": f"git {command}",
#         }


# def tree_view(
#     directory: str = ".",
#     max_depth: int = 3,
#     include_hidden: bool = False,
#     pattern: str | None = None,
# ) -> dict[str, Any]:
#     """Display directory structure as a tree.

#     This tool shows the hierarchical structure of directories and files,
#     useful for understanding project layout and finding files.

#     Args:
#         directory: Root directory to start from (default: current directory)
#         max_depth: Maximum depth to traverse (default: 3, max: 5)
#         include_hidden: Include hidden files/directories (default: False)
#         pattern: Optional glob pattern to filter files (e.g., "*.py")

#     Returns:
#         Dictionary containing:
#         - success: Whether operation succeeded
#         - tree: Tree structure as formatted string
#         - total_dirs: Number of directories found
#         - total_files: Number of files found
#         - directory: Root directory path

#     Examples:
#         tree_view("src", max_depth=2)
#         tree_view(".", pattern="*.py")
#         tree_view("tests", include_hidden=True)
#     """
#     try:
#         root = Path(directory).resolve()

#         if not root.exists():
#             return {
#                 "success": False,
#                 "error": f"Directory not found: {directory}",
#                 "directory": directory,
#             }

#         if not root.is_dir():
#             return {
#                 "success": False,
#                 "error": f"Not a directory: {directory}",
#                 "directory": directory,
#             }

#         # Limit max depth to avoid overwhelming output
#         max_depth = min(max_depth, 5)

#         tree_lines = []
#         total_dirs = 0
#         total_files = 0

#         def build_tree(path: Path, prefix: str = "", depth: int = 0):
#             nonlocal total_dirs, total_files

#             if depth > max_depth:
#                 return

#             try:
#                 entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

#                 # Filter hidden files if needed
#                 if not include_hidden:
#                     entries = [e for e in entries if not e.name.startswith(".")]

#                 # Filter by pattern if specified
#                 if pattern:
#                     from fnmatch import fnmatch

#                     entries = [e for e in entries if e.is_dir() or fnmatch(e.name, pattern)]

#                 for i, entry in enumerate(entries):
#                     is_last = i == len(entries) - 1
#                     current_prefix = "└── " if is_last else "├── "
#                     next_prefix = "    " if is_last else "│   "

#                     if entry.is_dir():
#                         total_dirs += 1
#                         tree_lines.append(f"{prefix}{current_prefix}{entry.name}/")
#                         build_tree(entry, prefix + next_prefix, depth + 1)
#                     else:
#                         total_files += 1
#                         tree_lines.append(f"{prefix}{current_prefix}{entry.name}")

#             except PermissionError:
#                 tree_lines.append(f"{prefix}[Permission Denied]")

#         # Build tree starting from root
#         tree_lines.append(f"{root.name}/")
#         build_tree(root)

#         tree_output = "\n".join(tree_lines)

#         return {
#             "success": True,
#             "tree": tree_output,
#             "total_dirs": total_dirs,
#             "total_files": total_files,
#             "directory": str(root),
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "error": f"Tree view error: {e!s}",
#             "directory": directory,
#         }
