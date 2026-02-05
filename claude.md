# Hardfox - Firefox Hardening Tool

**Hardfox** is a Python desktop GUI application for Firefox privacy and security hardening. It provides a user-friendly interface to configure 78+ Firefox privacy settings with preset profiles and granular control.

**Tech Stack**: Python 3.6+, CustomTkinter, Tkinter, Windows-focused (cross-platform compatible)

**Key Capabilities**:
- 78+ privacy/security settings with complete metadata
- 6 preset profiles (Developer, Office Worker, Privacy Enthusiast, Laptop/Battery Saver, Gaming/Streaming, Casual Browser)
- Profile import/export (JSON)
- Firefox profile detection and management
- BASE (prefs.js) and ADVANCED (user.js) settings separation

## Architecture

```
hardfox.py              (3,579 lines) - Main GUI, CustomTkinter UI, apply logic
hardfox_metadata.py     (2,647 lines) - 78+ settings metadata, categories, presets
hardfox_widgets.py      (547 lines)   - Custom UI components (CategorySlider, SettingRow)
hardfox_profiles.py     (539 lines)   - ProfileManager, FirefoxImporter
launch_hardfox.bat      - Dependency checker & launcher
```

### Module Responsibilities

- **hardfox.py**: Main application, UI rendering, settings application logic, preset handling
- **hardfox_metadata.py**: Single source of truth for settings (descriptions, warnings, levels, categories, presets)
- **hardfox_widgets.py**: Reusable UI components (CategorySlider, SettingRow, etc.)
- **hardfox_profiles.py**: Profile detection, import/export, Firefox integration

### Core Design Patterns

**Metadata-Driven Architecture**: Settings defined with complete metadata (descriptions, warnings, levels, mechanisms)
- All settings in `SETTINGS_METADATA` dictionary in hardfox_metadata.py
- Each setting includes: `name`, `description`, `default`, `level`, `mechanism`, `category`, `subcategory`, `warning`, `prefs`
- Settings organized into categories (Performance, Privacy, Security, Features) with subcategories

**Level-Based Configuration**: BASE settings (prefs.js) vs ADVANCED settings (user.js)
- **BASE**: Applied via `prefs.js` (Firefox preferences file) - user-configurable via Firefox UI
- **ADVANCED**: Applied via `user.js` (user overrides, higher precedence) - loaded every startup

**Preset System**: 6 curated configurations stored in `PRESET_PROFILES` constant (hardfox_metadata.py):
- Developer: Minimal restrictions, debugging tools enabled
- Office Worker: Moderate privacy, browser compatibility maintained
- Privacy Enthusiast: Strong privacy, minor breakage acceptable
- Laptop/Battery Saver: Battery optimization, reduced network usage
- Gaming/Streaming: Performance-focused, WebGL/WebRTC enabled
- Casual Browser: Balanced privacy and usability

**Category Organization**: Settings organized into categories (e.g., "Tracking Protection", "Location Services") and subcategories for grouping in the UI

## Development Guidelines

### Feature Development

