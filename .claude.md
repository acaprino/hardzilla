# Hardfox v4.0 - Firefox Privacy & Security Configurator

**Architecture:** Clean Architecture (Domain-Driven Design)
**Pattern:** MVVM with Repository + Use Case patterns
**Tech:** Python 3.9+, CustomTkinter, 58 Python files across 6 layers
**Innovation:** Intent-based configuration (3 questions → 78 settings)
**Status:** Production-ready, 97% complete (30/31 tasks)

---

## What This Is

Hardfox transforms Firefox into a privacy-focused browser by configuring 78+ about:config settings automatically. Unlike traditional tools that require manual configuration of each setting, v4 uses **intent-based analysis**: users answer 3 simple questions about their browsing habits, and the IntentAnalyzer generates an optimized configuration.


---

## Architecture

### Layer Structure

```
hardfox/
├── domain/              # Pure business logic (no dependencies)
│   ├── entities/       # Setting, Profile (core domain models)
│   ├── enums/          # SettingLevel (BASE/ADVANCED), SettingType
│   └── repositories/   # Abstract interfaces (ISettingsRepository, etc.)
│
├── application/         # Business use cases & services
│   ├── use_cases/      # 5 use cases (ApplySettings, GenerateRecommendation, etc.)
│   ├── services/       # IntentAnalyzer (CORE INNOVATION)
│   └── mappers/        # Data transformation (Setting ↔ Firefox pref)
│
├── infrastructure/      # External systems integration
│   ├── parsers/        # PrefsParser (robust Firefox prefs.js parser)
│   └── persistence/    # 3 repositories (Firefox files, JSON profiles, Metadata)
│
├── presentation/        # MVVM UI layer
│   ├── views/          # 3 wizard screens (Setup, Customize, Apply)
│   ├── view_models/    # Observable state (4 ViewModels)
│   ├── controllers/    # Flow coordination (2 controllers + ScreenNavigator)
│   ├── widgets/        # Reusable components (SettingRow, EnhancedWidgets)
│   ├── utils/          # KeyboardHandler (/, F1, Ctrl+S shortcuts)
│   └── theme.py        # Professional visual theme system
│
└── metadata/            # Source of truth
    └── settings_metadata.py  # All 78+ settings definitions (2,647 lines)
```

**Dependencies flow:** Presentation → Application → Domain ← Infrastructure
**Never:** Domain depends on Infrastructure or Presentation
**Pattern:** Dependency Inversion (interfaces in domain, implementations in infrastructure)

---

## Core Patterns

### 1. MVVM (Model-View-ViewModel)
- **Views:** UI rendering only (`hardfox/presentation/views/`)
- **ViewModels:** Observable state, no UI logic (`hardfox/presentation/view_models/`)
- **Controllers:** Wire views to use cases (`hardfox/presentation/controllers/`)
- **Why:** Decouples UI from business logic, enables testing without GUI

### 2. Repository Pattern
- **Interfaces:** `hardfox/domain/repositories/` (abstract)
- **Implementations:** `hardfox/infrastructure/persistence/` (concrete)
- **Three Repos:** FirefoxFileRepository, JsonProfileRepository, MetadataSettingsRepository
- **Why:** Abstracts data access, easy to test with mocks

### 3. Use Case Pattern
- **Location:** `hardfox/application/use_cases/`
- **Five Use Cases:** ApplySettings, GenerateRecommendation, ImportFromFirefox, LoadProfile, SaveProfile
- **Why:** Each user action = one testable class, clear business logic

### 4. Dependency Injection
- **Composition Root:** `hardfox_gui.py` (GUI), `hardfox_main.py` (CLI)
- **Wire dependencies:** Repositories → Use Cases → Controllers → Views
- **Why:** Loose coupling, testable components

---

## Core Innovation: Intent-Based Configuration

**Traditional Approach:** User configures 78+ settings manually
**Hardfox v4:** User answers 3 questions, IntentAnalyzer generates optimal config

### The 3 Questions
1. **Use Cases:** What do you use Firefox for? (Banking, Shopping, Development, Privacy, etc.)
2. **Privacy Level:** How important is privacy? (Basic, Moderate, Strong, Maximum)
3. **Breakage Tolerance:** Comfortable troubleshooting? (0-100% slider)

### IntentAnalyzer Service
**Location:** `hardfox/application/services/intent_analyzer.py`

**How It Works:**
1. Analyzes user intent (use cases + privacy level + tolerance)
2. Selects base preset template (Developer, Office, Privacy, etc.)
3. Applies rule-based adjustments:
   - Banking → Enable strict fingerprinting protection
   - Shopping → Allow payment processor cookies
   - Privacy=Strong → DoH, strict tracking protection
   - Breakage=Low → Keep WebRTC, relax some restrictions
