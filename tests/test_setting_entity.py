#!/usr/bin/env python3
"""
Tests for Setting Entity Validation
Ensures setting validation works correctly
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from hardzilla.domain.entities.setting import Setting
from hardzilla.domain.enums import SettingLevel, SettingType


class TestSettingValidation:
    """Test Setting entity validation"""

    def test_toggle_setting_valid(self):
        """Test creating valid toggle setting"""
        setting = Setting(
            key="test.toggle",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test"
        )

        assert setting.value is True
        assert setting.setting_type == SettingType.TOGGLE

    def test_slider_setting_valid(self):
        """Test creating valid slider setting"""
        setting = Setting(
            key="test.slider",
            value=50,
            level=SettingLevel.BASE,
            setting_type=SettingType.SLIDER,
            category="test",
            min_value=0,
            max_value=100,
            step=1
        )

        assert setting.value == 50
        assert setting.min_value == 0
        assert setting.max_value == 100

    def test_slider_missing_min_max_raises(self):
        """Test slider without min/max raises error"""
        with pytest.raises(ValueError, match="must have min_value and max_value"):
            Setting(
                key="test.slider",
                value=50,
                level=SettingLevel.BASE,
                setting_type=SettingType.SLIDER,
                category="test"
            )

    def test_slider_value_out_of_range_raises(self):
        """Test slider value out of range raises error"""
        with pytest.raises(ValueError, match="out of range"):
            Setting(
                key="test.slider",
                value=150,  # Out of range
                level=SettingLevel.BASE,
                setting_type=SettingType.SLIDER,
                category="test",
                min_value=0,
                max_value=100,
                step=1
            )

    def test_dropdown_setting_valid(self):
        """Test creating valid dropdown setting"""
        setting = Setting(
            key="test.dropdown",
            value="Option1",
            level=SettingLevel.BASE,
            setting_type=SettingType.DROPDOWN,
            category="test",
            options=["Option1", "Option2", "Option3"]
        )

        assert setting.value == "Option1"
        assert setting.options == ["Option1", "Option2", "Option3"]

    def test_dropdown_missing_options_raises(self):
        """Test dropdown without options raises error"""
        with pytest.raises(ValueError, match="must have options"):
            Setting(
                key="test.dropdown",
                value="Option1",
                level=SettingLevel.BASE,
                setting_type=SettingType.DROPDOWN,
                category="test"
            )

    def test_dropdown_invalid_value_raises(self):
        """Test dropdown with invalid value raises error"""
        with pytest.raises(ValueError, match="not in options"):
            Setting(
                key="test.dropdown",
                value="InvalidOption",
                level=SettingLevel.BASE,
                setting_type=SettingType.DROPDOWN,
                category="test",
                options=["Option1", "Option2"]
            )

    def test_breakage_score_in_range(self):
        """Test valid breakage score"""
        setting = Setting(
            key="test.setting",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test",
            breakage_score=5
        )

        assert setting.breakage_score == 5

    def test_breakage_score_out_of_range_raises(self):
        """Test breakage score out of range raises error"""
        with pytest.raises(ValueError, match="must be 0-10"):
            Setting(
                key="test.setting",
                value=True,
                level=SettingLevel.BASE,
                setting_type=SettingType.TOGGLE,
                category="test",
                breakage_score=15  # Out of range
            )

    def test_visibility_valid(self):
        """Test valid visibility values"""
        setting1 = Setting(
            key="test.setting",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test",
            visibility="core"
        )
        setting2 = Setting(
            key="test.setting2",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test",
            visibility="advanced"
        )

        assert setting1.visibility == "core"
        assert setting2.visibility == "advanced"

    def test_visibility_invalid_raises(self):
        """Test invalid visibility raises error"""
        with pytest.raises(ValueError, match="must be 'core' or 'advanced'"):
            Setting(
                key="test.setting",
                value=True,
                level=SettingLevel.BASE,
                setting_type=SettingType.TOGGLE,
                category="test",
                visibility="invalid"
            )

    def test_clone_with_value(self):
        """Test cloning setting with new value"""
        original = Setting(
            key="test.setting",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test"
        )

        cloned = original.clone_with_value(False)

        assert cloned.value is False
        assert cloned.key == original.key
        assert cloned.level == original.level
        assert original.value is True  # Original unchanged

    def test_to_firefox_pref_boolean(self):
        """Test converting boolean to Firefox pref"""
        setting = Setting(
            key="test.bool",
            value=True,
            level=SettingLevel.BASE,
            setting_type=SettingType.TOGGLE,
            category="test"
        )

        pref = setting.to_firefox_pref()

        assert 'user_pref("test.bool", true);' in pref

    def test_to_firefox_pref_integer(self):
        """Test converting integer to Firefox pref"""
        setting = Setting(
            key="test.int",
            value=42,
            level=SettingLevel.BASE,
            setting_type=SettingType.SLIDER,
            category="test",
            min_value=0,
            max_value=100,
            step=1
        )

        pref = setting.to_firefox_pref()

        assert 'user_pref("test.int", 42);' in pref

    def test_to_firefox_pref_string(self):
        """Test converting string to Firefox pref"""
        setting = Setting(
            key="test.string",
            value="hello",
            level=SettingLevel.BASE,
            setting_type=SettingType.INPUT,
            category="test"
        )

        pref = setting.to_firefox_pref()

        assert 'user_pref("test.string", "hello");' in pref
