"""Error handling and recovery strategies for deepagents CLI."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from namicode_cli.errors.taxonomy import ErrorCategory, RecoverableError


@dataclass
class RecoveryResult:
    """Result of error recovery attempt.

    Attributes:
        success: Whether recovery was successful
        message: Human-readable message about the recovery attempt
        suggestion: Optional suggestion for user action
        new_state: Optional new state to merge into context
    """

    success: bool
    message: str
    suggestion: str | None = None
    new_state: dict | None = None


class ErrorRecoveryStrategy(Protocol):
    """Protocol for error recovery strategies."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this strategy can handle the error.

        Args:
            error: The recoverable error to check

        Returns:
            True if this strategy can handle the error
        """
        ...

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Attempt to recover from the error.

        Args:
            error: The recoverable error to recover from

        Returns:
            Result of the recovery attempt
        """
        ...


class FileNotFoundRecovery:
    """Recover from file not found errors by searching."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this is a file not found error."""
        return error.category == ErrorCategory.FILE_NOT_FOUND

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Suggest searching for the file using glob.

        Args:
            error: The file not found error

        Returns:
            Recovery result with search suggestion
        """
        file_name = error.context.get("file_name", "")
        if not file_name:
            return RecoveryResult(
                success=False,
                message=f"File not found: {file_name}",
                suggestion="Please check the file path and try again.",
            )

        # Extract just the filename without path
        base_name = Path(file_name).name

        # Suggest searching for similar files
        suggestion = (
            f"I couldn't find '{file_name}'. "
            f"Let me search for similar files: `glob('**/*{base_name}')`\n"
            "If you know the correct path, please provide it."
        )

        return RecoveryResult(
            success=False,
            message=f"File not found: {file_name}",
            suggestion=suggestion,
            new_state={"search_pattern": f"**/*{base_name}"},
        )


class ContextOverflowRecovery:
    """Recover from context overflow by suggesting summarization."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this is a context overflow error."""
        return error.category == ErrorCategory.CONTEXT_OVERFLOW

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Suggest summarization and memory storage.

        Args:
            error: The context overflow error

        Returns:
            Recovery result with context management suggestions
        """
        return RecoveryResult(
            success=False,
            message="Context limit approaching or exceeded.",
            suggestion=(
                "The conversation context is getting too large. I can:\n"
                "1. Summarize our progress and save to memory\n"
                "2. Focus on a specific area of the codebase\n"
                "3. Use pagination (read_file with limit) instead of full reads\n\n"
                "What would you like me to do?"
            ),
        )


class NetworkErrorRecovery:
    """Recover from network errors with exponential backoff retry."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this is a network error."""
        return error.category == ErrorCategory.NETWORK_ERROR

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Implement exponential backoff retry.

        Args:
            error: The network error

        Returns:
            Recovery result indicating retry status
        """
        retry_count = error.context.get("retry_count", 0)
        max_retries = 3

        if retry_count >= max_retries:
            return RecoveryResult(
                success=False,
                message=f"Network error after {max_retries} retries: {error.original_error}",
                suggestion="Please check your internet connection and try again.",
            )

        # Exponential backoff: 1s, 2s, 4s
        wait_time = 2**retry_count
        await asyncio.sleep(wait_time)

        return RecoveryResult(
            success=True,  # Indicate retry is possible
            message=f"Network error, retrying in {wait_time}s... (attempt {retry_count + 1}/{max_retries})",
            new_state={"retry_count": retry_count + 1},
        )


class PermissionDeniedRecovery:
    """Recover from permission denied errors."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this is a permission denied error."""
        return error.category == ErrorCategory.PERMISSION_DENIED

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Suggest checking and fixing permissions.

        Args:
            error: The permission denied error

        Returns:
            Recovery result with permission fix suggestions
        """
        file_path = error.context.get("file_path", "")

        suggestion = (
            f"Permission denied for: {file_path}\n\n"
            "To fix this, you may need to:\n"
            "1. Check file permissions: `ls -la {file_path}`\n"
            "2. Make file executable: `chmod +x {file_path}`\n"
            "3. Change ownership if needed: `sudo chown $USER {file_path}`"
        )

        return RecoveryResult(
            success=False,
            message=f"Permission denied: {file_path}",
            suggestion=suggestion,
        )


class CommandNotFoundRecovery:
    """Recover from command not found errors."""

    def can_handle(self, error: RecoverableError) -> bool:
        """Check if this is a command not found error."""
        return error.category == ErrorCategory.COMMAND_NOT_FOUND

    async def recover(self, error: RecoverableError) -> RecoveryResult:
        """Suggest installing the missing command.

        Args:
            error: The command not found error

        Returns:
            Recovery result with installation suggestions
        """
        command = error.context.get("command", "")

        suggestion = (
            f"Command not found: {command}\n\n"
            "To fix this, you may need to:\n"
            "1. Check if package is installed: `which {command}`\n"
            "2. Install the package (examples):\n"
            "   - Python: `pip install {command}`\n"
            "   - Node: `npm install -g {command}`\n"
            "   - System: `sudo apt install {command}` or `brew install {command}`"
        )

        return RecoveryResult(
            success=False,
            message=f"Command not found: {command}",
            suggestion=suggestion,
        )


class ErrorHandler:
    """Central error handler with recovery strategies.

    This class provides error classification and recovery for common
    error scenarios in the deepagents CLI.
    """

    def __init__(self):
        """Initialize error handler with all recovery strategies."""
        self.strategies: list[ErrorRecoveryStrategy] = [
            FileNotFoundRecovery(),
            ContextOverflowRecovery(),
            NetworkErrorRecovery(),
            PermissionDeniedRecovery(),
            CommandNotFoundRecovery(),
        ]

    def classify_error(self, error: Exception, context: dict | None = None) -> RecoverableError:
        """Classify an error into a category.

        Args:
            error: The exception to classify
            context: Optional additional context about the error

        Returns:
            RecoverableError with classification and recovery info
        """
        context = context or {}

        error_str = str(error).lower()

        # File errors
        if "no such file" in error_str or "file not found" in error_str:
            return RecoverableError(
                category=ErrorCategory.FILE_NOT_FOUND,
                original_error=error,
                context=context,
                recovery_suggestion="Search for the file using glob or check the path",
                user_message=f"File not found: {context.get('file_name', 'unknown')}",
            )

        # Permission errors
        if "permission denied" in error_str or "access denied" in error_str:
            return RecoverableError(
                category=ErrorCategory.PERMISSION_DENIED,
                original_error=error,
                context=context,
                recovery_suggestion="Check file permissions with `ls -la`",
                user_message="Permission denied. You may need to change file permissions.",
            )

        # Command not found errors
        if "command not found" in error_str or "not recognized" in error_str:
            return RecoverableError(
                category=ErrorCategory.COMMAND_NOT_FOUND,
                original_error=error,
                context=context,
                recovery_suggestion="Check if the command is installed",
                user_message=f"Command not found: {context.get('command', 'unknown')}",
            )

        # Network errors
        if any(x in error_str for x in ["timeout", "connection", "network", "unreachable"]):
            return RecoverableError(
                category=ErrorCategory.NETWORK_ERROR,
                original_error=error,
                context=context,
                recovery_suggestion="Retry with exponential backoff",
                user_message="Network error occurred. Retrying...",
            )

        # Context overflow
        if "context" in error_str and ("limit" in error_str or "too large" in error_str):
            return RecoverableError(
                category=ErrorCategory.CONTEXT_OVERFLOW,
                original_error=error,
                context=context,
                recovery_suggestion="Summarize and use pagination",
                user_message="Context limit reached. Need to summarize or narrow scope.",
            )

        # Syntax errors
        if "syntax" in error_str or "invalid syntax" in error_str:
            return RecoverableError(
                category=ErrorCategory.SYNTAX_ERROR,
                original_error=error,
                context=context,
                recovery_suggestion="Check code syntax and fix issues",
                user_message=f"Syntax error: {error}",
            )

        # Generic tool error
        return RecoverableError(
            category=ErrorCategory.TOOL_ERROR,
            original_error=error,
            context=context,
            recovery_suggestion="Check the error message and try a different approach",
            user_message=f"Tool error: {error}",
        )

    async def handle(self, error: Exception, context: dict | None = None) -> RecoveryResult:
        """Handle error with appropriate recovery strategy.

        Args:
            error: The exception to handle
            context: Optional additional context about the error

        Returns:
            Result of the recovery attempt
        """
        classified = self.classify_error(error, context)

        # Try recovery strategies
        for strategy in self.strategies:
            if strategy.can_handle(classified):
                result = await strategy.recover(classified)
                if result.success or not classified.retry_allowed:
                    return result

        # No recovery strategy worked - surface to user
        return RecoveryResult(
            success=False,
            message=classified.user_message,
            suggestion=classified.recovery_suggestion,
        )
