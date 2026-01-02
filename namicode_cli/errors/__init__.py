"""Error handling and recovery system for deepagents CLI."""

from namicode_cli.errors.handlers import ErrorHandler, RecoveryResult
from namicode_cli.errors.taxonomy import ErrorCategory, RecoverableError

__all__ = ["ErrorHandler", "RecoveryResult", "ErrorCategory", "RecoverableError"]
