#!/usr/bin/env python3
"""
Ollama Model Analysis Tool
Analyzes current Ollama models and generates migration plan to MLX.

This script:
1. Lists all installed Ollama models with detailed stats
2. Categorizes models into DELETE, CONVERT, and KEEP based on mapping file
3. Calculates space savings and performance improvements
4. Generates detailed migration report

Usage:
    python3 ollama-model-analysis.py [--json] [--summary]

Options:
    --json      Output in JSON format
    --summary   Show summary statistics only
    --verbose   Show detailed information
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class OllamaAnalyzer:
    """Analyzes Ollama models and provides migration insights."""

    def __init__(self, mapping_file: str = "mlx-model-mapping.json"):
        """Initialize analyzer with model mapping data."""
        self.mapping_file = Path(mapping_file)
        self.mapping_data = self._load_mapping()
        self.ollama_models = []

    def _load_mapping(self) -> Dict:
        """Load model mapping from JSON file."""
        try:
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Mapping file '{self.mapping_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in mapping file: {e}", file=sys.stderr)
            sys.exit(1)

    def get_ollama_models(self) -> List[Dict]:
        """Fetch list of installed Ollama models using ollama list command."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True
            )

            models = []
            lines = result.stdout.strip().split('\n')

            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    model_id = parts[1]

                    # Parse size (handle GB/MB)
                    size_str = parts[2]
                    size_unit = parts[3]

                    if size_unit == 'GB':
                        size_gb = float(size_str)
                    elif size_unit == 'MB':
                        size_gb = float(size_str) / 1024
                    else:
                        size_gb = 0

                    # Get modified date (rest of the parts)
                    modified = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'

                    models.append({
                        'name': name,
                        'id': model_id,
                        'size_gb': round(size_gb, 2),
                        'size_str': f"{size_str} {size_unit}",
                        'modified': modified
                    })

            return models

        except subprocess.CalledProcessError as e:
            print(f"Error running ollama list: {e}", file=sys.stderr)
            print("Make sure Ollama is installed and running.", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: 'ollama' command not found.", file=sys.stderr)
            print("Please install Ollama first.", file=sys.stderr)
            sys.exit(1)

    def categorize_model(self, model: Dict) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Categorize a model as DELETE, CONVERT, or KEEP.

        Returns:
            Tuple of (action, reason, replacement)
        """
        model_name = model['name']

        # Check DELETE list
        for delete_model in self.mapping_data['models_to_delete']:
            if delete_model['ollama_name'] == model_name:
                return (
                    'DELETE',
                    delete_model['reason'],
                    delete_model['replacement']
                )

        # Check CONVERT list
        for convert_model in self.mapping_data['models_to_convert']:
            if convert_model['ollama_name'] == model_name:
                action = convert_model['action']
                return (
                    action,
                    convert_model['reason'],
                    convert_model['replacement']
                )

        # Unknown model
        return ('UNKNOWN', 'Not in mapping file', None)

    def get_mlx_model_info(self, mlx_model_key: Optional[str]) -> Optional[Dict]:
        """Get MLX model information from mapping."""
        if not mlx_model_key:
            return None

        mlx_models = self.mapping_data.get('mlx_models', {})
        return mlx_models.get(mlx_model_key)

    def analyze(self) -> Dict:
        """Run full analysis and return results."""
        self.ollama_models = self.get_ollama_models()

        # Categorize all models
        categorized = {
            'DELETE': [],
            'CONVERT': [],
            'KEEP': [],
            'OPTIONAL_CONVERT': [],
            'UNKNOWN': []
        }

        for model in self.ollama_models:
            action, reason, replacement = self.categorize_model(model)

            categorized_model = {
                **model,
                'action': action,
                'reason': reason,
                'replacement': replacement,
                'mlx_info': self.get_mlx_model_info(replacement) if replacement else None
            }

            categorized[action].append(categorized_model)

        # Calculate statistics
        total_size = sum(m['size_gb'] for m in self.ollama_models)
        delete_size = sum(m['size_gb'] for m in categorized['DELETE'])
        convert_size = sum(m['size_gb'] for m in categorized['CONVERT'])
        keep_size = sum(m['size_gb'] for m in categorized['KEEP'])

        # Calculate MLX replacement size
        mlx_replacement_size = 0
        for model in categorized['DELETE'] + categorized['CONVERT']:
            if model['mlx_info']:
                mlx_replacement_size += model['mlx_info']['size_gb']

        return {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(self.ollama_models),
            'categorized': categorized,
            'statistics': {
                'total_ollama_size_gb': round(total_size, 2),
                'delete_size_gb': round(delete_size, 2),
                'convert_size_gb': round(convert_size, 2),
                'keep_size_gb': round(keep_size, 2),
                'mlx_replacement_size_gb': round(mlx_replacement_size, 2),
                'space_freed_gb': round(delete_size, 2),
                'net_space_change_gb': round(mlx_replacement_size - total_size, 2),
                'delete_count': len(categorized['DELETE']),
                'convert_count': len(categorized['CONVERT']),
                'keep_count': len(categorized['KEEP']),
                'unknown_count': len(categorized['UNKNOWN'])
            }
        }

    def print_summary(self, analysis: Dict):
        """Print human-readable summary of analysis."""
        stats = analysis['statistics']

        print("\n" + "=" * 80)
        print(" OLLAMA TO MLX MIGRATION ANALYSIS")
        print("=" * 80)
        print(f"\nAnalysis Date: {analysis['timestamp']}")
        print(f"Total Ollama Models: {analysis['total_models']}")
        print(f"Total Ollama Size: {stats['total_ollama_size_gb']:.1f} GB")

        print("\n" + "-" * 80)
        print(" MODEL CATEGORIZATION")
        print("-" * 80)

        # DELETE models
        if analysis['categorized']['DELETE']:
            print(f"\n🗑️  DELETE ({stats['delete_count']} models, {stats['delete_size_gb']:.1f} GB):")
            print("=" * 80)
            for model in analysis['categorized']['DELETE']:
                print(f"\n  • {model['name']}")
                print(f"    Size: {model['size_str']}")
                print(f"    Reason: {model['reason']}")
                if model['mlx_info']:
                    print(f"    → Replace with: {model['mlx_info']['huggingface_repo']}")
                    print(f"    → Speed: {model['mlx_info']['speed_tokens_per_sec']} tok/sec")

        # CONVERT models
        if analysis['categorized']['CONVERT']:
            print(f"\n🔄 CONVERT ({stats['convert_count']} models, {stats['convert_size_gb']:.1f} GB):")
            print("=" * 80)
            for model in analysis['categorized']['CONVERT']:
                print(f"\n  • {model['name']}")
                print(f"    Size: {model['size_str']}")
                print(f"    Reason: {model['reason']}")
                if model['mlx_info']:
                    print(f"    → MLX Version: {model['mlx_info']['huggingface_repo']}")
                    print(f"    → Speed: {model['mlx_info']['speed_tokens_per_sec']} tok/sec")

        # KEEP models
        if analysis['categorized']['KEEP']:
            print(f"\n✅ KEEP ({stats['keep_count']} models, {stats['keep_size_gb']:.1f} GB):")
            print("=" * 80)
            for model in analysis['categorized']['KEEP']:
                print(f"\n  • {model['name']}")
                print(f"    Size: {model['size_str']}")
                print(f"    Reason: {model['reason']}")

        # OPTIONAL_CONVERT models
        if analysis['categorized']['OPTIONAL_CONVERT']:
            print(f"\n⚡ OPTIONAL CONVERT ({len(analysis['categorized']['OPTIONAL_CONVERT'])} models):")
            print("=" * 80)
            for model in analysis['categorized']['OPTIONAL_CONVERT']:
                print(f"\n  • {model['name']}")
                print(f"    Size: {model['size_str']}")
                print(f"    Reason: {model['reason']}")
                if model['mlx_info']:
                    print(f"    → Optional: {model['mlx_info']['huggingface_repo']}")

        # UNKNOWN models
        if analysis['categorized']['UNKNOWN']:
            print(f"\n❓ UNKNOWN ({stats['unknown_count']} models):")
            print("=" * 80)
            for model in analysis['categorized']['UNKNOWN']:
                print(f"\n  • {model['name']}")
                print(f"    Size: {model['size_str']}")
                print(f"    Note: {model['reason']}")

        print("\n" + "-" * 80)
        print(" MIGRATION IMPACT")
        print("-" * 80)
        print(f"\nSpace Freed by Deletions: {stats['space_freed_gb']:.1f} GB")
        print(f"MLX Replacement Size: {stats['mlx_replacement_size_gb']:.1f} GB")
        print(f"Net Space Change: {stats['net_space_change_gb']:+.1f} GB")

        if stats['net_space_change_gb'] < 0:
            print(f"✅ You will FREE {abs(stats['net_space_change_gb']):.1f} GB of space!")
        else:
            print(f"⚠️  You will USE {stats['net_space_change_gb']:.1f} GB additional space")

        print("\n" + "-" * 80)
        print(" PERFORMANCE IMPROVEMENTS")
        print("-" * 80)

        perf = self.mapping_data.get('performance_comparison', {})
        for model_key, perf_data in perf.items():
            print(f"\n{model_key.upper()}:")
            if 'ollama_gguf_speed' in perf_data:
                print(f"  Ollama GGUF: {perf_data['ollama_gguf_speed']}")
            if 'ollama_gguf_32b_speed' in perf_data:
                print(f"  Ollama GGUF 32B: {perf_data['ollama_gguf_32b_speed']}")
            if 'mlx_speed' in perf_data:
                print(f"  MLX: {perf_data['mlx_speed']}")
            if 'mlx_8b_speed' in perf_data:
                print(f"  MLX 8B: {perf_data['mlx_8b_speed']}")
            if 'improvement_percent' in perf_data:
                print(f"  Improvement: {perf_data['improvement_percent']}")
            if 'note' in perf_data:
                print(f"  Note: {perf_data['note']}")

        print("\n" + "=" * 80)
        print(" NEXT STEPS")
        print("=" * 80)
        print("\n1. Review the DELETE list above")
        print("2. Run: ./migrate-to-mlx.sh --dry-run")
        print("3. When ready: ./migrate-to-mlx.sh --execute")
        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze Ollama models and plan MLX migration'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary only'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    parser.add_argument(
        '--mapping',
        default='mlx-model-mapping.json',
        help='Path to model mapping JSON file'
    )

    args = parser.parse_args()

    # Create analyzer
    analyzer = OllamaAnalyzer(mapping_file=args.mapping)

    # Run analysis
    analysis = analyzer.analyze()

    # Output results
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        analyzer.print_summary(analysis)

        if args.verbose:
            print("\n" + "=" * 80)
            print(" DETAILED MODEL LIST")
            print("=" * 80)
            print(json.dumps(analysis, indent=2))


if __name__ == '__main__':
    main()
