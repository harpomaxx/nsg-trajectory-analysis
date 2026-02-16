#!/usr/bin/env python3
"""
JSONL Structure Analyzer
Analyzes the structure of JSONL files by sampling entries and extracting schema information.
"""

import json
import sys
from collections import defaultdict, Counter
from typing import Any, Dict, Set
import argparse


def get_type_info(value: Any) -> str:
    """Get detailed type information for a value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        if len(value) == 0:
            return "list[empty]"
        # Sample first few elements to determine list type
        types = set(get_type_info(item) for item in value[:5])
        if len(types) == 1:
            return f"list[{types.pop()}]"
        else:
            return f"list[mixed: {', '.join(sorted(types))}]"
    elif isinstance(value, dict):
        return "object"
    else:
        return type(value).__name__


def analyze_structure(obj: Dict, path: str = "") -> Dict[str, Set[str]]:
    """Recursively analyze the structure of a JSON object."""
    structure = defaultdict(set)

    for key, value in obj.items():
        current_path = f"{path}.{key}" if path else key
        type_info = get_type_info(value)
        structure[current_path].add(type_info)

        # Recursively analyze nested objects
        if isinstance(value, dict):
            nested = analyze_structure(value, current_path)
            for nested_path, types in nested.items():
                structure[nested_path].update(types)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # Analyze first few items in list of objects
            for item in value[:3]:
                if isinstance(item, dict):
                    nested = analyze_structure(item, current_path)
                    for nested_path, types in nested.items():
                        structure[nested_path].update(types)

    return structure


def get_sample_value(obj: Dict, path: str) -> Any:
    """Get a sample value from a nested path."""
    keys = path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def analyze_jsonl_file(filepath: str, max_lines: int = 100):
    """Analyze a JSONL file structure."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {filepath}")
    print(f"{'='*80}\n")

    structure = defaultdict(set)
    line_count = 0
    error_count = 0
    sample_records = []

    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line_count >= max_lines:
                break

            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                line_count += 1

                # Store first few samples
                if len(sample_records) < 3:
                    sample_records.append(obj)

                # Analyze structure
                obj_structure = analyze_structure(obj)
                for path, types in obj_structure.items():
                    structure[path].update(types)

            except json.JSONDecodeError as e:
                error_count += 1
                if error_count <= 5:
                    print(f"Error on line {line_num}: {e}")

    # Count total lines
    with open(filepath, 'r') as f:
        total_lines = sum(1 for line in f if line.strip())

    print(f"Total lines in file: {total_lines}")
    print(f"Lines analyzed: {line_count}")
    print(f"Parse errors: {error_count}")
    print(f"\n{'='*80}")
    print(f"SCHEMA STRUCTURE")
    print(f"{'='*80}\n")

    # Sort paths for better readability
    sorted_paths = sorted(structure.keys())

    for path in sorted_paths:
        types = structure[path]
        types_str = " | ".join(sorted(types))
        indent = "  " * (path.count('.'))
        key = path.split('.')[-1]
        print(f"{indent}{key}: {types_str}")

        # Show sample values for leaf nodes
        if sample_records and len(types) == 1 and list(types)[0] in ['string', 'int', 'float', 'bool']:
            sample_val = get_sample_value(sample_records[0], path)
            if sample_val is not None:
                sample_str = str(sample_val)
                if len(sample_str) > 60:
                    sample_str = sample_str[:60] + "..."
                print(f"{indent}  └─ example: {sample_str}")

    # Show a sample record
    if sample_records:
        print(f"\n{'='*80}")
        print(f"SAMPLE RECORD (first entry)")
        print(f"{'='*80}\n")
        print(json.dumps(sample_records[0], indent=2)[:2000])
        if len(json.dumps(sample_records[0], indent=2)) > 2000:
            print("\n... (truncated)")

    return structure


def main():
    parser = argparse.ArgumentParser(description='Analyze JSONL file structure')
    parser.add_argument('files', nargs='+', help='JSONL files to analyze')
    parser.add_argument('--max-lines', type=int, default=100,
                       help='Maximum lines to analyze per file (default: 100)')

    args = parser.parse_args()

    for filepath in args.files:
        try:
            analyze_jsonl_file(filepath, args.max_lines)
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
