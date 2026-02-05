#!/usr/bin/env python3
"""
Firefox Prefs Parser
Robust line-by-line parser for prefs.js and user.js files with error recovery
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class PrefsParser:
    """
    Parses Firefox preference files (prefs.js, user.js) with robust error handling.

    Handles:
    - user_pref() and pref() function calls
    - Boolean values (true/false)
    - Integer and float numbers
    - Quoted strings with escape sequences
    - Malformed lines (skip with warning)
    - Encoding issues (UTF-8 with Latin-1 fallback)
    - Comments and empty lines
    """

    # Regex patterns for parsing pref lines
    PREF_PATTERN = re.compile(
        r'^\s*(?:user_)?pref\s*\(\s*"([^"]+)"\s*,\s*(.+?)\s*\)\s*;?\s*$',
        re.MULTILINE
    )

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Firefox preference file.

        Args:
            file_path: Path to prefs.js or user.js file

        Returns:
            Dictionary of preference key -> value

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Preference file not found: {file_path}")

        # Try UTF-8 first, fallback to Latin-1
        content = self._read_file_with_fallback(file_path)

        prefs = {}
        for line_num, line in enumerate(content.splitlines(), start=1):
            try:
                key, value = self._parse_line(line)
                if key is not None:
                    prefs[key] = value
            except Exception as e:
                logger.warning(f"Skipping malformed line {line_num} in {file_path.name}: {e}")
                logger.debug(f"Malformed line content: {line}")

        logger.info(f"Parsed {len(prefs)} preferences from {file_path.name}")
        return prefs

    def _read_file_with_fallback(self, file_path: Path) -> str:
        """Read file with UTF-8, fallback to Latin-1 on encoding errors"""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decode failed for {file_path.name}, trying Latin-1")
            return file_path.read_text(encoding='latin-1')

    def _parse_line(self, line: str) -> Tuple[Optional[str], Optional[Any]]:
        """
        Parse a single preference line.

        Args:
            line: Single line from pref file

        Returns:
            Tuple of (key, value) or (None, None) if not a pref line
        """
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            return None, None

        # Match pref() or user_pref() pattern
        match = self.PREF_PATTERN.match(line)
        if not match:
            return None, None

        key = match.group(1)
        value_str = match.group(2).strip()

        # Parse value
        value = self._parse_value(value_str)
        return key, value

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse JavaScript value to Python type.

        Args:
            value_str: String representation of value

        Returns:
            Parsed Python value (bool, int, float, or str)

        Raises:
            ValueError: If value format is invalid
        """
        value_str = value_str.strip().rstrip(';')

        # Boolean values
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False

        # String values (quoted)
        if value_str.startswith('"') and value_str.endswith('"'):
            return self._parse_quoted_string(value_str[1:-1])

        # Numeric values
        try:
            # Try integer first
            if '.' not in value_str:
                return int(value_str)
            # Then float
            return float(value_str)
        except ValueError:
            pass

        raise ValueError(f"Cannot parse value: {value_str}")

    def _parse_quoted_string(self, escaped_str: str) -> str:
        """
        Parse escaped string value.

        Args:
            escaped_str: String content (without surrounding quotes)

        Returns:
            Unescaped string
        """
        # FIX [MED-005]: Handle escape sequences in correct order
        # Process \\\\ FIRST to avoid double-processing (e.g., \\n becoming newline)
        return (escaped_str
                .replace('\\\\', '\x00')    # Placeholder for literal backslash
                .replace('\\n', '\n')
                .replace('\\t', '\t')
                .replace('\\r', '\r')
                .replace('\\"', '"')
                .replace('\x00', '\\'))     # Restore literal backslashes

    def write_prefs(self, prefs: Dict[str, Any], file_path: Path, use_user_pref: bool = True) -> None:
        """
        Write preferences to a file.

        Args:
            prefs: Dictionary of preference key -> value
            file_path: Path to write to
            use_user_pref: If True, use user_pref(), else use pref()
        """
        prefix = "user_pref" if use_user_pref else "pref"
        lines = []

        # Add header comment
        lines.append("// Hardfox Firefox Configuration")
        lines.append("// Generated by Hardfox")
        lines.append("")

        # Write each preference
        for key, value in sorted(prefs.items()):
            formatted_value = self._format_value_for_js(value)
            lines.append(f'{prefix}("{key}", {formatted_value});')

        # Write to file with UTF-8 encoding
        file_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        logger.info(f"Wrote {len(prefs)} preferences to {file_path.name}")

    def _format_value_for_js(self, value: Any) -> str:
        """
        Format Python value as JavaScript value.

        Args:
            value: Python value to format

        Returns:
            JavaScript-formatted string
        """
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            # Escape special characters
            escaped = (value
                       .replace('\\', '\\\\')
                       .replace('"', '\\"')
                       .replace('\n', '\\n')
                       .replace('\t', '\\t')
                       .replace('\r', '\\r'))
            return f'"{escaped}"'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            raise ValueError(f"Unsupported value type for JavaScript: {type(value)}")

    def merge_prefs(
        self,
        base_prefs: Dict[str, Any],
        new_prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge new preferences into base preferences.

        Args:
            base_prefs: Existing preferences
            new_prefs: New preferences to merge in

        Returns:
            Merged preferences dictionary
        """
        merged = base_prefs.copy()
        merged.update(new_prefs)
        return merged
