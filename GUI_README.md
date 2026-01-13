# Hardzilla - Firefox Hardening Tool

## Overview

Hardzilla is a graphical user interface (GUI) for Firefox privacy and security configuration with granular control over individual data types and settings.

## Features

### ✨ Main Features
- **User-friendly interface** - No command line needed
- **Granular data control** - Choose exactly what to keep and what to delete
- **Session restore settings** - Control session and tab restoration
- **Cookie management** - Fine-grained cookie control
- **Network & security options** - DNS, WebRTC, and connection settings
- **Permission controls** - Manage site permissions
- **Profile import/export** - Save and share configurations

### 🛡️ Privacy Categories

The GUI allows you to configure:
- **Telemetry & Tracking** - Control data sent to Mozilla
- **Fingerprinting Protection** - Reduce browser uniqueness
- **WebRTC** - Configure video conferencing security
- **WebGL** - Control 3D graphics
- **Safe Browsing** - Google malware protection
- **DRM Content** - Digital rights management
- **Cookies Cleanup** - Automatic data deletion with custom control
- **Network Settings** - DNS and prefetch options
- **HTTPS Preferences** - SSL/TLS security
- **Search & Autofill** - Search and form autofill settings
- **UI Features** - User interface privacy features
- **IPv6** - IPv6 protocol control
- **Extensions** - Extension security settings

## Installation

### Prerequisites
- Python 3.6 or higher
- Firefox Portable installation
- Windows OS

### Quick Start

1. **Method 1: Using the Batch File** (Recommended)
   - Double-click `launch_hardzilla.bat`
   - The GUI will open automatically

2. **Method 2: Direct Python**
   - Open Command Prompt
   - Navigate to the directory
   - Run: `python hardzilla.py`

## Usage Guide

### 1. Initial Setup
1. Launch the GUI using one of the methods above
2. The application will try to auto-detect Firefox Portable
3. If not found, click "Browse" to select your Firefox Portable directory
4. Click "Verify" to confirm the profile was found

### 2. Configure Settings

#### Option A: Use Quick Presets
Navigate to the "Quick Presets" tab and choose:
- 🟢 **Basic** - Minimal protection, full functionality
- 🟡 **Balanced** - Recommended for most users
- 🟠 **Strict** - Strong privacy, may break some sites
- 🔴 **Paranoid** - Maximum privacy, will break many sites

#### Option B: Custom Configuration
1. Go to the "Categories" tab
2. For each category, select your preferred protection level:
   - **OFF** - No protection
   - **SOFT** - Light protection
   - **MEDIUM** - Balanced protection
   - **HARD** - Maximum protection
3. Pay attention to warnings (⚠️) for settings that may break sites

### 3. Apply Configuration
1. Click "✅ Apply Configuration"
2. Review the summary
3. Confirm to proceed
4. A backup will be created automatically
5. Restart Firefox for changes to take effect

### 4. Profile Management

#### Save a Profile
1. Configure your desired settings
2. Click "💾 Save Profile"
3. Choose a name and location
4. Your configuration is saved as a JSON file

#### Load a Profile
1. Click "📂 Load Profile"
2. Select a previously saved JSON profile
3. Settings will be applied instantly

### 5. Advanced Options

Navigate to the "Advanced" tab for:
- **Backup Settings** - Configure automatic backups
- **Merge Options** - Preserve custom preferences
- **Activity Log** - View all operations
- **View user.js** - Inspect the actual configuration file

## Files Included

- `hardzilla.py` - Main GUI application with granular privacy controls
- `launch_hardzilla.bat` - Windows launcher
- `main.json` - Example configuration profile
- `GUI_README.md` - This documentation file

## Comparison with Original Script

| Feature | Original Script | GUI Version |
|---------|----------------|-------------|
| Interface | Command line | Graphical |
| Platform | Cross-platform | Windows-focused |
| Navigation | Text menus | Tabs and buttons |
| Presets | Sequential selection | One-click presets |
| Visualization | Text only | Icons and colors |
| Backup | Manual | Automatic |
| Profile Management | Basic | Import/Export |

## Troubleshooting

### Python Not Found
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### Tkinter Error
- Tkinter should be included with Python
- If missing, reinstall Python with standard library

### Firefox Profile Not Found
- Ensure Firefox Portable is properly installed
- Check that the profile exists in `Data\profile` or `profile` directory
- Use the Browse button to manually select the directory

### Changes Not Taking Effect
- Make sure Firefox is completely closed
- Delete Firefox's cache after applying changes
- Check that user.js file exists in the profile directory

## Important Notes

⚠️ **Warning**: Some hardening options will break website functionality:
- **JavaScript HARD** - Disables all JavaScript (breaks 99% of sites)
- **WebRTC HARD** - Breaks video conferencing (Zoom, Teams, etc.)
- **DRM HARD** - Blocks streaming services (Netflix, Spotify, etc.)
- **Cookies MEDIUM/HARD** - Logs you out of all sites on browser close

💡 **Recommendation**: Start with the "Balanced" preset and adjust as needed.

## Support

For issues or questions:
1. Check the Activity Log in the Advanced tab
2. Review the warnings for each category
3. Try resetting to defaults and reconfiguring
4. Create a backup before making changes

## Credits

Based on:
- Firefox Hardening Guide by BrainFuckSec
- arkenfox user.js project
- Privacy community recommendations

GUI created with Python and Tkinter for improved usability.