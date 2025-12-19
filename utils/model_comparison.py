#!/usr/bin/env python3
"""
Model Comparison - A/B Testing for AI Router
Allows side-by-side comparison of multiple models with the same prompt
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid
from pathlib import Path


@dataclass
class ComparisonResult:
    """Stores a model comparison session"""
    comparison_id: str
    timestamp: datetime
    prompt: str
    responses: List[Dict]  # List of {model_id, model_name, response, tokens_input, tokens_output, duration}
    winner: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'comparison_id': self.comparison_id,
            'timestamp': self.timestamp.isoformat(),
            'prompt': self.prompt,
            'responses': self.responses,
            'winner': self.winner,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ComparisonResult':
        """Create ComparisonResult from dictionary"""
        return cls(
            comparison_id=data['comparison_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            prompt=data['prompt'],
            responses=data['responses'],
            winner=data.get('winner'),
            notes=data.get('notes')
        )


class ModelComparison:
    """Manages side-by-side model comparisons"""

    def __init__(self, output_dir: Path):
        """
        Initialize model comparison manager

        Args:
            output_dir: Directory to store comparison exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def create_comparison(self, prompt: str, model_responses: List[Dict]) -> ComparisonResult:
        """
        Create a comparison result from multiple model responses

        Args:
            prompt: The prompt text used for all models
            model_responses: List of response dicts with keys:
                - model_id: Model identifier
                - model_name: Human-readable model name
                - response: Response text
                - tokens_input: Input token count (optional)
                - tokens_output: Output token count (optional)
                - duration: Duration in seconds (optional)

        Returns:
            ComparisonResult object
        """
        comparison_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Ensure all responses have required fields
        formatted_responses = []
        for resp in model_responses:
            formatted_responses.append({
                'model_id': resp['model_id'],
                'model_name': resp['model_name'],
                'response': resp['response'],
                'tokens_input': resp.get('tokens_input', 0),
                'tokens_output': resp.get('tokens_output', 0),
                'duration': resp.get('duration', 0.0)
            })

        return ComparisonResult(
            comparison_id=comparison_id,
            timestamp=timestamp,
            prompt=prompt,
            responses=formatted_responses
        )

    def display_comparison(self, result: ComparisonResult, colors=None):
        """
        Display side-by-side comparison in terminal

        Args:
            result: ComparisonResult to display
            colors: Optional Colors class for terminal formatting
        """
        if colors is None:
            # Fallback to no colors if not provided
            class DummyColors:
                RESET = BOLD = BRIGHT_CYAN = BRIGHT_WHITE = CYAN = GREEN = YELLOW = ""
                BRIGHT_GREEN = BRIGHT_YELLOW = DIM = RED = BRIGHT_RED = ""
            colors = DummyColors()

        # Display header
        print(f"\n{colors.BRIGHT_CYAN}{colors.BOLD}╔══════════════════════════════════════════════════════════════╗{colors.RESET}")
        print(f"{colors.BRIGHT_CYAN}{colors.BOLD}║  MODEL COMPARISON RESULTS{colors.RESET}")
        print(f"{colors.BRIGHT_CYAN}{colors.BOLD}╚══════════════════════════════════════════════════════════════╝{colors.RESET}\n")

        # Display prompt
        print(f"{colors.BRIGHT_WHITE}Prompt:{colors.RESET}")
        print(f"{colors.CYAN}{result.prompt}{colors.RESET}\n")
        print(f"{colors.DIM}{'─' * 80}{colors.RESET}\n")

        # Display each model's response
        for idx, resp in enumerate(result.responses, 1):
            print(f"{colors.BRIGHT_GREEN}[{idx}] {resp['model_name']}{colors.RESET}")
            print(f"{colors.DIM}Model ID: {resp['model_id']}{colors.RESET}\n")

            # Display response text
            response_text = resp['response']
            # Truncate if too long for side-by-side display
            max_lines = 30
            lines = response_text.split('\n')
            if len(lines) > max_lines:
                display_text = '\n'.join(lines[:max_lines]) + f"\n{colors.DIM}... (truncated){colors.RESET}"
            else:
                display_text = response_text

            print(display_text)
            print(f"\n{colors.DIM}{'─' * 80}{colors.RESET}\n")

    def display_comparison_table(self, result: ComparisonResult, colors=None):
        """
        Display comparison as a performance metrics table

        Args:
            result: ComparisonResult to display
            colors: Optional Colors class for terminal formatting
        """
        if colors is None:
            class DummyColors:
                RESET = BOLD = BRIGHT_CYAN = BRIGHT_WHITE = CYAN = GREEN = YELLOW = ""
                BRIGHT_GREEN = BRIGHT_YELLOW = DIM = RED = BRIGHT_RED = ""
            colors = DummyColors()

        print(f"\n{colors.BRIGHT_CYAN}{colors.BOLD}╔══════════════════════════════════════════════════════════════╗{colors.RESET}")
        print(f"{colors.BRIGHT_CYAN}{colors.BOLD}║  PERFORMANCE METRICS{colors.RESET}")
        print(f"{colors.BRIGHT_CYAN}{colors.BOLD}╚══════════════════════════════════════════════════════════════╝{colors.RESET}\n")

        # Table header
        print(f"{colors.BRIGHT_WHITE}{'Model':<30} {'In/Out Tokens':<20} {'Duration':<12} {'Tok/Sec':<12}{colors.RESET}")
        print(f"{colors.DIM}{'─' * 80}{colors.RESET}")

        # Calculate fastest model for highlighting
        fastest_idx = -1
        fastest_speed = 0
        for idx, resp in enumerate(result.responses):
            if resp['duration'] > 0 and resp['tokens_output'] > 0:
                speed = resp['tokens_output'] / resp['duration']
                if speed > fastest_speed:
                    fastest_speed = speed
                    fastest_idx = idx

        # Display each model's metrics
        for idx, resp in enumerate(result.responses):
            model_name = resp['model_name'][:28]  # Truncate long names
            tokens_str = f"{resp['tokens_input']}/{resp['tokens_output']}"
            duration_str = f"{resp['duration']:.2f}s" if resp['duration'] > 0 else "N/A"

            # Calculate tokens/sec
            if resp['duration'] > 0 and resp['tokens_output'] > 0:
                tokens_per_sec = resp['tokens_output'] / resp['duration']
                speed_str = f"{tokens_per_sec:.1f} tok/s"
            else:
                tokens_per_sec = 0
                speed_str = "N/A"

            # Highlight fastest model
            if idx == fastest_idx:
                color = colors.BRIGHT_GREEN
                winner_mark = " ⭐"
            else:
                color = colors.RESET
                winner_mark = ""

            print(f"{color}{model_name:<30} {tokens_str:<20} {duration_str:<12} {speed_str:<12}{winner_mark}{colors.RESET}")

        print(f"{colors.DIM}{'─' * 80}{colors.RESET}\n")

        # Display summary
        if fastest_idx >= 0:
            winner = result.responses[fastest_idx]
            print(f"{colors.BRIGHT_GREEN}⭐ Fastest: {winner['model_name']} ({fastest_speed:.1f} tok/s){colors.RESET}\n")

    def export_comparison(self, result: ComparisonResult, format: str = 'json') -> Path:
        """
        Export comparison to JSON or Markdown

        Args:
            result: ComparisonResult to export
            format: 'json' or 'markdown'

        Returns:
            Path to exported file
        """
        timestamp_str = result.timestamp.strftime("%Y%m%d_%H%M%S")

        if format == 'json':
            filename = f"comparison_{timestamp_str}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)

        elif format == 'markdown':
            filename = f"comparison_{timestamp_str}.md"
            filepath = self.output_dir / filename

            md_content = self._format_as_markdown(result)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return filepath

    def _format_as_markdown(self, result: ComparisonResult) -> str:
        """
        Format comparison result as markdown

        Args:
            result: ComparisonResult to format

        Returns:
            Markdown-formatted string
        """
        lines = [
            "# Model Comparison Report",
            "",
            f"**Comparison ID:** {result.comparison_id}",
            f"**Timestamp:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Models Compared:** {len(result.responses)}",
            "",
            "## Prompt",
            "",
            f"```",
            result.prompt,
            f"```",
            "",
            "## Performance Metrics",
            "",
            "| Model | Input Tokens | Output Tokens | Duration | Tokens/Sec |",
            "| ----- | ------------ | ------------- | -------- | ---------- |",
        ]

        # Calculate performance for each model
        for resp in result.responses:
            model_name = resp['model_name']
            tokens_in = resp.get('tokens_input', 0)
            tokens_out = resp.get('tokens_output', 0)
            duration = resp.get('duration', 0.0)

            if duration > 0 and tokens_out > 0:
                speed = tokens_out / duration
                speed_str = f"{speed:.1f}"
            else:
                speed_str = "N/A"

            duration_str = f"{duration:.2f}s" if duration > 0 else "N/A"

            lines.append(f"| {model_name} | {tokens_in} | {tokens_out} | {duration_str} | {speed_str} |")

        lines.extend([
            "",
            "## Responses",
            ""
        ])

        # Add each model's response
        for idx, resp in enumerate(result.responses, 1):
            lines.extend([
                f"### {idx}. {resp['model_name']}",
                "",
                f"**Model ID:** `{resp['model_id']}`",
                "",
                "**Response:**",
                "",
                "```",
                resp['response'],
                "```",
                ""
            ])

        # Add notes if present
        if result.notes:
            lines.extend([
                "## Notes",
                "",
                result.notes,
                ""
            ])

        # Add winner if present
        if result.winner:
            lines.extend([
                "## Winner",
                "",
                f"**Selected Model:** {result.winner}",
                ""
            ])

        return "\n".join(lines)

    def save_comparison_to_db(self, result: ComparisonResult, session_manager):
        """
        Save comparison to session database

        Args:
            result: ComparisonResult to save
            session_manager: SessionManager instance with database connection
        """
        # Store comparison metadata
        comparison_data = {
            'comparison_id': result.comparison_id,
            'timestamp': result.timestamp.isoformat(),
            'prompt': result.prompt,
            'model_count': len(result.responses),
            'winner': result.winner,
            'notes': result.notes
        }

        # Store in session_metadata table using comparison_id as session_id
        # This allows us to use existing infrastructure
        for key, value in comparison_data.items():
            if value is not None:
                session_manager.set_session_metadata(
                    result.comparison_id,
                    f"comparison_{key}",
                    str(value)
                )

        # Store each response as metadata
        for idx, resp in enumerate(result.responses):
            response_key = f"comparison_response_{idx}"
            response_data = json.dumps(resp)
            session_manager.set_session_metadata(
                result.comparison_id,
                response_key,
                response_data
            )

    def load_comparison_from_db(self, comparison_id: str, session_manager) -> Optional[ComparisonResult]:
        """
        Load comparison from session database

        Args:
            comparison_id: Comparison ID to load
            session_manager: SessionManager instance

        Returns:
            ComparisonResult or None if not found
        """
        # Load metadata
        timestamp_str = session_manager.get_session_metadata(comparison_id, "comparison_timestamp")
        if not timestamp_str:
            return None

        prompt = session_manager.get_session_metadata(comparison_id, "comparison_prompt")
        model_count = int(session_manager.get_session_metadata(comparison_id, "comparison_model_count") or "0")
        winner = session_manager.get_session_metadata(comparison_id, "comparison_winner")
        notes = session_manager.get_session_metadata(comparison_id, "comparison_notes")

        # Load responses
        responses = []
        for idx in range(model_count):
            response_key = f"comparison_response_{idx}"
            response_data = session_manager.get_session_metadata(comparison_id, response_key)
            if response_data:
                responses.append(json.loads(response_data))

        return ComparisonResult(
            comparison_id=comparison_id,
            timestamp=datetime.fromisoformat(timestamp_str),
            prompt=prompt,
            responses=responses,
            winner=winner,
            notes=notes
        )