4. Returns complete Profile with all 78+ settings configured

**Why This Matters:** Users get expert-level configuration without needing to understand about:config.

---

## Key Files

### Entry Points
- **`hardfox_gui.py`** - GUI application (3-screen wizard, MVVM wiring)
- **`hardfox_main.py`** - CLI demo (dependency injection composition root)
- **`launch_hardfox.bat`** - Windows launcher with dependency checks

### Metadata (Source of Truth)
- **`hardfox/metadata/settings_metadata.py`** - All 78+ settings definitions
  - Each setting: key, value, level, type, category, description, intent_tags, breakage_score
  - Used by IntentAnalyzer for intent matching
  - Used by repositories for validation

### Domain Model
- **`hardfox/domain/entities/setting.py`** - Setting entity (validation, Firefox pref conversion)
- **`hardfox/domain/entities/profile.py`** - Profile entity (collection of settings)
- **`hardfox/domain/enums/setting_level.py`** - BASE (user-editable) vs ADVANCED (locked)

### Core Services
- **`hardfox/application/services/intent_analyzer.py`** - Intent → Config engine
- **`hardfox/infrastructure/parsers/prefs_parser.py`** - Robust Firefox prefs.js parser
- **`hardfox/infrastructure/persistence/firefox_file_repository.py`** - Firefox file I/O

### UI Layer
- **`hardfox/presentation/views/setup_view.py`** - Screen 1 (Intent questions)
- **`hardfox/presentation/views/customize_view.py`** - Screen 2 (78+ settings browser)
- **`hardfox/presentation/views/apply_view.py`** - Screen 3 (Apply to Firefox)
- **`hardfox/presentation/widgets/setting_row.py`** - Individual setting control
- **`hardfox/presentation/theme.py`** - Professional visual theme


---

## Development Workflow

### Running the Application

```bash
# GUI (recommended for testing full wizard)
python hardfox_gui.py

# CLI demo (quick testing)
python hardfox_main.py

# Windows launcher (checks dependencies)
launch_hardfox.bat

# Settings browser demo (browse all 78+ settings)
python demo_customize_screen.py
```

### Testing

```bash
# All tests
pytest tests/ -v

# Parser unit tests (20 tests, robust edge cases)
pytest tests/test_prefs_parser.py -v

# Integration tests (file I/O, repositories)
pytest tests/test_integration_file_io.py -v
```

**Testing Philosophy:** Add tests for new features, maintain 80%+ coverage on business logic.

---

## Two-Level Configuration System

