#!/usr/bin/env python3
"""
Security Validator for MCP Server

Provides input validation and path traversal protection including:
- Project name validation
- File path validation and traversal prevention
- Symlink resolution safety
- Input size limits
- Parameter validation
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger('security_validator')


class SecurityValidator:
    """Validate inputs and prevent security vulnerabilities"""

    # Size limits (in bytes)
    MAX_QUERY_SIZE = 500  # 500 characters for queries
    MAX_PROJECT_NAME_SIZE = 100  # 100 characters
    MAX_RESULTS_SIZE = 10 * 1024 * 1024  # 10MB for results
    MAX_FILE_PATH_SIZE = 260  # Windows MAX_PATH
    MAX_TAGS_SIZE = 1000  # Total size of tags

    # Valid characters for project names (alphanumeric, dash, underscore)
    VALID_PROJECT_CHARS = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    )

    def __init__(self, base_projects_dir: str = r'D:\models\projects'):
        """Initialize validator with base directory"""
        self.base_projects_dir = Path(base_projects_dir).resolve()
        logger.info(f"SecurityValidator initialized with base: {self.base_projects_dir}")

    def validate_project_name(self, project_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate project name

        Args:
            project_name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not project_name:
            return False, "Project name cannot be empty"

        if not isinstance(project_name, str):
            return False, "Project name must be a string"

        # Check size
        if len(project_name) > self.MAX_PROJECT_NAME_SIZE:
            return False, f"Project name exceeds maximum length"

        # Check for path traversal attempts
        if '..' in project_name:
            return False, "Project name contains invalid characters"

        if '/' in project_name or '\\' in project_name:
            return False, "Project name contains invalid characters"

        # Check for absolute paths
        if project_name.startswith('/') or (len(project_name) > 1 and project_name[1] == ':'):
            return False, "Project name contains invalid characters"

        # Check for hidden files
        if project_name.startswith('.'):
            return False, "Project name contains invalid characters"

        # Check character whitelist
        if not all(c in self.VALID_PROJECT_CHARS for c in project_name):
            return False, "Project name contains invalid characters"

        return True, None

    def validate_file_path(self, file_path: str,
                          allowed_base_dir: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate file path and prevent traversal attacks

        Args:
            file_path: Path to validate
            allowed_base_dir: Base directory path must stay within (default: system temp)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path cannot be empty"

        if not isinstance(file_path, str):
            return False, "File path must be a string"

        # Check size
        if len(file_path) > self.MAX_FILE_PATH_SIZE:
            return False, "File path exceeds maximum length"

        try:
            # Convert to Path object and resolve (resolves .. and symlinks)
            path = Path(file_path).resolve()

            # Determine allowed base directory
            if allowed_base_dir:
                base_dir = Path(allowed_base_dir).resolve()
            else:
                # Default to system temp directory for safety
                base_dir = Path(os.environ.get('TEMP', '/tmp')).resolve()

            # Check if resolved path is within allowed directory
            try:
                path.relative_to(base_dir)
            except ValueError:
                # Path is not under base directory
                return False, "Access to this path is not permitted"

            # Check if path exists and is readable (after resolution)
            # Don't follow symlinks further
            if path.exists():
                # Path exists, it's safe
                return True, None
            else:
                # Path doesn't exist - this may be intentional, allow for creation
                # but parent must be valid
                parent = path.parent
                if parent.exists() and parent.is_dir():
                    return True, None
                else:
                    return False, "Invalid file path"

        except (OSError, ValueError) as e:
            # Path resolution failed
            logger.warning(f"File path validation failed: {str(e)}")
            return False, "Invalid file path"

    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate search query

        Args:
            query: Query string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if query is None:
            return False, "Query cannot be null"

        if not isinstance(query, str):
            return False, "Query must be a string"

        if len(query) == 0:
            return False, "Query cannot be empty"

        if len(query) > self.MAX_QUERY_SIZE:
            return False, "Query exceeds maximum length"

        return True, None

    def validate_results_size(self, results) -> Tuple[bool, Optional[str]]:
        """
        Validate results don't exceed size limit

        Args:
            results: Results object to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        import json

        if results is None:
            return False, "Results cannot be null"

        try:
            # Estimate size by JSON serialization
            results_json = json.dumps(results)
            size = len(results_json.encode('utf-8'))

            if size > self.MAX_RESULTS_SIZE:
                return False, "Results exceed maximum size"

            return True, None
        except (TypeError, ValueError) as e:
            logger.warning(f"Results validation failed: {str(e)}")
            return False, "Results are not JSON serializable"

    def validate_tags(self, tags: list) -> Tuple[bool, Optional[str]]:
        """
        Validate tags list

        Args:
            tags: List of tags to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if tags is None:
            return True, None  # Tags are optional

        if not isinstance(tags, list):
            return False, "Tags must be a list"

        if len(tags) > 50:  # Limit number of tags
            return False, "Too many tags"

        total_size = 0
        for tag in tags:
            if not isinstance(tag, str):
                return False, "Each tag must be a string"

            if len(tag) > 50:
                return False, "Tag exceeds maximum length"

            total_size += len(tag)

        if total_size > self.MAX_TAGS_SIZE:
            return False, "Total tag size exceeds maximum"

        return True, None

    def validate_date_string(self, date_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate date string format (YYYY-MM-DD)

        Args:
            date_string: Date string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(date_string, str):
            return False, "Date must be a string"

        # Simple format validation
        if len(date_string) != 10:
            return False, "Invalid date format"

        parts = date_string.split('-')
        if len(parts) != 3:
            return False, "Invalid date format"

        try:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            if not (1900 <= year <= 2100):
                return False, "Invalid date"

            if not (1 <= month <= 12):
                return False, "Invalid date"

            if not (1 <= day <= 31):
                return False, "Invalid date"

            return True, None
        except ValueError:
            return False, "Invalid date format"

    def validate_date_range(self, date_range: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate date range dictionary

        Args:
            date_range: Dictionary with 'start' and 'end' date strings

        Returns:
            Tuple of (is_valid, error_message)
        """
        if date_range is None:
            return True, None  # Date range is optional

        if not isinstance(date_range, dict):
            return False, "Date range must be a dictionary"

        for key in date_range.keys():
            if key not in ('start', 'end'):
                return False, "Invalid date range key"

        # Validate start date if present
        if 'start' in date_range:
            valid, error = self.validate_date_string(date_range['start'])
            if not valid:
                return False, error

        # Validate end date if present
        if 'end' in date_range:
            valid, error = self.validate_date_string(date_range['end'])
            if not valid:
                return False, error

        return True, None

    def get_safe_project_path(self, project_name: str) -> Optional[Path]:
        """
        Get safe project path after validation

        Args:
            project_name: Project name to convert to path

        Returns:
            Path object if valid, None otherwise
        """
        valid, error = self.validate_project_name(project_name)
        if not valid:
            return None

        # Create path and verify it stays within base directory
        project_path = self.base_projects_dir / project_name

        try:
            resolved = project_path.resolve()
            # Verify it's under base directory
            resolved.relative_to(self.base_projects_dir.resolve())
            return resolved
        except ValueError:
            return None
