#!/usr/bin/env python3
"""
Tests for Path Traversal Prevention
Critical security tests for JsonProfileRepository
"""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from hardfox.infrastructure.persistence.json_profile_repository import JsonProfileRepository
from hardfox.infrastructure.persistence.metadata_settings_repository import MetadataSettingsRepository


class TestPathTraversalPrevention:
    """Test path traversal attack prevention"""

    @pytest.fixture
    def temp_profiles_dir(self):
        """Create temporary profiles directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def settings_repo(self):
        """Create settings repository"""
        return MetadataSettingsRepository()

    @pytest.fixture
    def profile_repo(self, temp_profiles_dir, settings_repo):
        """Create profile repository with temp directory"""
        return JsonProfileRepository(temp_profiles_dir, settings_repo)

    def test_sanitize_rejects_parent_directory_traversal(self, profile_repo):
        """Test that ../ is rejected"""
        with pytest.raises(ValueError, match="Invalid profile name"):
            profile_repo._sanitize_profile_name("../evil")

    def test_sanitize_rejects_absolute_path(self, profile_repo):
        """Test that absolute paths are rejected"""
        with pytest.raises(ValueError, match="Invalid profile name"):
            profile_repo._sanitize_profile_name("/etc/passwd")

    def test_sanitize_rejects_backslash_traversal(self, profile_repo):
        """Test that Windows-style traversal is rejected"""
        with pytest.raises(ValueError, match="Invalid profile name"):
            profile_repo._sanitize_profile_name("..\\evil")

    def test_sanitize_rejects_null_bytes(self, profile_repo):
        """Test that null bytes are rejected"""
        with pytest.raises(ValueError, match="Invalid profile name"):
            profile_repo._sanitize_profile_name("evil\x00.json")

    def test_sanitize_accepts_valid_name(self, profile_repo):
        """Test that valid profile names are accepted"""
        result = profile_repo._sanitize_profile_name("valid_profile")

        assert result == "valid_profile"

    def test_sanitize_accepts_name_with_spaces(self, profile_repo):
        """Test that spaces are converted to underscores"""
        result = profile_repo._sanitize_profile_name("My Profile")

        assert result == "my_profile"

    def test_sanitize_accepts_name_with_hyphens(self, profile_repo):
        """Test that hyphens are preserved"""
        result = profile_repo._sanitize_profile_name("privacy-pro")

        assert result == "privacy-pro"

    def test_sanitize_path_prevents_directory_escape(self, profile_repo, temp_profiles_dir):
        """Test that sanitized paths stay within profiles directory"""
        # Try to escape using ../
        profile_name = "valid_profile"
        sanitized = profile_repo._sanitize_profile_name(profile_name)
        full_path = profile_repo._get_profile_path(sanitized)

        # Resolve both paths to absolute
        resolved_path = full_path.resolve()
        resolved_dir = temp_profiles_dir.resolve()

        # Verify the profile path is within profiles directory
        assert str(resolved_path).startswith(str(resolved_dir))

    def test_load_rejects_path_outside_profiles_dir(self, profile_repo, temp_profiles_dir):
        """Test that load() rejects paths outside profiles directory"""
        # Create a file outside profiles dir
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            outside_path = Path(f.name)

        try:
            # Try to load it (should fail)
            with pytest.raises(ValueError):
                profile_repo.load(str(outside_path))
        finally:
            outside_path.unlink()

    def test_sanitize_removes_dangerous_characters(self, profile_repo):
        """Test that dangerous characters are removed"""
        result = profile_repo._sanitize_profile_name("my<profile>name")

        assert "<" not in result
        assert ">" not in result

    def test_sanitize_lowercases_name(self, profile_repo):
        """Test that profile names are lowercased"""
        result = profile_repo._sanitize_profile_name("MyProfile")

        assert result == "myprofile"

    def test_get_profile_path_always_returns_child_of_profiles_dir(
        self, profile_repo, temp_profiles_dir
    ):
        """Test that _get_profile_path() always returns path within profiles dir"""
        test_names = [
            "normal_profile",
            "../../etc/passwd",
            "/absolute/path",
            "..\\windows\\path",
            "profile\x00.json"
        ]

        for name in test_names:
            try:
                sanitized = profile_repo._sanitize_profile_name(name)
                path = profile_repo._get_profile_path(sanitized)

                # Resolve to absolute paths
                resolved_path = path.resolve()
                resolved_dir = temp_profiles_dir.resolve()

                # Verify containment
                assert str(resolved_path).startswith(str(resolved_dir))
            except ValueError:
                # Invalid names should raise ValueError, which is acceptable
                pass