**BASE Settings:**
- Stored in: `prefs.js` (Firefox's main config file)
- User can change: Yes (via Firefox UI or about:config)
- Applied: On first launch or when changed
- Use for: Settings users should control (cookie behavior, startup page)

**ADVANCED Settings:**
- Stored in: `user.js` (loaded on every Firefox start)
- User can change: No (Hardfox locks them)
- Applied: Every Firefox restart (overrides user changes)
- Use for: Security-critical settings (fingerprinting resistance, WebRTC)

**Why Two Levels:** BASE gives flexibility, ADVANCED ensures security baseline.

---

## Adding New Settings

1. **Edit Metadata**
   - File: `hardfox/metadata/settings_metadata.py`
   - Add to `SETTINGS_METADATA` dictionary

2. **Setting Structure**
   ```python
   "privacy.example.setting": Setting(
       key="privacy.example.setting",
       value=True,                           # Default value
       level=SettingLevel.ADVANCED,          # BASE or ADVANCED
       setting_type=SettingType.TOGGLE,      # TOGGLE, SLIDER, DROPDOWN, INPUT
       category="privacy",                    # Category for UI grouping
       description="Clear description...",   # User-facing explanation
       intent_tags=["privacy", "banking"],   # For IntentAnalyzer matching
       breakage_score=5,                     # 0-10 (likelihood to break sites)
       visibility="core"                     # "core" or "advanced"
   )
   ```

3. **IntentAnalyzer Integration**
   - If setting should be auto-selected based on intent, add relevant `intent_tags`
   - IntentAnalyzer matches user's use cases against these tags

4. **Testing**
   - Validate setting appears in GUI (run `demo_customize_screen.py`)
   - Test apply to Firefox (create test profile)

---

## Common Tasks

### Modify Intent Analysis Rules
- **File:** `hardfox/application/services/intent_analyzer.py`
- **Method:** `_apply_intent_adjustments()`
- **Pattern:** Add conditional logic based on use cases, privacy level, tolerance

### Add New UI Widget
- **Location:** `hardfox/presentation/widgets/`
- **Pattern:** Inherit from `ctk.CTkFrame` or use composition
- **Theme:** Import `Theme` from `hardfox/presentation/theme.py`
- **Example:** See `SettingRow`, `EnhancedWidgets`

### Add New Use Case
- **Location:** `hardfox/application/use_cases/`
- **Pattern:** Class with `execute()` method, inject repositories via constructor
- **Example:** See `ApplySettingsUseCase`, `GenerateRecommendationUseCase`

### Modify Firefox File Handling
- **Parser:** `hardfox/infrastructure/parsers/prefs_parser.py`
- **Repository:** `hardfox/infrastructure/persistence/firefox_file_repository.py`
- **Tests:** `tests/test_prefs_parser.py` (add edge case tests)

---

## Architecture Guidelines

### Layer Dependencies
✅ **DO:** Presentation → Application → Domain ← Infrastructure
❌ **DON'T:** Domain → Infrastructure (breaks clean architecture)
❌ **DON'T:** Skip layers (Presentation → Infrastructure directly)

### Repository Pattern
✅ **DO:** Define interface in `domain/repositories/`
✅ **DO:** Implement in `infrastructure/persistence/`
❌ **DON'T:** Implement data access directly in use cases

### ViewModels
✅ **DO:** Store observable state, notify observers on change
✅ **DO:** Keep business logic in use cases
❌ **DON'T:** Put UI logic in ViewModels
❌ **DON'T:** Access repositories directly from ViewModels

### Use Cases
✅ **DO:** One class per user action
✅ **DO:** Inject dependencies via constructor
✅ **DO:** Return domain entities, not DTOs
❌ **DON'T:** Create God use cases (keep focused)

---

## Known Gotchas

1. **Font Weight:** CustomTkinter only accepts `"normal"` or `"bold"`, NOT numeric values like `"600"`
2. **Firefox Path Spaces:** Always quote paths with spaces in bash commands
3. **Backup Timestamps:** Use `sleep(1.1)` between backups to ensure different filenames
4. **Dropdown Values:** Must match options exactly (case-sensitive)
5. **Slider Settings:** Must have `min_value`, `max_value`, `step` defined

---

## Testing Notes

### Parser Tests (20 tests)
- **Coverage:** Boolean, string, integer values
- **Edge Cases:** Quoted strings with semicolons, malformed lines, encoding issues
- **Philosophy:** Fail-safe parsing (skip malformed, log warning, continue)

### Integration Tests
- **File I/O:** Atomic backups, merge vs replace modes
- **Repositories:** Load, save, validation
- **Use Cases:** End-to-end workflows

### Manual Testing
- **GUI Workflow:** Run `hardfox_gui.py`, complete 3-screen wizard
- **Settings Browser:** Run `demo_customize_screen.py`, verify all 78+ settings
- **Firefox Apply:** Create test profile, apply settings, verify in about:config

---

## Keyboard Shortcuts

**Global:**
- `/` or `Ctrl+F` - Focus search
- `F1` - Show keyboard shortcuts help
- `Escape` - Clear search
- `Tab` - Navigate through elements

**Apply Screen:**
- `Ctrl+S` - Apply settings to Firefox

**Settings Browser:**
- Type to search in real-time
- Click category headers to expand/collapse

---

## External Resources

**Firefox Configuration:**
- [arkenfox user.js](https://github.com/arkenfox/user.js) - Comprehensive Firefox hardening reference
- [Mozilla Firefox Preferences](https://kb.mozillazine.org/About:config_entries) - Official preference documentation

**Privacy Testing:**
- [Cover Your Tracks](https://coveryourtracks.eff.org/) - Browser fingerprinting test
- [BrowserLeaks](https://browserleaks.com/) - Comprehensive privacy testing suite

**UI Framework:**
- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/) - Modern tkinter library

---

## Documentation

- **`README.md`** - Quick start guide, feature overview
- **`GUI_IMPROVEMENTS.md`** - Visual design enhancements documentation
- **`ARCHITECTURE.md`** - *(TBD)* Comprehensive architecture documentation

---

## Project Status

**Version:** 4.0
**Completion:** 97% (30/31 tasks)
**Lines of Code:** ~7,000 across 58 files
**Test Coverage:** 80%+ on business logic
**Status:** Production-ready

**Remaining:** Manual testing checklist (optional, for beta phase)

---

*Last Updated: 2026-02-01 - Complete rewrite for v4 clean architecture*
