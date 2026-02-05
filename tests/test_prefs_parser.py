#!/usr/bin/env python3
"""
Tests for PrefsParser
Critical component that parses and writes Firefox prefs.js files
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hardfox.infrastructure.parsers.prefs_parser import PrefsParser


class TestPrefsParser:
    """Test PrefsParser roundtrip and edge cases"""

    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return PrefsParser()

    @pytest.fixture
    def temp_file(self):
        """Create temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_parse_boolean_true(self, parser, temp_file):
        """Test parsing boolean true value"""
        temp_file.write_text('user_pref("test.bool", true);', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.bool" in result
        assert result["test.bool"] is True

    def test_parse_boolean_false(self, parser, temp_file):
        """Test parsing boolean false value"""
        temp_file.write_text('user_pref("test.bool", false);', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.bool" in result
        assert result["test.bool"] is False

    def test_parse_integer(self, parser, temp_file):
        """Test parsing integer value"""
        temp_file.write_text('user_pref("test.int", 42);', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.int" in result
        assert result["test.int"] == 42

    def test_parse_negative_integer(self, parser, temp_file):
        """Test parsing negative integer"""
        temp_file.write_text('user_pref("test.int", -10);', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.int" in result
        assert result["test.int"] == -10

    def test_parse_string(self, parser, temp_file):
        """Test parsing string value"""
        temp_file.write_text('user_pref("test.string", "hello");', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.string" in result
        assert result["test.string"] == "hello"

    def test_parse_string_with_semicolon(self, parser, temp_file):
        """Test parsing string containing semicolon"""
        temp_file.write_text('user_pref("test.string", "hello;world");', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.string" in result
        assert result["test.string"] == "hello;world"

    def test_parse_string_with_escaped_quotes(self, parser, temp_file):
        """Test parsing string with escaped quotes"""
        temp_file.write_text(r'user_pref("test.string", "hello\"world");', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.string" in result
        assert result["test.string"] == 'hello"world'

    def test_parse_string_with_backslash(self, parser, temp_file):
        """Test parsing string with backslashes"""
        temp_file.write_text(r'user_pref("test.path", "C:\\Users\\Test");', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.path" in result
        assert result["test.path"] == "C:\\Users\\Test"

    def test_parse_multiple_prefs(self, parser, temp_file):
        """Test parsing multiple preferences"""
        content = '''
user_pref("test.bool", true);
user_pref("test.int", 42);
user_pref("test.string", "hello");
'''
        temp_file.write_text(content, encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert len(result) == 3
        assert result["test.bool"] is True
        assert result["test.int"] == 42
        assert result["test.string"] == "hello"

    def test_parse_with_pref_prefix(self, parser, temp_file):
        """Test parsing with pref() prefix instead of user_pref()"""
        temp_file.write_text('pref("test.bool", true);', encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.bool" in result
        assert result["test.bool"] is True

    def test_parse_skips_malformed_line(self, parser, temp_file):
        """Test parser continues after malformed line"""
        content = '''
user_pref("test.valid1", true);
this is malformed garbage
user_pref("test.valid2", false);
'''
        temp_file.write_text(content, encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert "test.valid1" in result
        assert "test.valid2" in result
        assert len(result) == 2

    def test_parse_skips_comments(self, parser, temp_file):
        """Test parser skips comment lines"""
        content = '''
// This is a comment
user_pref("test.bool", true);
/* Multi-line comment */
user_pref("test.int", 42);
'''
        temp_file.write_text(content, encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert len(result) == 2

    def test_write_prefs_boolean(self, parser, temp_file):
        """Test writing boolean preference"""
        prefs = {"test.bool": True}

        parser.write_prefs(prefs, temp_file, use_user_pref=True)

        content = temp_file.read_text(encoding='utf-8')
        assert 'user_pref("test.bool", true);' in content

    def test_write_prefs_integer(self, parser, temp_file):
        """Test writing integer preference"""
        prefs = {"test.int": 42}

        parser.write_prefs(prefs, temp_file, use_user_pref=True)

        content = temp_file.read_text(encoding='utf-8')
        assert 'user_pref("test.int", 42);' in content

    def test_write_prefs_string(self, parser, temp_file):
        """Test writing string preference"""
        prefs = {"test.string": "hello"}

        parser.write_prefs(prefs, temp_file, use_user_pref=True)

        content = temp_file.read_text(encoding='utf-8')
        assert 'user_pref("test.string", "hello");' in content

    def test_write_prefs_with_pref_prefix(self, parser, temp_file):
        """Test writing with pref() prefix"""
        prefs = {"test.bool": True}

        parser.write_prefs(prefs, temp_file, use_user_pref=False)

        content = temp_file.read_text(encoding='utf-8')
        assert 'pref("test.bool", true);' in content

    def test_roundtrip_boolean(self, parser, temp_file):
        """Test parse and write roundtrip for boolean"""
        original = {"test.bool": True}

        parser.write_prefs(original, temp_file, use_user_pref=True)
        parsed = parser.parse_file(temp_file)

        assert parsed == original

    def test_roundtrip_integer(self, parser, temp_file):
        """Test parse and write roundtrip for integer"""
        original = {"test.int": 42}

        parser.write_prefs(original, temp_file, use_user_pref=True)
        parsed = parser.parse_file(temp_file)

        assert parsed == original

    def test_roundtrip_string(self, parser, temp_file):
        """Test parse and write roundtrip for string"""
        original = {"test.string": "hello world"}

        parser.write_prefs(original, temp_file, use_user_pref=True)
        parsed = parser.parse_file(temp_file)

        assert parsed == original

    def test_roundtrip_complex(self, parser, temp_file):
        """Test roundtrip with multiple types"""
        original = {
            "test.bool": True,
            "test.int": 42,
            "test.string": "hello",
            "test.negative": -10
        }

        parser.write_prefs(original, temp_file, use_user_pref=True)
        parsed = parser.parse_file(temp_file)

        assert parsed == original

    def test_parse_empty_file(self, parser, temp_file):
        """Test parsing empty file"""
        temp_file.write_text("", encoding='utf-8')

        result = parser.parse_file(temp_file)

        assert result == {}

    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("/nonexistent/file.js"))

    def test_write_empty_prefs(self, parser, temp_file):
        """Test writing empty prefs dict"""
        parser.write_prefs({}, temp_file, use_user_pref=True)

        content = temp_file.read_text(encoding='utf-8')
        # File contains header comments but no pref lines
        for line in content.strip().splitlines():
            assert line.startswith("//") or line.strip() == "", f"Unexpected pref line: {line}"

    def test_write_preserves_encoding(self, parser, temp_file):
        """Test writing preserves UTF-8 encoding"""
        prefs = {"test.unicode": "hello 世界"}

        parser.write_prefs(prefs, temp_file, use_user_pref=True)
        parsed = parser.parse_file(temp_file)

        assert parsed["test.unicode"] == "hello 世界"
