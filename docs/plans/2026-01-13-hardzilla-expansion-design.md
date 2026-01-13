# Hardzilla Expansion Design

**Date:** 2026-01-13
**Status:** Approved
**Scope:** Full expansion with custom profiles

---

## Overview

Expand Hardzilla from ~50 privacy-focused settings to ~100+ comprehensive Firefox hardening settings covering Performance, Privacy, Security, and Experimental Features, with a new profile management system.

---

## New Features Summary

### 1. Performance Section (NEW)

**Cache & Memory Tab:**
- Disk cache toggle + size (100MB/256MB/512MB/1GB)
- RAM cache toggle + size (64MB/256MB/512MB/1GB)
- Session history entries (5/25/50)
- Cached pages in memory (1/4/8)
- Session save interval (10s/60s/120s/600s)

**Processes & GPU Tab:**
- Content processes (2/6/12)
- Isolated site processes (1/2/4)
- WebRender compositor
- Force GPU acceleration
- Separate GPU process
- Hardware video decoding
- Force WebGL
- WebGPU
- Max frame rate (30/60/144/unlimited)

**Network Performance (in Network tab):**
- Max HTTP connections (256/1200/1800)
- Connections per server (4/8/10)
- Speculative connections (0/8/20)

### 2. Experimental Features Section (NEW)

**UI & Tabs:**
- Tab grouping
- AI-powered tab grouping
- New sidebar design
- Vertical tab bar

**AI Features:**
- ML features toggle
- AI chatbot sidebar
- AI link previews
- Visual search

**Graphics & Media:**
- WebGPU API
- AVIF image format
- Animated AVIF
- JPEG XL format (Nightly)

**CSS Experimental:**
- Scroll-driven animations
- CSS Masonry layout
- CSS :has() selector

**DOM & Network:**
- Sanitizer API
- HTTP/3 protocol
- WebTransport API

### 3. Profile Library & Custom Profiles

**6 Preset Profiles:**
1. Developer - Max Power, Balanced Privacy, Bleeding Edge Features
2. Office - Balanced all categories
3. Privacy Enthusiast - Balanced Perf, Paranoid Privacy, Conservative Features
4. Laptop - Battery Saver Perf, Balanced Privacy, Conservative Features
5. Gaming - Max Power, Open Privacy, Bleeding Edge Features
6. Casual - Balanced all categories

**Custom Profile Features:**
- Create new profiles from scratch or copy existing
- Import from current Firefox (scan prefs.js)
- Save with name, description, tags
- Export/Import as JSON
- Duplicate, edit, delete

### 4. Granular Editor

**Features:**
- Full list of all ~100+ flags
- Search by name, description, or pref name
- Filter by category, impact level, modified status
- Collapsible category sections

**Flag Documentation (per setting):**
- Inline short description (1-2 sentences)
- Expandable details panel with:
  - Full description
  - Firefox pref name
  - Impact level (High/Medium/Low)
  - Compatibility warning (None/Minor/Major)
  - Recommended value per profile type

### 5. Enhanced Quick Start

**3-Tier Category Sliders:**
- Performance: Battery Saver ↔ Balanced ↔ Max Power
- Privacy: Open ↔ Balanced ↔ Paranoid
- Features: Conservative ↔ Balanced ↔ Bleeding Edge

**Slider Behavior:**
- 5 discrete positions
- Preview text updates with slider
- Independent sliders (mix any combination)
- Apply Sliders button

**Use-Case Preset Buttons:**
- One-click applies all three sliders
- Visual feedback on slider positions

### 6. Enhanced Summary

**Category Overview:**
- Visual meters showing spectrum position
- Quick description of current stance

**Changes from Default:**
- Grouped by impact (High/Medium/Low)
- Expandable sections
- Count of modifications

**Compatibility Warnings:**
- List settings that may break sites
- Percentage estimate of affected sites

**Export Options:**
- Export JSON (for Hardzilla)
- Export user.js (raw Firefox prefs)
- Preview user.js before applying

### 7. Firefox Import

**Import Current Settings:**
- Scan prefs.js from selected Firefox profile
- Match against Hardzilla's ~100+ known settings
- Create "Imported [date]" custom profile
- Show count of recognized settings

---

## Data Model

### Settings Metadata Structure

```python
SETTINGS_METADATA = {
    "browser.cache.memory.capacity": {
        "name": "RAM Cache",
        "category": "performance",
        "subcategory": "cache",
        "short": "Keep cache in memory for faster access",
        "full": "Higher values improve page load speed but consume more system memory. Recommended for systems with 8GB+.",
        "pref": "browser.cache.memory.capacity",
        "type": "choice",  # toggle, choice, number
        "impact": "medium",  # low, medium, high
        "compatibility": "none",  # none, minor, major
        "values": [65536, 262144, 524288],
        "labels": ["64MB", "256MB", "512MB"],
        "default": 262144,
        "recommended": {
            "max_power": 524288,
            "balanced": 262144,
            "battery": 65536,
            "paranoid": 262144,
            "open": 262144
        }
    }
}
```

### Profile Structure

```python
{
    "name": "My Work Setup",
    "description": "Balanced with extra privacy for work",
    "tags": ["work", "privacy"],
    "created": "2026-01-13T10:30:00",
    "modified": "2026-01-13T14:22:00",
    "base": "balanced",  # or null for custom
    "version": "3.0",
    "settings": {
        "browser.cache.memory.capacity": 524288,
        "privacy.resistFingerprinting": true,
        # ... all modified settings
    }
}
```

---

## UI Structure

### Tab Organization (11 tabs)

```
QUICK SETUP
├── Quick Start (enhanced with sliders + 6 presets)
├── Profile Library (NEW)

PERFORMANCE (NEW)
├── Cache & Memory
├── Processes & GPU

PRIVACY (existing, expanded)
├── Session & Startup
├── Data & Cleanup
├── Cookies
├── Tracking Protection

SECURITY (existing, expanded)
├── Network & DNS
├── Permissions

FEATURES (NEW)
├── Experimental

EXTRAS (existing)
├── Extensions
├── Userscripts

Summary (enhanced)
```

---

## Implementation Notes

### Files to Modify
- `hardzilla.py` - Main application (major expansion)

### New Components
- `SETTINGS_METADATA` dict with all ~100+ settings
- `ProfileLibrary` class for profile management
- `GranularEditor` class for flag editing
- `FirefoxImporter` class for prefs.js parsing
- `CategorySlider` custom widget

### Estimated New Settings Count
- Performance: ~20 settings
- Experimental: ~20 settings
- Enhanced existing: ~10 settings
- **Total: ~100+ settings** (up from ~50)

---

## Approval

- [x] Overall Architecture
- [x] Performance Settings
- [x] Experimental Features
- [x] Profile Library & Custom Profiles
- [x] Granular Editor & Flag Documentation
- [x] Enhanced Quick Start with Sliders
- [x] Enhanced Summary & Export

**Design approved: 2026-01-13**
