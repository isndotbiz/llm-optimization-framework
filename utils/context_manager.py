#!/usr/bin/env python3
"""
Context Manager - File and Text Context Injection System
Manages context loading, token estimation, and prompt building for AI Router
"""

from pathlib import Path
from typing import List, Optional, Dict
import re


class ContextManager:
    """Manages context injection from files and text"""

    # Language detection mapping
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.ps1': 'powershell',
        '.md': 'markdown',
        '.txt': 'text',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.dockerfile': 'dockerfile',
        '.makefile': 'makefile',
    }

    def __init__(self):
        """Initialize context manager"""
        self.context_items: List[Dict] = []
        self.max_tokens = 4096  # Default, adjustable
        self.token_estimation_ratio = 1.3  # words * 1.3 heuristic

    def add_file(self, file_path: Path, label: Optional[str] = None):
        """
        Add file contents as context

        Args:
            file_path: Path to the file to load
            label: Optional custom label (defaults to filename)

        Returns:
            Dict with file info or None if failed
        """
        try:
            file_path = Path(file_path)

            # SECURITY FIX CVE-2025-AIR-002: Path traversal protection
            # Resolve to absolute path and validate it's within allowed base directory
            base_dir = Path.cwd().resolve()
            file_path_resolved = file_path.resolve()

            # Check if the resolved path is within the base directory
            try:
                file_path_resolved.relative_to(base_dir)
            except ValueError:
                raise ValueError(f"Access denied: Path '{file_path}' is outside the allowed base directory '{base_dir}'")

            if not file_path_resolved.exists():
                raise FileNotFoundError(f"File not found: {file_path_resolved}")

            if not file_path_resolved.is_file():
                raise ValueError(f"Not a file: {file_path_resolved}")

            # Read file contents
            with open(file_path_resolved, 'r', encoding='utf-8') as f:
                content = f.read()

            # Detect language from extension (using resolved path)
            language = self._detect_language(file_path_resolved)

            # Create label
            if label is None:
                label = file_path_resolved.name

            # Create context item
            context_item = {
                'type': 'file',
                'label': label,
                'content': content,
                'language': language,
                'path': str(file_path_resolved),
                'tokens': self.estimate_tokens(content)
            }

            self.context_items.append(context_item)
            return context_item

        except Exception as e:
            raise RuntimeError(f"Failed to add file: {e}")

    def add_text(self, text: str, label: str):
        """
        Add arbitrary text as context

        Args:
            text: Text content to add
            label: Label for this text context

        Returns:
            Dict with text info
        """
        if not text.strip():
            raise ValueError("Cannot add empty text as context")

        if not label.strip():
            raise ValueError("Label is required for text context")

        # Create context item
        context_item = {
            'type': 'text',
            'label': label,
            'content': text,
            'language': 'text',
            'tokens': self.estimate_tokens(text)
        }

        self.context_items.append(context_item)
        return context_item

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count using words * 1.3 heuristic

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Split on whitespace and count words
        words = len(text.split())

        # Apply heuristic: tokens ≈ words * 1.3
        estimated_tokens = int(words * self.token_estimation_ratio)

        return estimated_tokens

    def build_context_prompt(self, user_prompt: str, truncate: bool = True) -> str:
        """
        Build final prompt with context injection

        Args:
            user_prompt: The user's actual query/prompt
            truncate: Whether to truncate context if exceeding max_tokens

        Returns:
            Complete prompt with context
        """
        if not self.context_items:
            # No context, return user prompt as-is
            return user_prompt

        # Calculate available tokens for context
        user_prompt_tokens = self.estimate_tokens(user_prompt)
        available_tokens = self.max_tokens - user_prompt_tokens - 100  # Reserve 100 for formatting

        if available_tokens <= 0:
            # User prompt alone exceeds limit
            if truncate:
                # Just return truncated user prompt
                return user_prompt
            else:
                raise ValueError(f"User prompt ({user_prompt_tokens} tokens) exceeds max_tokens ({self.max_tokens})")

        # Build context sections
        context_sections = []
        total_context_tokens = 0

        for item in self.context_items:
            if truncate and (total_context_tokens + item['tokens']) > available_tokens:
                # Would exceed limit, stop adding context
                break

            # Format context item
            section = self._format_context_item(item)
            context_sections.append(section)
            total_context_tokens += item['tokens']

        # Combine everything
        if context_sections:
            context_block = "\n\n".join(context_sections)
            separator = "\n\n" + "="*80 + "\n\n"
            full_prompt = f"{context_block}{separator}USER REQUEST:\n{user_prompt}"
        else:
            # No context could fit, return user prompt
            full_prompt = user_prompt

        return full_prompt

    def _format_context_item(self, item: Dict) -> str:
        """
        Format a single context item for injection

        Args:
            item: Context item dict

        Returns:
            Formatted string
        """
        if item['type'] == 'file':
            # Format: ## Label (path)
            # ```language
            # content
            # ```
            header = f"## {item['label']}"
            if 'path' in item:
                header += f" ({item['path']})"

            code_block = f"```{item['language']}\n{item['content']}\n```"
            return f"{header}\n\n{code_block}"

        else:  # text
            # Format: ## Label
            # content
            header = f"## {item['label']}"
            return f"{header}\n\n{item['content']}"

    def clear_context(self):
        """Clear all context items"""
        self.context_items.clear()

    def get_context_summary(self) -> str:
        """
        Get summary of current context

        Returns:
            Human-readable summary string
        """
        if not self.context_items:
            return "No context loaded"

        total_tokens = sum(item['tokens'] for item in self.context_items)

        summary_lines = [
            f"Context Summary:",
            f"  Items: {len(self.context_items)}",
            f"  Total tokens: {total_tokens:,}",
            f"  Max tokens: {self.max_tokens:,}",
            f"  Utilization: {(total_tokens/self.max_tokens)*100:.1f}%",
            "",
            "Context Items:"
        ]

        for idx, item in enumerate(self.context_items, 1):
            summary_lines.append(
                f"  [{idx}] {item['label']} ({item['type']}, {item['tokens']:,} tokens)"
            )

        return "\n".join(summary_lines)

    def remove_context_item(self, index: int) -> bool:
        """
        Remove a context item by index

        Args:
            index: 0-based index of item to remove

        Returns:
            True if removed, False if index invalid
        """
        if 0 <= index < len(self.context_items):
            removed = self.context_items.pop(index)
            return True
        return False

    def set_max_tokens(self, max_tokens: int):
        """
        Set maximum token limit

        Args:
            max_tokens: New maximum token limit
        """
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        self.max_tokens = max_tokens

    def get_total_tokens(self) -> int:
        """
        Get total tokens across all context items

        Returns:
            Total token count
        """
        return sum(item['tokens'] for item in self.context_items)

    def _detect_language(self, file_path: Path) -> str:
        """
        Detect programming language from file extension

        Args:
            file_path: Path to file

        Returns:
            Language identifier
        """
        suffix = file_path.suffix.lower()

        # Check special filenames
        name_lower = file_path.name.lower()
        if 'dockerfile' in name_lower:
            return 'dockerfile'
        if 'makefile' in name_lower:
            return 'makefile'

        # Check extension mapping
        return self.LANGUAGE_MAP.get(suffix, 'text')
