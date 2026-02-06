"""
Extension metadata for Firefox privacy extensions.

Defines the 9 core privacy-focused extensions available for one-click installation.

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
        # Hagezi filter lists replacing third-party defaults (EasyList, EasyPrivacy, etc.)
        # Mini variants use top-traffic domains (Umbrella/Cloudflare/Tranco) for ~281k total rules:
        #   pro.mini (~71k) ads/tracking | tif.mini (~138k) threats | popupads (~58k) | fake (~14k)
        # Loaded via Enterprise Policies adminSettings.selectedFilterLists (replaces full list)
        "custom_filter_lists": [
            "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/pro.mini.txt",
            "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/tif.mini.txt",
            "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/popupads.txt",
            "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/fake.txt",
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
    },
    "addon@darkreader.org": {
        "name": "Dark Reader",
        "description": "Dark mode for every website — protects eyes during night browsing",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/darkreader/latest.xpi",
        "icon": "🌙",
        "breakage_risk": 2,
        "size_mb": 0.6
    },
    "{21f1ba12-47e1-4a9b-ad4e-3a0260bbeb26}": {
        "name": "RYS — Remove YouTube Suggestions",
        "description": "Removes YouTube recommendations, Shorts, comments, and more",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/remove-youtube-s-suggestions/latest.xpi",
        "icon": "📺",
        "breakage_risk": 1,
        "size_mb": 0.3
    },
    "{446900e4-71c2-419f-a6a7-df9c091e268b}": {
        "name": "Bitwarden Password Manager",
        "description": "Open-source password manager for secure credential storage",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/bitwarden-password-manager/latest.xpi",
        "icon": "🔑",
        "breakage_risk": 0,
        "size_mb": 15.6
    }
}
