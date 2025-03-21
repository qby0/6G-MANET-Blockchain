#!/usr/bin/env python3

import glob
import os
import re
from typing import List, Tuple


def fix_logging_format(file_path: str) -> Tuple[bool, int]:
    """
    Fix the logging format in the specified file.

    Args:
        file_path: Path to the file to fix

    Returns:
        Tuple of (whether file was modified, number of replacements)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip standard logging configuration format
    if re.search(
        r'format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"', content
    ):
        # This is a logging config line which is correct
        standard_format = True
    else:
        standard_format = False

    modified_content = content
    total_replacements = 0

    # Pattern 1: Simple dictionary cases like logger.info("%(key)s text", {key: value})
    pattern1 = re.compile(
        r'(logger\.[a-z]+\(\s*")(%\(([^)]+)\)s)([^"]*")(\s*,\s*\{[^}]+\})'
    )

    # Find all matches first
    matches = list(pattern1.finditer(content))
    if matches:
        for match in matches:
            prefix = match.group(1)  # logger.info("
            format_spec = match.group(2)  # %(key)s
            key = match.group(3)  # key
            suffix = match.group(4)  # text"
            dict_part = match.group(5)  # , {key: value}

            # Extract the value from the dictionary
            dict_text = dict_part.strip()
            # Try to find the corresponding value in the dictionary
            value_match = re.search(rf"{re.escape(key)}:\s*([^,}}]+)", dict_text)

            if value_match:
                value = value_match.group(1).strip()
                # Replace with %s format
                replacement = f"{prefix}%s{suffix}, {value}"

                # Only replace this specific occurrence
                old_text = match.group(0)
                # Check if this is not part of a standard logging format line
                if standard_format and "format=" in old_text:
                    continue

                modified_content = modified_content.replace(old_text, replacement, 1)
                total_replacements += 1

    # Pattern 2: Handle specific cases like in models/integration/distributed_blockchain_manager.py
    pattern2 = re.compile(
        r'(self\.logger\.[a-z]+\(\s*")(%\(([^)]+)\)s)([^"]*")(\s*,\s*\{[^}]+\})'
    )

    matches = list(pattern2.finditer(content))
    if matches:
        for match in matches:
            prefix = match.group(1)  # self.logger.info("
            format_spec = match.group(2)  # %(key)s
            key = match.group(3)  # key
            suffix = match.group(4)  # text"
            dict_part = match.group(5)  # , {key: value}

            # Extract the value from the dictionary
            dict_text = dict_part.strip()
            # Try to find the corresponding value in the dictionary
            value_match = re.search(rf"{re.escape(key)}:\s*([^,}}]+)", dict_text)

            if value_match:
                value = value_match.group(1).strip()
                # Replace with %s format
                replacement = f"{prefix}%s{suffix}, {value}"

                # Only replace this specific occurrence
                old_text = match.group(0)
                modified_content = modified_content.replace(old_text, replacement, 1)
                total_replacements += 1

    # Pattern 3: Handle cases with multiple format specifiers
    # This pattern is more complex because we need to preserve the order of arguments
    pattern3 = re.compile(
        r'((?:self\.)?logger\.[a-z]+\(\s*")([^"]+)("(?:\s*,\s*\{[^}]+\}))'
    )

    matches = list(pattern3.finditer(content))
    if matches:
        for match in matches:
            full_match = match.group(0)  # The entire match
            prefix = match.group(1)  # logger.info("
            message = match.group(2)  # text with %(key1)s and %(key2)s
            suffix = match.group(3)  # ", {key1: val1, key2: val2}

            # Skip if this is part of the standard logging format (already handled)
            if "format=" in full_match and standard_format:
                continue

            # Find all format specifiers in the message
            format_specs = list(re.finditer(r"%\(([^)]+)\)s", message))
            if format_specs:
                # Skip if there are no format specifiers
                if not format_specs:
                    continue

                # If there's a dictionary part, extract the values
                dict_match = re.search(r"\{([^}]+)\}", suffix)
                if dict_match:
                    dict_content = dict_match.group(1)

                    # Try to find all keys and values in the dictionary
                    keys_values = {}
                    for format_spec in format_specs:
                        key = format_spec.group(1)
                        value_match = re.search(
                            rf"{re.escape(key)}:\s*([^,}}]+)", dict_content
                        )
                        if value_match:
                            keys_values[key] = value_match.group(1).strip()

                    # Check if we found all keys
                    if len(keys_values) == len(format_specs):
                        # Replace all format specifiers with %s
                        new_message = message
                        for format_spec in format_specs:
                            key = format_spec.group(1)
                            new_message = new_message.replace(f"%({key})s", "%s")

                        # Create a list of values in the order they appear in the format string
                        values = []
                        for format_spec in format_specs:
                            key = format_spec.group(1)
                            values.append(keys_values[key])

                        # Create the replacement
                        if len(values) == 1:
                            replacement = f'{prefix}{new_message}", {values[0]}'
                        else:
                            replacement = (
                                f'{prefix}{new_message}", ({", ".join(values)})'
                            )

                        # Replace in the content
                        modified_content = modified_content.replace(
                            full_match, replacement, 1
                        )
                        total_replacements += 1

    # If we made changes, write the file
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True, total_replacements

    return False, 0


def process_directory(directory: str) -> List[str]:
    """
    Process all Python files in the given directory and its subdirectories.

    Args:
        directory: The directory to process

    Returns:
        List of files that were modified
    """
    modified_files = []
    total_replacements = 0

    for py_file in glob.glob(f"{directory}/**/*.py", recursive=True):
        modified, count = fix_logging_format(py_file)
        if modified:
            modified_files.append(py_file)
            total_replacements += count
            print(f"Fixed logging format in {py_file} ({count} replacements)")

    print(f"\nTotal files modified: {len(modified_files)}")
    print(f"Total replacements: {total_replacements}")

    return modified_files


if __name__ == "__main__":
    print("Fixing logging format issues...")
    process_directory("test_ns3_blocksim")
    print("Done.")
