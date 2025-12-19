"""
Response Post-Processing & Formatting Utilities
Handles saving, formatting, and extracting content from model responses
"""

from pathlib import Path
from typing import Optional, List, Dict
import re
from datetime import datetime


class ResponseProcessor:
    """Post-processing utilities for model responses"""

    def __init__(self, output_dir: Path):
        """Initialize processor with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def save_response(self, response: str, filename: Optional[str] = None,
                     model_name: str = "", metadata: Optional[Dict] = None) -> Path:
        """
        Save response to file with metadata header

        Args:
            response: Response text to save
            filename: Optional custom filename (auto-generated if None)
            model_name: Name of the model that generated the response
            metadata: Optional metadata dict to include in header

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"response_{timestamp}.txt"

        # Ensure .txt extension if not present
        if not filename.endswith('.txt'):
            filename += '.txt'

        filepath = self.output_dir / filename

        # Build metadata header
        header = self._build_metadata_header(model_name, metadata)

        # Combine header and response
        full_content = f"{header}\n{response}"

        # Save to file
        filepath.write_text(full_content, encoding='utf-8')

        return filepath

    def _build_metadata_header(self, model_name: str, metadata: Optional[Dict] = None) -> str:
        """Build metadata header for saved response"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header_lines = [
            "=" * 80,
            "AI ROUTER - MODEL RESPONSE",
            "=" * 80,
            f"Generated: {timestamp}",
        ]

        if model_name:
            header_lines.append(f"Model: {model_name}")

        if metadata:
            for key, value in metadata.items():
                header_lines.append(f"{key}: {value}")

        header_lines.extend([
            "=" * 80,
            ""
        ])

        return "\n".join(header_lines)

    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks with language tags from markdown

        Args:
            text: Text containing markdown code blocks

        Returns:
            List of dicts with 'language' and 'code' keys
        """
        # Regex pattern for markdown code blocks: ```language\n...\n```
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        return [
            {
                "language": lang.strip() if lang else "text",
                "code": code.strip()
            }
            for lang, code in matches
        ]

    def save_code_blocks(self, text: str, base_name: str) -> List[Path]:
        """
        Extract and save code blocks to separate files

        Args:
            text: Text containing code blocks
            base_name: Base name for saved files (e.g., "output")

        Returns:
            List of paths to saved code files
        """
        blocks = self.extract_code_blocks(text)
        saved_files = []

        for i, block in enumerate(blocks):
            ext = self._get_extension(block['language'])
            filename = f"{base_name}_code_{i}{ext}"
            filepath = self.output_dir / filename

            # Save code with language comment at top
            content = f"# Language: {block['language']}\n\n{block['code']}"
            filepath.write_text(content, encoding='utf-8')

            saved_files.append(filepath)

        return saved_files

    def format_as_markdown(self, response: str, model_name: str = "",
                          metadata: Optional[Dict] = None) -> str:
        """
        Format response with metadata as markdown

        Args:
            response: Response text to format
            model_name: Name of the model
            metadata: Optional metadata dict

        Returns:
            Formatted markdown string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_lines = [
            "# AI Router Response",
            "",
            f"**Generated:** {timestamp}",
        ]

        if model_name:
            md_lines.append(f"**Model:** {model_name}")

        if metadata:
            md_lines.append("")
            md_lines.append("## Metadata")
            md_lines.append("")
            for key, value in metadata.items():
                md_lines.append(f"- **{key}:** {value}")

        md_lines.extend([
            "",
            "---",
            "",
            "## Response",
            "",
            response
        ])

        return "\n".join(md_lines)

    def get_statistics(self, text: str) -> Dict:
        """
        Calculate response statistics

        Args:
            text: Text to analyze

        Returns:
            Dict with statistics
        """
        lines = text.splitlines()
        words = text.split()
        code_blocks = self.extract_code_blocks(text)

        return {
            "char_count": len(text),
            "word_count": len(words),
            "line_count": len(lines),
            "code_blocks": len(code_blocks),
            "avg_line_length": len(text) / len(lines) if lines else 0
        }

    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to clipboard (requires pyperclip)

        Args:
            text: Text to copy

        Returns:
            True if successful, False if pyperclip not available
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            return False

    @staticmethod
    def _get_extension(language: str) -> str:
        """
        Map programming language to file extension

        Args:
            language: Language name (e.g., "python", "javascript")

        Returns:
            File extension with dot (e.g., ".py", ".js")
        """
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c++": ".cpp",
            "c": ".c",
            "rust": ".rs",
            "go": ".go",
            "bash": ".sh",
            "shell": ".sh",
            "sql": ".sql",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "yaml": ".yaml",
            "yml": ".yaml",
            "xml": ".xml",
            "markdown": ".md",
            "md": ".md",
            "text": ".txt",
        }
        return extensions.get(language.lower(), ".txt")

    def list_saved_responses(self, limit: int = 10) -> List[Path]:
        """
        List recently saved response files

        Args:
            limit: Maximum number of files to return

        Returns:
            List of paths sorted by modification time (newest first)
        """
        files = sorted(
            self.output_dir.glob("response_*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return files[:limit]