**Adding New Firefox Settings**:
1. Reference [arkenfox user.js](https://github.com/arkenfox/user.js) and [Mozilla documentation](https://firefox-source-docs.mozilla.org/)
2. Add setting to `SETTINGS_METADATA` dictionary in `hardfox_metadata.py`
3. Follow existing metadata structure (description, warning, level, mechanism, category)
4. Add to appropriate category/subcategory
5. Update preset profiles if the setting should be included
6. Test in Firefox to verify behavior

**Suggesting Improvements**:
- Propose better patterns when you see opportunities
- Move fast - prioritize improvements over backward compatibility
- Breaking changes are acceptable if they improve the codebase


### Code Refactoring

**Principles**:
- Maintain module separation (UI, metadata, widgets, profiles)
- Improve code clarity without breaking functionality
- Move fast - don't overly worry about backward compatibility
- Simplify complex logic when possible

**Common Refactoring Targets**:
- Reducing code duplication
- Simplifying conditional logic
- Improving function/variable naming
- Extracting reusable components to hardfox_widgets.py

### Documentation

**When to Document**:
- User-facing changes → Update `GUI_README.md`
- Complex algorithms → Add docstrings
- Breaking changes → Document in commit messages
- New settings → Include clear description and warning in metadata

### Windows-Specific Features

- **Primary Platform**: Windows with graceful fallbacks for cross-platform compatibility
- **pywinstyles**: Optional dependency for acrylic/mica window effects
- **Batch Launcher**: `launch_hardfox.bat` handles dependency installation and Python environment setup

## Testing & Verification

**Manual Testing Approach**:
1. Run `python hardfox.py` or `launch_hardfox.bat`
2. Test affected features in the GUI
3. Apply settings to a Firefox profile
4. Check generated files in Firefox profile directory:
   - `prefs.js` for BASE settings
   - `user.js` for ADVANCED settings
5. Restart Firefox and verify settings applied correctly
6. Test functionality (e.g., visit test sites for tracking protection)

**Test Resources**:
- [Cover Your Tracks](https://coveryourtracks.eff.org/) - Fingerprinting test
- [BrowserLeaks](https://browserleaks.com/) - Privacy leak detection
- [CanvasBlocker Test](https://canvasblocker.kkapsner.de/test/) - Canvas fingerprinting

## Critical Files & Constants

**Key Files**:
- `hardfox_metadata.py`: Settings definitions, categories, presets
- `hardfox.py`: Main application loop, UI rendering
- `hardfox_profiles.py`: `ProfileManager`, `FirefoxImporter` classes
- `GUI_README.md`: User documentation

**Important Constants** (hardfox_metadata.py):
- `SETTINGS_METADATA`: Dictionary of all 78+ Firefox settings
- `CATEGORIES`: List of categories for UI organization
- `PRESET_PROFILES`: 6 preset configurations
- `COLORS`: Color scheme for CustomTkinter theme (in hardfox.py)

**Important Functions** (hardfox_metadata.py):
- `get_base_settings()`: Returns settings with level="BASE"
- `get_advanced_settings()`: Returns settings with level="ADVANCED"

## Common Tasks

### Adding a New Firefox Setting

```python
# In hardfox_metadata.py SETTINGS_METADATA dictionary:
"privacy.newfeature.enabled": {
    "description": "Brief explanation of what this does",
    "warning": "Privacy trade-off or functionality impact",
    "level": "BASE",  # or "ADVANCED"
    "mechanism": "Boolean toggle",  # or "Numeric value", "Dropdown"
    "category": "Tracking Protection",
    "subcategory": "Content Blocking",
    "type": "toggle",  # or "slider", "dropdown"
    # For sliders:
    "min": 0,
    "max": 100,
    "step": 10,
    # For dropdowns:
    "options": ["option1", "option2"],
}
```

### Creating a New Category

1. Add category name to `CATEGORIES` list in `hardfox_metadata.py`
2. Add settings with `"category": "New Category Name"`
3. Update UI color scheme in `COLORS` if needed (category-specific colors)

### Modifying a Preset Profile

```python
# In hardfox_metadata.py PRESET_PROFILES dictionary:
"privacy_enthusiast": {
    "name": "Privacy Enthusiast",
    # ... other metadata ...
    # Add/modify setting values in preset
}
```

### Adding a New UI Widget

1. Create widget class in `hardfox_widgets.py`
2. Inherit from appropriate CustomTkinter base class
3. Implement reusable component with consistent styling
4. Import and use in `hardfox.py`

## External References

- **arkenfox user.js**: https://github.com/arkenfox/user.js (Privacy settings reference)
- **Mozilla Firefox Source Docs**: https://firefox-source-docs.mozilla.org/ (Official documentation)
- **CustomTkinter Docs**: https://customtkinter.tomschimansky.com/ (UI framework)

## Claude's Role

**Primary Tasks**:
- Feature development (new settings, UI improvements)
- Code refactoring (improving architecture and clarity)
- Documentation (user guides, code comments)

**Approach**:
- Reference arkenfox and Mozilla docs when adding settings
- Follow existing patterns in metadata structure
- Suggest improvements to patterns when appropriate
- Prioritize code quality and user experience
- Move fast - don't overthink backward compatibility
