#!/usr/bin/env python3
"""
Script to fix common type annotation issues in the codebase.
"""

import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


def add_optional_annotations(file_path: str) -> bool:
    """Adds Optional[] type hint to parameters with None default."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to find function parameters with None default
    pattern = r"(def \w+\([^)]*?)(\w+)(\s*=\s*None[^)]*?\))"

    # If "from typing import Optional" not in file, add it
    if "Optional" not in content and re.search(pattern, content):
        if "from typing import " in content:
            content = re.sub(
                r"from typing import (.*)", r"from typing import \1, Optional", content
            )
        elif "import typing" in content:
            content = re.sub(r"import typing", r"from typing import Optional", content)
        else:
            # Add after other imports
            import_end = 0
            for match in re.finditer(r"^import .*$", content, re.MULTILINE):
                import_end = max(import_end, match.end())

            if import_end > 0:
                content = (
                    content[:import_end]
                    + "\nfrom typing import Optional, Any"
                    + content[import_end:]
                )
            else:
                content = "from typing import Optional, Any\n\n" + content

    # Replace param=None with param: Optional[type]=None
    def replacement(match):
        prefix, param, suffix = match.groups()

        # Look for type hints in function definition
        type_hint_pattern = r": *(\w+)"
        type_hint_match = re.search(rf"{param}{type_hint_pattern}", prefix)

        if type_hint_match:
            type_name = type_hint_match.group(1)
            # Already has a type hint, wrap it in Optional
            return f"{prefix.replace(f': {type_name}', f': Optional[{type_name}]')}{param}{suffix}"
        else:
            # No type hint, add a basic one
            return f"{prefix}{param}: Optional[Any]{suffix}"

    modified_content = re.sub(pattern, replacement, content)

    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True
    return False


def add_var_annotations(file_path: str) -> bool:
    """Adds missing variable type annotations."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Need to check if Any is imported
    if "self." in content and "Any" not in content:
        if "from typing import " in content:
            content = re.sub(
                r"from typing import (.*)", r"from typing import \1, Any", content
            )
        elif "import typing" in content:
            content = content.replace("import typing", "from typing import Any")
        else:
            # Add after other imports
            import_end = 0
            for match in re.finditer(r"^import .*$", content, re.MULTILINE):
                import_end = max(import_end, match.end())

            if import_end > 0:
                content = (
                    content[:import_end]
                    + "\nfrom typing import Any"
                    + content[import_end:]
                )
            else:
                content = "from typing import Any\n\n" + content

    # Dict and List pattern to find class variables without type annotations
    patterns = [
        # Dictionaries
        (r"self\.(\w+)\s*=\s*\{\}", r"self.\1: Dict[str, Any] = {}"),
        # Lists
        (r"self\.(\w+)\s*=\s*\[\]", r"self.\1: List[Any] = []"),
        # Node dictionaries (from error messages)
        (r"self\.(nodes)\s*=\s*\{\}", r"self.\1: Dict[str, Any] = {}"),
        # Links dictionaries
        (r"self\.(links)\s*=\s*\{\}", r"self.\1: Dict[str, Any] = {}"),
        # Transactions lists
        (
            r"self\.(transactions|pending_transactions)\s*=\s*\[\]",
            r"self.\1: List[Any] = []",
        ),
        # Current state dictionaries
        (r"self\.(current_state)\s*=\s*\{\}", r"self.\1: Dict[str, Any] = {}"),
        # Events lists
        (
            r"self\.(network_events|blockchain_events)\s*=\s*\[\]",
            r"self.\1: List[Any] = []",
        ),
    ]

    modified_content = content
    changes_made = False

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, modified_content)
        if new_content != modified_content:
            modified_content = new_content
            changes_made = True

    # Ensure typing imports if changes were made
    if changes_made and (
        "Dict" not in modified_content or "List" not in modified_content
    ):
        if "from typing import " in modified_content:
            if "Dict" not in modified_content:
                modified_content = re.sub(
                    r"from typing import (.*)",
                    r"from typing import \1, Dict",
                    modified_content,
                )
            if "List" not in modified_content:
                modified_content = re.sub(
                    r"from typing import (.*)",
                    r"from typing import \1, List",
                    modified_content,
                )
        else:
            # Add after other imports
            import_end = 0
            for match in re.finditer(r"^import .*$", modified_content, re.MULTILINE):
                import_end = max(import_end, match.end())

            if import_end > 0:
                modified_content = (
                    modified_content[:import_end]
                    + "\nfrom typing import Dict, List, Any"
                    + modified_content[import_end:]
                )
            else:
                modified_content = (
                    "from typing import Dict, List, Any\n\n" + modified_content
                )

    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True
    return False


def fix_security_issues(file_path: str) -> bool:
    """Fix common security issues."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace hardcoded temp directories
    modified_content = re.sub(
        r'"/tmp/([^"]+)"', r'os.path.join(tempfile.gettempdir(), "\1")', content
    )

    # Add tempfile import if needed
    if modified_content != content and "tempfile" not in modified_content:
        if "import os" in modified_content:
            modified_content = re.sub(
                r"import os", r"import os\nimport tempfile", modified_content
            )
        else:
            modified_content = "import os\nimport tempfile\n\n" + modified_content

    # Replace random with secrets for cryptographic purposes - only in node.py where we know it's used
    if file_path.endswith("node.py") and "random.random()" in content:
        modified_content = re.sub(
            r"random\.random\(\)",
            r'int.from_bytes(secrets.token_bytes(4), "big") / 2**32',
            modified_content,
        )

        # Add secrets import
        if "secrets" not in modified_content:
            if "import random" in modified_content:
                modified_content = re.sub(
                    r"import random", r"import random\nimport secrets", modified_content
                )
            else:
                modified_content = "import secrets\n\n" + modified_content

    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True
    return False


def process_directory(directory: str) -> Tuple[int, int, int]:
    """Process all Python files in a directory."""
    optional_fixes = 0
    var_annotation_fixes = 0
    security_fixes = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if add_optional_annotations(file_path):
                    optional_fixes += 1
                    print(f"Fixed Optional annotations in {file_path}")

                if add_var_annotations(file_path):
                    var_annotation_fixes += 1
                    print(f"Fixed variable annotations in {file_path}")

                if fix_security_issues(file_path):
                    security_fixes += 1
                    print(f"Fixed security issues in {file_path}")

    return optional_fixes, var_annotation_fixes, security_fixes


if __name__ == "__main__":
    directories = ["models", "scripts"]

    if len(sys.argv) > 1:
        directories = sys.argv[1:]

    total_optional_fixes = 0
    total_var_fixes = 0
    total_security_fixes = 0

    for directory in directories:
        o_fixes, v_fixes, s_fixes = process_directory(directory)
        total_optional_fixes += o_fixes
        total_var_fixes += v_fixes
        total_security_fixes += s_fixes

    print(f"\nTotal files with Optional annotation fixes: {total_optional_fixes}")
    print(f"Total files with variable annotation fixes: {total_var_fixes}")
    print(f"Total files with security fixes: {total_security_fixes}")
