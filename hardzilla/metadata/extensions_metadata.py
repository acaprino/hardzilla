"""
Extension metadata for Firefox privacy extensions.

Defines the 6 core privacy-focused extensions available for one-click installation.

Note: HTTPS Everywhere has been deprecated (2022) as Firefox now includes built-in
HTTPS-Only Mode. Users should enable dom.security.https_only_mode in Firefox settings.
"""

EXTENSIONS_METADATA = {
    "uBlock0@raymondhill.net": {
        "name": "uBlock Origin",
        "description": "Efficient wide-spectrum content blocker",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi",
        "icon": "🛡️",
        "breakage_risk": 2,
        "size_mb": 3.2,
        # Custom filter lists that replace uBlock Origin's default lists
        # These are loaded via Firefox Enterprise Policies (3rdparty.Extensions)
        "custom_filter_lists": [
            "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/pro.mini.txt"
        ]
    },
    "jid1-MnnxcxisBPnSXQ@jetpack": {
        "name": "Privacy Badger",
        "description": "Learns to block invisible trackers",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/privacy-badger17/latest.xpi",
        "icon": "🦡",
        "breakage_risk": 3,
        "size_mb": 1.8
    },
    "jid1-BoFifL9Vbdl2zQ@jetpack": {
        "name": "Decentraleyes",
        "description": "Local CDN emulation to protect against tracking",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/decentraleyes/latest.xpi",
        "icon": "📦",
        "breakage_risk": 1,
        "size_mb": 2.1
    },
    "{74145f27-f039-47ce-a470-a662b129930a}": {
        "name": "ClearURLs",
        "description": "Removes tracking elements from URLs",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/clearurls/latest.xpi",
        "icon": "🧹",
        "breakage_risk": 2,
        "size_mb": 0.5
    },
    "CookieAutoDelete@kennydo.com": {
        "name": "Cookie AutoDelete",
        "description": "Automatically delete cookies when tabs are closed",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/cookie-autodelete/latest.xpi",
        "icon": "🍪",
        "breakage_risk": 4,
        "size_mb": 0.8
    },
    "CanvasBlocker@kkapsner.de": {
        "name": "CanvasBlocker",
        "description": "Prevents fingerprinting via canvas API",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/canvasblocker/latest.xpi",
        "icon": "🎨",
        "breakage_risk": 3,
        "size_mb": 1.2
    }
}
