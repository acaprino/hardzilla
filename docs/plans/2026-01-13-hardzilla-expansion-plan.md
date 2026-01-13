# Hardzilla Expansion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand Hardzilla from ~50 privacy settings to ~100+ comprehensive Firefox hardening settings with Performance, Experimental Features sections, Profile Library, Granular Editor, and Firefox import.

**Architecture:** Refactor to metadata-driven settings system. Each setting has full documentation (short/full description, impact, compatibility, recommended values). New ProfileManager class handles library. New GranularEditor widget for flag editing. CategorySlider widget for Quick Start.

**Tech Stack:** Python 3.6+, CustomTkinter, pywinstyles (Windows), JSON profiles

---

## Phase 1: Settings Metadata System

### Task 1.1: Create Settings Metadata Dictionary

**Files:**
- Create: `hardzilla_metadata.py`

**Step 1: Create the metadata module**

```python
# hardzilla_metadata.py
"""
Hardzilla Settings Metadata
Complete definitions for all ~100+ Firefox settings
"""

from typing import Dict, Any, List, TypedDict

class SettingMeta(TypedDict, total=False):
    name: str
    category: str
    subcategory: str
    short: str
    full: str
    pref: str
    type: str  # toggle, choice, number
    impact: str  # low, medium, high
    compatibility: str  # none, minor, major
    values: List[Any]
    labels: List[str]
    default: Any
    recommended: Dict[str, Any]

# Categories for organization
CATEGORIES = {
    'performance': {
        'name': 'Performance',
        'icon': '⚡',
        'subcategories': ['cache', 'processes', 'network_perf']
    },
    'privacy': {
        'name': 'Privacy',
        'icon': '🔒',
        'subcategories': ['session', 'data', 'cookies', 'tracking']
    },
    'security': {
        'name': 'Security',
        'icon': '🛡️',
        'subcategories': ['network', 'permissions']
    },
    'features': {
        'name': 'Features',
        'icon': '🧪',
        'subcategories': ['ui', 'ai', 'graphics', 'css', 'dom']
    }
}

# Preset profile definitions
PRESET_PROFILES = {
    'developer': {
        'name': 'Developer',
        'icon': '👨‍💻',
        'description': 'Max performance, balanced privacy, bleeding edge features',
        'performance': 'max_power',
        'privacy': 'balanced',
        'features': 'bleeding_edge'
    },
    'office': {
        'name': 'Office',
        'icon': '🏢',
        'description': 'Balanced settings for work environments',
        'performance': 'balanced',
        'privacy': 'balanced',
        'features': 'balanced'
    },
    'privacy_enthusiast': {
        'name': 'Privacy Pro',
        'icon': '🔐',
        'description': 'Maximum privacy, may break some sites',
        'performance': 'balanced',
        'privacy': 'paranoid',
        'features': 'conservative'
    },
    'laptop': {
        'name': 'Laptop',
        'icon': '💻',
        'description': 'Battery optimized for portable use',
        'performance': 'battery',
        'privacy': 'balanced',
        'features': 'conservative'
    },
    'gaming': {
        'name': 'Gaming',
        'icon': '🎮',
        'description': 'Maximum performance, minimal restrictions',
        'performance': 'max_power',
        'privacy': 'open',
        'features': 'bleeding_edge'
    },
    'casual': {
        'name': 'Casual',
        'icon': '📱',
        'description': 'Easy everyday browsing',
        'performance': 'balanced',
        'privacy': 'balanced',
        'features': 'balanced'
    }
}

# Complete settings metadata
SETTINGS_METADATA: Dict[str, SettingMeta] = {
    # ========== PERFORMANCE: Cache & Memory ==========
    'disk_cache_enabled': {
        'name': 'Disk Cache',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Store temporary files on disk',
        'full': 'Enables caching website data to disk. Improves load times for revisited sites but uses disk space. Disable for privacy or on systems with slow storage.',
        'pref': 'browser.cache.disk.enable',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },
    'disk_cache_size': {
        'name': 'Disk Cache Size',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Maximum disk space for cache',
        'full': 'Controls how much disk space Firefox uses for cached files. Larger cache means faster loading of previously visited sites but more disk usage.',
        'pref': 'browser.cache.disk.capacity',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [102400, 262144, 524288, 1048576],
        'labels': ['100MB', '256MB', '512MB', '1GB'],
        'default': 262144,
        'recommended': {
            'max_power': 524288,
            'balanced': 262144,
            'battery': 102400
        }
    },
    'memory_cache_enabled': {
        'name': 'RAM Cache',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Store cache in memory for faster access',
        'full': 'Keeps frequently accessed data in RAM for instant access. Uses more memory but significantly speeds up browsing. Essential for performance.',
        'pref': 'browser.cache.memory.enable',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True
        }
    },
    'memory_cache_size': {
        'name': 'RAM Cache Size',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Maximum RAM for cache',
        'full': 'Controls how much RAM Firefox uses for cached data. Higher values improve performance but consume system memory. Recommended: 256MB for 8GB RAM, 512MB for 16GB+.',
        'pref': 'browser.cache.memory.capacity',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [65536, 262144, 524288, 1048576],
        'labels': ['64MB', '256MB', '512MB', '1GB'],
        'default': 262144,
        'recommended': {
            'max_power': 524288,
            'balanced': 262144,
            'battery': 65536
        }
    },
    'session_history_entries': {
        'name': 'History Entries Per Tab',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Back/forward history depth',
        'full': 'Number of pages to remember in each tab\'s back/forward history. Higher values use more memory but allow navigating further back.',
        'pref': 'browser.sessionhistory.max_entries',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [5, 25, 50],
        'labels': ['5', '25', '50'],
        'default': 25,
        'recommended': {
            'max_power': 50,
            'balanced': 25,
            'battery': 5
        }
    },
    'cached_pages': {
        'name': 'Cached Pages in Memory',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'Pages kept ready for instant back',
        'full': 'Number of recently visited pages kept fully loaded in memory. Enables instant back/forward navigation but uses significant RAM.',
        'pref': 'browser.sessionhistory.max_total_viewers',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [0, 1, 4, 8],
        'labels': ['0', '1', '4', '8'],
        'default': 4,
        'recommended': {
            'max_power': 8,
            'balanced': 4,
            'battery': 1
        }
    },
    'session_save_interval': {
        'name': 'Session Save Frequency',
        'category': 'performance',
        'subcategory': 'cache',
        'short': 'How often to save session state',
        'full': 'Interval between automatic session saves. More frequent saves protect against data loss but increase disk writes. Less frequent saves improve battery life.',
        'pref': 'browser.sessionstore.interval',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [10000, 60000, 120000, 600000],
        'labels': ['10s', '60s', '2min', '10min'],
        'default': 60000,
        'recommended': {
            'max_power': 60000,
            'balanced': 120000,
            'battery': 600000
        }
    },

    # ========== PERFORMANCE: Processes & GPU ==========
    'content_processes': {
        'name': 'Content Processes',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Separate processes for web content',
        'full': 'Number of processes Firefox uses for web pages. More processes improve stability and security (isolated tabs) but use more RAM. 8GB RAM: 4-6, 16GB+: 8-12.',
        'pref': 'dom.ipc.processCount',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'none',
        'values': [2, 4, 6, 8, 12],
        'labels': ['2', '4', '6', '8', '12'],
        'default': 6,
        'recommended': {
            'max_power': 12,
            'balanced': 6,
            'battery': 2
        }
    },
    'isolated_processes': {
        'name': 'Site Isolation Processes',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Extra isolation for different sites',
        'full': 'Additional processes for isolating different websites. Improves security by separating sites but increases memory usage.',
        'pref': 'dom.ipc.processCount.webIsolated',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [1, 2, 4],
        'labels': ['1', '2', '4'],
        'default': 2,
        'recommended': {
            'max_power': 4,
            'balanced': 2,
            'battery': 1
        }
    },
    'webrender_enabled': {
        'name': 'WebRender',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'GPU-accelerated rendering engine',
        'full': 'Modern GPU-based rendering engine. Significantly improves scrolling smoothness and page rendering speed. Requires compatible GPU.',
        'pref': 'gfx.webrender.all',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False
        }
    },
    'gpu_acceleration': {
        'name': 'Force GPU Acceleration',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Force hardware acceleration',
        'full': 'Forces GPU acceleration even on systems where Firefox would normally disable it. Can improve performance but may cause issues on some hardware.',
        'pref': 'layers.acceleration.force-enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False
        }
    },
    'gpu_process': {
        'name': 'Separate GPU Process',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Run GPU operations in dedicated process',
        'full': 'Runs GPU operations in a separate process. Improves stability (GPU crash won\'t crash browser) and security but uses slightly more resources.',
        'pref': 'layers.gpu-process.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False
        }
    },
    'hardware_video': {
        'name': 'Hardware Video Decoding',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Use GPU for video playback',
        'full': 'Offloads video decoding to GPU. Dramatically reduces CPU usage during video playback and improves battery life. Essential for smooth 4K/HDR video.',
        'pref': 'media.hardware-video-decoding.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True
        }
    },
    'webgl_enabled': {
        'name': 'WebGL',
        'category': 'performance',
        'subcategory': 'processes',
        'short': '3D graphics in browser',
        'full': 'Enables WebGL for 3D graphics and games in the browser. Required for many interactive websites, games, and visualizations. Can be fingerprinted.',
        'pref': 'webgl.force-enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False
        }
    },
    'webgpu_enabled': {
        'name': 'WebGPU',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Next-gen GPU API',
        'full': 'Modern GPU API successor to WebGL. Enables advanced graphics and compute capabilities. Experimental but offers better performance for compatible sites.',
        'pref': 'dom.webgpu.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False
        }
    },
    'frame_rate': {
        'name': 'Max Frame Rate',
        'category': 'performance',
        'subcategory': 'processes',
        'short': 'Limit rendering frame rate',
        'full': 'Maximum frames per second for rendering. Match your monitor refresh rate for optimal experience. Lower values save battery. -1 for unlimited.',
        'pref': 'layout.frame_rate',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [30, 60, 144, -1],
        'labels': ['30fps', '60fps', '144fps', 'Unlimited'],
        'default': 60,
        'recommended': {
            'max_power': 144,
            'balanced': 60,
            'battery': 30
        }
    },

    # ========== PERFORMANCE: Network ==========
    'max_connections': {
        'name': 'Max HTTP Connections',
        'category': 'performance',
        'subcategory': 'network_perf',
        'short': 'Total concurrent connections',
        'full': 'Maximum number of simultaneous HTTP connections. Higher values can speed up page loading but may overwhelm some networks or servers.',
        'pref': 'network.http.max-connections',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [256, 900, 1200, 1800],
        'labels': ['256', '900', '1200', '1800'],
        'default': 900,
        'recommended': {
            'max_power': 1800,
            'balanced': 1200,
            'battery': 256
        }
    },
    'connections_per_server': {
        'name': 'Connections Per Server',
        'category': 'performance',
        'subcategory': 'network_perf',
        'short': 'Concurrent connections per site',
        'full': 'Maximum connections to a single server. Higher values speed up loading from individual sites but may trigger rate limiting.',
        'pref': 'network.http.max-persistent-connections-per-server',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [4, 6, 8, 10],
        'labels': ['4', '6', '8', '10'],
        'default': 6,
        'recommended': {
            'max_power': 10,
            'balanced': 8,
            'battery': 4
        }
    },
    'speculative_connections': {
        'name': 'Speculative Connections',
        'category': 'performance',
        'subcategory': 'network_perf',
        'short': 'Pre-connect to likely links',
        'full': 'Opens connections to links you might click before you click them. Speeds up navigation but uses bandwidth and may leak browsing intent.',
        'pref': 'network.http.speculative-parallel-limit',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [0, 4, 8, 20],
        'labels': ['Off', '4', '8', '20'],
        'default': 8,
        'recommended': {
            'max_power': 20,
            'balanced': 8,
            'battery': 0,
            'paranoid': 0
        }
    },
}
```

**Step 2: Verify the file was created correctly**

Run: `python -c "from hardzilla_metadata import SETTINGS_METADATA; print(f'Loaded {len(SETTINGS_METADATA)} settings')"`

Expected: `Loaded 17 settings`

---

### Task 1.2: Add Remaining Performance & Feature Settings

**Files:**
- Modify: `hardzilla_metadata.py`

**Step 1: Append experimental features settings**

Add to SETTINGS_METADATA in hardzilla_metadata.py:

```python
    # ========== FEATURES: UI & Tabs ==========
    'tab_groups': {
        'name': 'Tab Groups',
        'category': 'features',
        'subcategory': 'ui',
        'short': 'Group tabs together',
        'full': 'Enables tab grouping feature to organize tabs into collapsible groups. Helps manage many open tabs.',
        'pref': 'browser.tabs.groups.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': True
        }
    },
    'smart_tab_groups': {
        'name': 'AI Tab Grouping',
        'category': 'features',
        'subcategory': 'ui',
        'short': 'Automatically group related tabs',
        'full': 'Uses AI to automatically suggest and create tab groups based on content. May increase CPU usage.',
        'pref': 'browser.tabs.groups.smart.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },
    'sidebar_revamp': {
        'name': 'New Sidebar',
        'category': 'features',
        'subcategory': 'ui',
        'short': 'Modern sidebar design',
        'full': 'Enables the redesigned sidebar with improved organization and features.',
        'pref': 'sidebar.revamp',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'vertical_tabs': {
        'name': 'Vertical Tabs',
        'category': 'features',
        'subcategory': 'ui',
        'short': 'Tabs on the side',
        'full': 'Shows tabs vertically in the sidebar instead of horizontally at the top. Better for widescreen monitors and many tabs.',
        'pref': 'sidebar.verticalTabs',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },

    # ========== FEATURES: AI ==========
    'ml_enabled': {
        'name': 'ML Features',
        'category': 'features',
        'subcategory': 'ai',
        'short': 'Enable machine learning',
        'full': 'Master toggle for Firefox\'s machine learning features. Required for AI chat, smart features, and other ML-powered capabilities.',
        'pref': 'browser.ml.enable',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'ai_chat': {
        'name': 'AI Chatbot',
        'category': 'features',
        'subcategory': 'ai',
        'short': 'Built-in AI assistant',
        'full': 'Enables AI chatbot in the sidebar for asking questions and getting help while browsing.',
        'pref': 'browser.ml.chat.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'ai_chat_sidebar': {
        'name': 'AI Chat in Sidebar',
        'category': 'features',
        'subcategory': 'ai',
        'short': 'Show AI chat in sidebar',
        'full': 'Makes AI chat accessible from the sidebar panel.',
        'pref': 'browser.ml.chat.sidebar',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'link_preview': {
        'name': 'AI Link Preview',
        'category': 'features',
        'subcategory': 'ai',
        'short': 'AI-powered link previews',
        'full': 'Shows AI-generated summaries when hovering over links. Experimental feature.',
        'pref': 'browser.ml.linkPreview.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },
    'visual_search': {
        'name': 'Visual Search',
        'category': 'features',
        'subcategory': 'ai',
        'short': 'Search by image',
        'full': 'Enables visual/image-based search capabilities.',
        'pref': 'browser.search.visualSearch.featureGate',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    # ========== FEATURES: Graphics & Media ==========
    'avif_enabled': {
        'name': 'AVIF Images',
        'category': 'features',
        'subcategory': 'graphics',
        'short': 'Modern image format',
        'full': 'Enables AVIF image format support. AVIF offers better compression than JPEG/PNG with similar quality.',
        'pref': 'image.avif.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': True
        }
    },
    'avif_animated': {
        'name': 'Animated AVIF',
        'category': 'features',
        'subcategory': 'graphics',
        'short': 'AVIF animation support',
        'full': 'Enables animated AVIF images (like GIFs but much smaller file size).',
        'pref': 'image.avif.sequence.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': True
        }
    },
    'jxl_enabled': {
        'name': 'JPEG XL',
        'category': 'features',
        'subcategory': 'graphics',
        'short': 'Next-gen JPEG format (Nightly)',
        'full': 'Enables JPEG XL image format. Superior compression and quality but only available in Firefox Nightly builds.',
        'pref': 'image.jxl.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    # ========== FEATURES: CSS Experimental ==========
    'scroll_animations': {
        'name': 'Scroll-Driven Animations',
        'category': 'features',
        'subcategory': 'css',
        'short': 'CSS scroll-linked animations',
        'full': 'Enables CSS scroll-driven animations API. Allows animations that respond to scroll position.',
        'pref': 'layout.css.scroll-driven-animations.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'css_masonry': {
        'name': 'CSS Masonry Layout',
        'category': 'features',
        'subcategory': 'css',
        'short': 'Pinterest-style layouts',
        'full': 'Enables CSS masonry layout for grid. Creates Pinterest-style layouts natively in CSS.',
        'pref': 'layout.css.grid-template-masonry-value.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },
    'css_has': {
        'name': 'CSS :has() Selector',
        'category': 'features',
        'subcategory': 'css',
        'short': 'Parent selector in CSS',
        'full': 'Enables the :has() CSS selector which allows styling parent elements based on their children.',
        'pref': 'layout.css.has-selector.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': True
        }
    },

    # ========== FEATURES: DOM & Network ==========
    'sanitizer_api': {
        'name': 'Sanitizer API',
        'category': 'features',
        'subcategory': 'dom',
        'short': 'Safe HTML sanitization',
        'full': 'Enables the Sanitizer API for safely sanitizing HTML content. Improves security for web apps.',
        'pref': 'dom.security.sanitizer.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': False
        }
    },
    'http3_enabled': {
        'name': 'HTTP/3',
        'category': 'features',
        'subcategory': 'dom',
        'short': 'Next-gen HTTP protocol',
        'full': 'Enables HTTP/3 (QUIC) protocol. Offers faster connections, especially on unreliable networks.',
        'pref': 'network.http.http3.enable',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': True,
            'conservative': True
        }
    },
    'webtransport': {
        'name': 'WebTransport',
        'category': 'features',
        'subcategory': 'dom',
        'short': 'Modern data transport API',
        'full': 'Enables WebTransport API for efficient bidirectional communication. Used by modern real-time applications.',
        'pref': 'network.webtransport.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },
```

**Step 2: Verify all settings loaded**

Run: `python -c "from hardzilla_metadata import SETTINGS_METADATA; print(f'Loaded {len(SETTINGS_METADATA)} settings')"`

Expected: `Loaded 35+ settings`

---

### Task 1.3: Add Existing Privacy/Security Settings to Metadata

**Files:**
- Modify: `hardzilla_metadata.py`

**Step 1: Add existing privacy settings with metadata**

These mirror the existing `privacy_vars` but now with full documentation:

```python
    # ========== PRIVACY: Session & Startup ==========
    'restore_session': {
        'name': 'Restore Session',
        'category': 'privacy',
        'subcategory': 'session',
        'short': 'Reopen tabs from last session',
        'full': 'Restores your previous browsing session including all open tabs and windows. Convenient but stores browsing data between sessions.',
        'pref': 'browser.startup.page',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'restore_pinned': {
        'name': 'Restore Pinned Tabs',
        'category': 'privacy',
        'subcategory': 'session',
        'short': 'Keep pinned tabs across sessions',
        'full': 'Restores pinned tabs when starting Firefox. Pinned tabs stay on the left and persist between sessions.',
        'pref': 'browser.sessionstore.restore_pinned_tabs_on_demand',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'restore_from_crash': {
        'name': 'Crash Recovery',
        'category': 'privacy',
        'subcategory': 'session',
        'short': 'Restore session after crash',
        'full': 'Automatically restores your session if Firefox crashes. Prevents data loss but requires storing session data.',
        'pref': 'browser.sessionstore.resume_from_crash',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },
    'lazy_restore': {
        'name': 'Lazy Tab Loading',
        'category': 'privacy',
        'subcategory': 'session',
        'short': 'Load tabs only when clicked',
        'full': 'Tabs are not loaded until you click them. Dramatically speeds up Firefox startup with many tabs and saves memory.',
        'pref': 'browser.sessionstore.restore_on_demand',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True
        }
    },

    # ========== PRIVACY: Data & Cleanup ==========
    'keep_cookies': {
        'name': 'Keep Cookies',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Preserve cookies on shutdown',
        'full': 'Keeps cookies when Firefox closes. Required for staying logged into websites. Disable for maximum privacy.',
        'pref': 'privacy.clearOnShutdown.cookies',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['Keep', 'Clear'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'keep_sessions': {
        'name': 'Keep Session Data',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Preserve session on shutdown',
        'full': 'Keeps open tabs and windows data. Required for session restore feature.',
        'pref': 'privacy.clearOnShutdown.sessions',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Keep', 'Clear'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'keep_logins': {
        'name': 'Keep Saved Logins',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Remember passwords',
        'full': 'Allows Firefox to save and remember login credentials. Uses encrypted storage.',
        'pref': 'signon.rememberSignons',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'keep_formdata': {
        'name': 'Keep Form Data',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Remember form entries',
        'full': 'Saves text entered in forms for autocomplete suggestions. Convenient but stores personal data.',
        'pref': 'privacy.clearOnShutdown.formdata',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Keep', 'Clear'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'keep_history': {
        'name': 'Keep Browsing History',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Preserve history on shutdown',
        'full': 'Keeps browsing history when Firefox closes. Useful for finding previously visited sites.',
        'pref': 'privacy.clearOnShutdown.history',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },
    'keep_downloads': {
        'name': 'Keep Download History',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Remember downloaded files',
        'full': 'Keeps list of downloaded files. The files themselves are not affected, only the list.',
        'pref': 'privacy.clearOnShutdown.downloads',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },
    'clear_cache': {
        'name': 'Clear Cache',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Delete cached files on shutdown',
        'full': 'Clears temporary cached files when Firefox closes. Improves privacy but slower browsing after restart.',
        'pref': 'privacy.clearOnShutdown.cache',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Clear', 'Keep'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },
    'clear_offline': {
        'name': 'Clear Offline Data',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Delete offline website data',
        'full': 'Clears data stored by websites for offline use. May break offline functionality of some web apps.',
        'pref': 'privacy.clearOnShutdown.offlineApps',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Clear', 'Keep'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },
    'clear_siteprefs': {
        'name': 'Clear Site Preferences',
        'category': 'privacy',
        'subcategory': 'data',
        'short': 'Reset per-site settings',
        'full': 'Clears per-site preferences like zoom level, permissions, and notification settings.',
        'pref': 'privacy.clearOnShutdown.siteSettings',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Clear', 'Keep'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': True,
            'open': False
        }
    },

    # ========== PRIVACY: Cookies ==========
    'cookie_lifetime': {
        'name': 'Cookie Lifetime',
        'category': 'privacy',
        'subcategory': 'cookies',
        'short': 'How long cookies last',
        'full': 'Controls cookie expiration. Normal: sites set expiration. Session: deleted when browser closes. Days: custom maximum lifetime.',
        'pref': 'network.cookie.lifetimePolicy',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': ['normal', 'session', 'days'],
        'labels': ['Normal', 'Session Only', 'Custom Days'],
        'default': 'normal',
        'recommended': {
            'balanced': 'normal',
            'paranoid': 'session',
            'open': 'normal'
        }
    },
    'cookie_days': {
        'name': 'Cookie Days',
        'category': 'privacy',
        'subcategory': 'cookies',
        'short': 'Maximum cookie lifetime in days',
        'full': 'When cookie lifetime is set to "days", this controls the maximum number of days cookies can persist.',
        'pref': 'network.cookie.lifetime.days',
        'type': 'number',
        'impact': 'low',
        'compatibility': 'none',
        'values': [1, 7, 30, 90, 365],
        'labels': ['1', '7', '30', '90', '365'],
        'default': 30,
        'recommended': {
            'balanced': 30,
            'paranoid': 1,
            'open': 365
        }
    },
    'third_party_cookies': {
        'name': 'Third-Party Cookies',
        'category': 'privacy',
        'subcategory': 'cookies',
        'short': 'Cookies from other sites',
        'full': 'Controls cookies set by domains other than the site you\'re visiting. Used for tracking across sites. Cross-site isolation is recommended.',
        'pref': 'network.cookie.cookieBehavior',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': ['all', 'cross-site', 'none', 'visited'],
        'labels': ['Allow All', 'Isolate Cross-Site', 'Block All', 'Only Visited'],
        'default': 'cross-site',
        'recommended': {
            'balanced': 'cross-site',
            'paranoid': 'none',
            'open': 'all'
        }
    },

    # ========== PRIVACY: Tracking Protection ==========
    'tracking_protection': {
        'name': 'Tracking Protection',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Block known trackers',
        'full': 'Firefox\'s built-in tracking protection. Standard blocks common trackers. Strict blocks more but may break some sites.',
        'pref': 'browser.contentblocking.category',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': ['standard', 'strict', 'custom'],
        'labels': ['Standard', 'Strict', 'Custom'],
        'default': 'strict',
        'recommended': {
            'balanced': 'strict',
            'paranoid': 'strict',
            'open': 'standard'
        }
    },
    'fingerprint_resist': {
        'name': 'Fingerprint Protection',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Block fingerprinting scripts',
        'full': 'Blocks scripts that try to identify your browser through unique characteristics like canvas, fonts, and screen size.',
        'pref': 'privacy.trackingprotection.fingerprinting.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },
    'cryptomining_block': {
        'name': 'Cryptomining Protection',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Block cryptocurrency miners',
        'full': 'Blocks scripts that use your computer to mine cryptocurrency without permission.',
        'pref': 'privacy.trackingprotection.cryptomining.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },

    # ========== SECURITY: Network & DNS ==========
    'dns_over_https': {
        'name': 'DNS over HTTPS',
        'category': 'security',
        'subcategory': 'network',
        'short': 'Encrypt DNS queries',
        'full': 'Encrypts DNS lookups to prevent ISP snooping. Off: system DNS. Increased: DoH with fallback. Max: DoH only (may break some networks).',
        'pref': 'network.trr.mode',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': ['off', 'default', 'increased', 'max'],
        'labels': ['Off', 'Default', 'Increased', 'Max'],
        'default': 'increased',
        'recommended': {
            'balanced': 'increased',
            'paranoid': 'max',
            'open': 'off'
        }
    },
    'dns_provider': {
        'name': 'DNS Provider',
        'category': 'security',
        'subcategory': 'network',
        'short': 'DoH server to use',
        'full': 'The DNS-over-HTTPS server for encrypted DNS queries. Cloudflare is fast, Quad9 blocks malware, NextDNS offers customization.',
        'pref': 'network.trr.uri',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': ['cloudflare', 'quad9', 'nextdns'],
        'labels': ['Cloudflare', 'Quad9', 'NextDNS'],
        'default': 'quad9',
        'recommended': {
            'balanced': 'quad9',
            'paranoid': 'quad9',
            'open': 'cloudflare'
        }
    },
    'https_only': {
        'name': 'HTTPS-Only Mode',
        'category': 'security',
        'subcategory': 'network',
        'short': 'Force HTTPS connections',
        'full': 'Automatically upgrades HTTP connections to HTTPS and warns before loading insecure sites.',
        'pref': 'dom.security.https_only_mode',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },
    'webrtc_enabled': {
        'name': 'WebRTC',
        'category': 'security',
        'subcategory': 'network',
        'short': 'Real-time communication',
        'full': 'Enables WebRTC for video/audio calls and peer-to-peer connections. Required for video conferencing but can leak your IP address.',
        'pref': 'media.peerconnection.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },
    'webrtc_ip_leak': {
        'name': 'WebRTC IP Protection',
        'category': 'security',
        'subcategory': 'network',
        'short': 'Prevent IP leak via WebRTC',
        'full': 'Prevents WebRTC from revealing your real IP address when using VPN. May affect video call quality.',
        'pref': 'media.peerconnection.ice.default_address_only',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Protected', 'Normal'],
        'default': False,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    # ========== SECURITY: Permissions ==========
    'location_permission': {
        'name': 'Location Access',
        'category': 'security',
        'subcategory': 'permissions',
        'short': 'Website location access',
        'full': 'Controls whether websites can request your physical location. Ask prompts each time.',
        'pref': 'geo.enabled',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': ['allow', 'ask', 'block'],
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 'ask',
        'recommended': {
            'balanced': 'ask',
            'paranoid': 'block',
            'open': 'ask'
        }
    },
    'camera_permission': {
        'name': 'Camera Access',
        'category': 'security',
        'subcategory': 'permissions',
        'short': 'Website camera access',
        'full': 'Controls whether websites can access your camera. Required for video calls.',
        'pref': 'permissions.default.camera',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': ['allow', 'ask', 'block'],
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 'ask',
        'recommended': {
            'balanced': 'ask',
            'paranoid': 'block',
            'open': 'ask'
        }
    },
    'microphone_permission': {
        'name': 'Microphone Access',
        'category': 'security',
        'subcategory': 'permissions',
        'short': 'Website microphone access',
        'full': 'Controls whether websites can access your microphone. Required for voice/video calls.',
        'pref': 'permissions.default.microphone',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': ['allow', 'ask', 'block'],
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 'ask',
        'recommended': {
            'balanced': 'ask',
            'paranoid': 'block',
            'open': 'ask'
        }
    },
    'notifications_permission': {
        'name': 'Notifications',
        'category': 'security',
        'subcategory': 'permissions',
        'short': 'Website notifications',
        'full': 'Controls whether websites can send desktop notifications. Block to avoid notification spam.',
        'pref': 'permissions.default.desktop-notification',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': ['allow', 'ask', 'block'],
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 'ask',
        'recommended': {
            'balanced': 'ask',
            'paranoid': 'block',
            'open': 'ask'
        }
    },
    'autoplay_permission': {
        'name': 'Autoplay',
        'category': 'security',
        'subcategory': 'permissions',
        'short': 'Video/audio autoplay',
        'full': 'Controls whether videos and audio can play automatically. Block prevents annoying auto-playing media.',
        'pref': 'media.autoplay.default',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': ['allow', 'block'],
        'labels': ['Allow', 'Block'],
        'default': 'block',
        'recommended': {
            'balanced': 'block',
            'paranoid': 'block',
            'open': 'allow'
        }
    },

    # ========== Telemetry ==========
    'telemetry_enabled': {
        'name': 'Telemetry',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Send usage data to Mozilla',
        'full': 'Sends anonymous usage statistics to Mozilla to help improve Firefox. No personal data is collected.',
        'pref': 'toolkit.telemetry.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },
    'studies_enabled': {
        'name': 'Firefox Studies',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Participate in Firefox studies',
        'full': 'Allows Mozilla to install and run studies to test new features. Studies may change browser behavior.',
        'pref': 'app.shield.optoutstudies.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },
    'crash_reports': {
        'name': 'Crash Reports',
        'category': 'privacy',
        'subcategory': 'tracking',
        'short': 'Send crash reports to Mozilla',
        'full': 'Automatically sends crash reports to help Mozilla fix bugs. May include some browsing data.',
        'pref': 'browser.tabs.crashReporting.sendReport',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },
}
```

---

## Phase 2: UI Components

### Task 2.1: Create CategorySlider Widget

**Files:**
- Create: `hardzilla_widgets.py`

**Step 1: Create the widgets module**

```python
# hardzilla_widgets.py
"""
Custom widgets for Hardzilla
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, List, Optional

class CategorySlider(ctk.CTkFrame):
    """
    A 5-position slider for category presets.
    Positions: far_left, left, center, right, far_right
    """

    def __init__(
        self,
        parent,
        label_left: str,
        label_right: str,
        icon_left: str = "",
        icon_right: str = "",
        descriptions: List[str] = None,
        on_change: Callable[[int], None] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.on_change = on_change
        self.descriptions = descriptions or [""] * 5
        self.current_position = 2  # Center by default

        # Header with labels
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))

        # Left label
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left")
        ctk.CTkLabel(
            left_frame,
            text=f"{icon_left} {label_left}",
            font=ctk.CTkFont(size=11),
            text_color="#a0a0a0"
        ).pack(side="left")

        # Right label
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right")
        ctk.CTkLabel(
            right_frame,
            text=f"{label_right} {icon_right}",
            font=ctk.CTkFont(size=11),
            text_color="#a0a0a0"
        ).pack(side="right")

        # Slider frame
        slider_frame = ctk.CTkFrame(self, fg_color="#2a2a4a", corner_radius=8, height=40)
        slider_frame.pack(fill="x", pady=5)
        slider_frame.pack_propagate(False)

        inner = ctk.CTkFrame(slider_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=5)

        # Create 5 position buttons
        self.position_buttons = []
        for i in range(5):
            btn = ctk.CTkButton(
                inner,
                text="●" if i == 2 else "○",
                width=30,
                height=24,
                fg_color="transparent" if i != 2 else "#3B8ED0",
                hover_color="#3a3a5a",
                text_color="#ffffff",
                command=lambda pos=i: self.set_position(pos)
            )
            btn.pack(side="left", expand=True)
            self.position_buttons.append(btn)

        # Description label
        self.desc_label = ctk.CTkLabel(
            self,
            text=self.descriptions[2],
            font=ctk.CTkFont(size=10),
            text_color="#808080"
        )
        self.desc_label.pack(anchor="center")

    def set_position(self, position: int):
        """Set slider to specific position (0-4)"""
        self.current_position = position

        # Update button appearance
        for i, btn in enumerate(self.position_buttons):
            if i == position:
                btn.configure(text="●", fg_color="#3B8ED0")
            else:
                btn.configure(text="○", fg_color="transparent")

        # Update description
        if position < len(self.descriptions):
            self.desc_label.configure(text=self.descriptions[position])

        # Callback
        if self.on_change:
            self.on_change(position)

    def get_position(self) -> int:
        """Get current position (0-4)"""
        return self.current_position


class SettingRow(ctk.CTkFrame):
    """
    A single setting row with toggle/choice, inline description, and expandable details.
    """

    def __init__(
        self,
        parent,
        name: str,
        short_desc: str,
        full_desc: str,
        setting_type: str,  # 'toggle' or 'choice'
        values: List,
        labels: List[str],
        impact: str,
        compatibility: str,
        recommended: dict,
        variable: tk.Variable,
        **kwargs
    ):
        super().__init__(parent, fg_color="#2a2a4a", corner_radius=8, **kwargs)

        self.full_desc = full_desc
        self.impact = impact
        self.compatibility = compatibility
        self.recommended = recommended
        self.expanded = False

        # Main row
        main_row = ctk.CTkFrame(self, fg_color="transparent")
        main_row.pack(fill="x", padx=12, pady=10)

        # Left side: name and description
        left = ctk.CTkFrame(main_row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        # Name with info button
        name_frame = ctk.CTkFrame(left, fg_color="transparent")
        name_frame.pack(anchor="w")

        ctk.CTkLabel(
            name_frame,
            text=name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        self.info_btn = ctk.CTkButton(
            name_frame,
            text="ⓘ",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#3a3a5a",
            text_color="#808080",
            command=self.toggle_details
        )
        self.info_btn.pack(side="left", padx=(5, 0))

        # Short description
        ctk.CTkLabel(
            left,
            text=short_desc,
            font=ctk.CTkFont(size=11),
            text_color="#a0a0a0"
        ).pack(anchor="w")

        # Right side: control
        right = ctk.CTkFrame(main_row, fg_color="transparent")
        right.pack(side="right")

        if setting_type == 'toggle':
            self.control = ctk.CTkSwitch(
                right,
                text="",
                variable=variable,
                onvalue=True,
                offvalue=False,
                width=40
            )
            self.control.pack()
        else:  # choice
            self.control = ctk.CTkSegmentedButton(
                right,
                values=labels,
                variable=variable,
                width=len(labels) * 60
            )
            self.control.pack()

        # Expandable details panel (hidden by default)
        self.details_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=6)

    def toggle_details(self):
        """Toggle the expanded details panel"""
        if self.expanded:
            self.details_frame.pack_forget()
            self.info_btn.configure(text_color="#808080")
        else:
            self._build_details()
            self.details_frame.pack(fill="x", padx=12, pady=(0, 10))
            self.info_btn.configure(text_color="#3B8ED0")
        self.expanded = not self.expanded

    def _build_details(self):
        """Build the details panel content"""
        # Clear existing
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        inner = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # Full description
        ctk.CTkLabel(
            inner,
            text=self.full_desc,
            font=ctk.CTkFont(size=11),
            text_color="#c0c0c0",
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Impact
        impact_colors = {'low': '#2FA572', 'medium': '#FFA500', 'high': '#E74C3C'}
        impact_frame = ctk.CTkFrame(inner, fg_color="transparent")
        impact_frame.pack(anchor="w", pady=2)
        ctk.CTkLabel(
            impact_frame,
            text="Impact:",
            font=ctk.CTkFont(size=10),
            text_color="#808080"
        ).pack(side="left")
        ctk.CTkLabel(
            impact_frame,
            text=f" {self.impact.upper()}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=impact_colors.get(self.impact, '#808080')
        ).pack(side="left")

        # Compatibility
        compat_text = {
            'none': '✅ No issues',
            'minor': '⚠️ Minor issues possible',
            'major': '❌ May break some sites'
        }
        ctk.CTkLabel(
            inner,
            text=f"Compatibility: {compat_text.get(self.compatibility, 'Unknown')}",
            font=ctk.CTkFont(size=10),
            text_color="#808080"
        ).pack(anchor="w", pady=2)

        # Recommended values
        if self.recommended:
            ctk.CTkLabel(
                inner,
                text="Recommended per profile:",
                font=ctk.CTkFont(size=10),
                text_color="#808080"
            ).pack(anchor="w", pady=(8, 2))

            for profile, value in self.recommended.items():
                ctk.CTkLabel(
                    inner,
                    text=f"  • {profile.replace('_', ' ').title()}: {value}",
                    font=ctk.CTkFont(size=10),
                    text_color="#a0a0a0"
                ).pack(anchor="w")
```

**Step 2: Verify widgets module**

Run: `python -c "from hardzilla_widgets import CategorySlider, SettingRow; print('Widgets loaded successfully')"`

Expected: `Widgets loaded successfully`

---

### Task 2.2: Create Profile Manager Class

**Files:**
- Create: `hardzilla_profiles.py`

**Step 1: Create profile manager module**

```python
# hardzilla_profiles.py
"""
Profile management for Hardzilla
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import re


class ProfileManager:
    """Manages custom profiles and presets"""

    def __init__(self, profiles_dir: Path = None):
        self.profiles_dir = profiles_dir or Path.home() / ".hardzilla" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile: Optional[Dict] = None

    def list_profiles(self) -> List[Dict]:
        """List all saved custom profiles"""
        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    profile['_file'] = str(file)
                    profiles.append(profile)
            except Exception:
                continue
        return sorted(profiles, key=lambda p: p.get('modified', ''), reverse=True)

    def save_profile(
        self,
        name: str,
        description: str,
        settings: Dict[str, Any],
        tags: List[str] = None,
        base: str = None
    ) -> Path:
        """Save a custom profile"""
        # Sanitize filename
        safe_name = re.sub(r'[^\w\-]', '_', name.lower())
        filepath = self.profiles_dir / f"{safe_name}.json"

        profile = {
            'name': name,
            'description': description,
            'tags': tags or [],
            'base': base,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'version': '3.0',
            'settings': settings
        }

        # Update modified time if exists
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    profile['created'] = existing.get('created', profile['created'])
            except Exception:
                pass

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)

        self.current_profile = profile
        return filepath

    def load_profile(self, filepath: str) -> Dict[str, Any]:
        """Load a profile from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        self.current_profile = profile
        return profile

    def delete_profile(self, filepath: str) -> bool:
        """Delete a profile"""
        try:
            Path(filepath).unlink()
            return True
        except Exception:
            return False

    def duplicate_profile(self, filepath: str, new_name: str) -> Path:
        """Duplicate a profile with new name"""
        profile = self.load_profile(filepath)
        profile['name'] = new_name
        return self.save_profile(
            name=new_name,
            description=profile.get('description', ''),
            settings=profile.get('settings', {}),
            tags=profile.get('tags', []),
            base=profile.get('base')
        )

    def export_profile(self, filepath: str, export_path: str) -> bool:
        """Export profile to external location"""
        try:
            profile = self.load_profile(filepath)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            return True
        except Exception:
            return False

    def import_profile(self, import_path: str) -> Path:
        """Import profile from external file"""
        with open(import_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        return self.save_profile(
            name=profile.get('name', 'Imported Profile'),
            description=profile.get('description', ''),
            settings=profile.get('settings', {}),
            tags=profile.get('tags', []),
            base=profile.get('base')
        )


class FirefoxImporter:
    """Import settings from existing Firefox installation"""

    # Map Firefox prefs to Hardzilla setting keys
    PREF_MAP = {
        'browser.startup.page': 'restore_session',
        'browser.cache.disk.enable': 'disk_cache_enabled',
        'browser.cache.disk.capacity': 'disk_cache_size',
        'browser.cache.memory.enable': 'memory_cache_enabled',
        'browser.cache.memory.capacity': 'memory_cache_size',
        'dom.ipc.processCount': 'content_processes',
        'gfx.webrender.all': 'webrender_enabled',
        'network.cookie.cookieBehavior': 'third_party_cookies',
        'network.trr.mode': 'dns_over_https',
        'privacy.trackingprotection.fingerprinting.enabled': 'fingerprint_resist',
        'browser.tabs.groups.enabled': 'tab_groups',
        'sidebar.verticalTabs': 'vertical_tabs',
        'browser.ml.enable': 'ml_enabled',
        # Add more mappings...
    }

    # Value transformations
    VALUE_TRANSFORMS = {
        'restore_session': lambda v: v == 3,  # 3 = restore session
        'third_party_cookies': lambda v: {0: 'all', 1: 'none', 3: 'visited', 5: 'cross-site'}.get(v, 'cross-site'),
        'dns_over_https': lambda v: {0: 'off', 2: 'default', 3: 'max'}.get(v, 'default'),
    }

    def __init__(self, profile_path: Path):
        self.profile_path = profile_path
        self.prefs_file = profile_path / "prefs.js"
        self.userjs_file = profile_path / "user.js"

    def scan_preferences(self) -> Dict[str, Any]:
        """Scan Firefox prefs.js and user.js for current settings"""
        prefs = {}

        # Read prefs.js (main preferences)
        if self.prefs_file.exists():
            prefs.update(self._parse_prefs_file(self.prefs_file))

        # Read user.js (user overrides) - takes precedence
        if self.userjs_file.exists():
            prefs.update(self._parse_prefs_file(self.userjs_file))

        return prefs

    def _parse_prefs_file(self, filepath: Path) -> Dict[str, Any]:
        """Parse a Firefox prefs file"""
        prefs = {}
        pref_pattern = re.compile(r'user_pref\("([^"]+)",\s*(.+?)\);')

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for match in pref_pattern.finditer(content):
                key = match.group(1)
                value_str = match.group(2).strip()

                # Parse value
                if value_str == 'true':
                    value = True
                elif value_str == 'false':
                    value = False
                elif value_str.startswith('"') and value_str.endswith('"'):
                    value = value_str[1:-1]
                else:
                    try:
                        value = int(value_str)
                    except ValueError:
                        try:
                            value = float(value_str)
                        except ValueError:
                            value = value_str

                prefs[key] = value
        except Exception:
            pass

        return prefs

    def import_to_hardzilla(self) -> Dict[str, Any]:
        """Import Firefox settings to Hardzilla format"""
        firefox_prefs = self.scan_preferences()
        hardzilla_settings = {}

        for ff_pref, hz_key in self.PREF_MAP.items():
            if ff_pref in firefox_prefs:
                value = firefox_prefs[ff_pref]

                # Apply transformation if needed
                if hz_key in self.VALUE_TRANSFORMS:
                    value = self.VALUE_TRANSFORMS[hz_key](value)

                hardzilla_settings[hz_key] = value

        return hardzilla_settings

    def get_import_summary(self) -> Dict[str, int]:
        """Get summary of what can be imported"""
        firefox_prefs = self.scan_preferences()

        recognized = 0
        for ff_pref in self.PREF_MAP.keys():
            if ff_pref in firefox_prefs:
                recognized += 1

        return {
            'total_firefox_prefs': len(firefox_prefs),
            'recognized_by_hardzilla': recognized,
            'hardzilla_settings': len(self.PREF_MAP)
        }
```

**Step 2: Verify profile manager**

Run: `python -c "from hardzilla_profiles import ProfileManager, FirefoxImporter; print('Profile manager loaded')"`

Expected: `Profile manager loaded`

---

## Phase 3: Integrate New UI into Main Application

### Task 3.1: Refactor hardzilla.py to Use Metadata System

**Files:**
- Modify: `hardzilla.py`

**Step 1: Add imports at top of file**

After existing imports, add:
```python
from hardzilla_metadata import SETTINGS_METADATA, PRESET_PROFILES, CATEGORIES
from hardzilla_widgets import CategorySlider, SettingRow
from hardzilla_profiles import ProfileManager, FirefoxImporter
```

**Step 2: Update __init__ to create settings vars from metadata**

Replace the hardcoded `self.privacy_vars` dictionary with dynamic creation:

```python
# In __init__, replace self.privacy_vars = {...} with:
self.settings_vars = {}
for key, meta in SETTINGS_METADATA.items():
    if meta['type'] == 'toggle':
        self.settings_vars[key] = tk.BooleanVar(value=meta['default'])
    elif meta['type'] == 'choice':
        self.settings_vars[key] = tk.StringVar(value=str(meta['default']))
    elif meta['type'] == 'number':
        self.settings_vars[key] = tk.IntVar(value=meta['default'])

# Keep backward compatibility alias
self.privacy_vars = self.settings_vars

# Initialize profile manager
self.profile_manager = ProfileManager()
```

---

### Task 3.2: Add Performance Section Tab

**Files:**
- Modify: `hardzilla.py`

**Step 1: Update nav_items in setup_sidebar**

Add Performance section after Quick Setup:
```python
nav_items = [
    ("divider", "QUICK SETUP"),
    ("quick_start", "Quick Start"),
    ("profile_library", "Profile Library"),  # NEW
    ("divider", "PERFORMANCE"),              # NEW
    ("cache_memory", "Cache & Memory"),      # NEW
    ("processes_gpu", "Processes & GPU"),    # NEW
    ("divider", "PRIVACY"),
    # ... rest unchanged
]
```

**Step 2: Create cache_memory section**

Add new method:
```python
def create_cache_memory_section(self):
    """Create Cache & Memory settings section"""
    frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

    self.create_section_header(frame, "Cache & Memory",
        "Control how Firefox stores temporary data")

    # Get all cache-related settings from metadata
    cache_settings = [
        k for k, v in SETTINGS_METADATA.items()
        if v.get('subcategory') == 'cache'
    ]

    for key in cache_settings:
        meta = SETTINGS_METADATA[key]
        row = SettingRow(
            frame,
            name=meta['name'],
            short_desc=meta['short'],
            full_desc=meta['full'],
            setting_type=meta['type'],
            values=meta['values'],
            labels=meta['labels'],
            impact=meta['impact'],
            compatibility=meta['compatibility'],
            recommended=meta.get('recommended', {}),
            variable=self.settings_vars[key]
        )
        row.pack(fill="x", pady=4)

    return frame
```

**Step 3: Create processes_gpu section**

Add new method:
```python
def create_processes_gpu_section(self):
    """Create Processes & GPU settings section"""
    frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

    self.create_section_header(frame, "Processes & GPU",
        "Control Firefox process architecture and hardware acceleration")

    process_settings = [
        k for k, v in SETTINGS_METADATA.items()
        if v.get('subcategory') == 'processes'
    ]

    for key in process_settings:
        meta = SETTINGS_METADATA[key]
        row = SettingRow(
            frame,
            name=meta['name'],
            short_desc=meta['short'],
            full_desc=meta['full'],
            setting_type=meta['type'],
            values=meta['values'],
            labels=meta['labels'],
            impact=meta['impact'],
            compatibility=meta['compatibility'],
            recommended=meta.get('recommended', {}),
            variable=self.settings_vars[key]
        )
        row.pack(fill="x", pady=4)

    return frame
```

**Step 4: Register new sections in setup_content_area**

Add to sections dict:
```python
self.sections['cache_memory'] = self.create_cache_memory_section()
self.sections['processes_gpu'] = self.create_processes_gpu_section()
self.sections['profile_library'] = self.create_profile_library_section()
```

---

### Task 3.3: Add Experimental Features Section

**Files:**
- Modify: `hardzilla.py`

**Step 1: Add nav item for experimental**

In nav_items:
```python
("divider", "FEATURES"),
("experimental", "Experimental"),
```

**Step 2: Create experimental section**

```python
def create_experimental_section(self):
    """Create Experimental Features settings section"""
    frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

    self.create_section_header(frame, "Experimental Features",
        "Enable cutting-edge Firefox features (may be unstable)")

    # Group by subcategory
    subcategories = {
        'ui': 'UI & Tabs',
        'ai': 'AI Features',
        'graphics': 'Graphics & Media',
        'css': 'CSS Experimental',
        'dom': 'DOM & Network'
    }

    for subcat, subcat_name in subcategories.items():
        # Subcategory header
        header = ctk.CTkLabel(
            frame,
            text=subcat_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#a0a0a0"
        )
        header.pack(anchor="w", pady=(15, 8))

        # Settings in this subcategory
        settings = [
            k for k, v in SETTINGS_METADATA.items()
            if v.get('category') == 'features' and v.get('subcategory') == subcat
        ]

        for key in settings:
            meta = SETTINGS_METADATA[key]
            row = SettingRow(
                frame,
                name=meta['name'],
                short_desc=meta['short'],
                full_desc=meta['full'],
                setting_type=meta['type'],
                values=meta['values'],
                labels=meta['labels'],
                impact=meta['impact'],
                compatibility=meta['compatibility'],
                recommended=meta.get('recommended', {}),
                variable=self.settings_vars[key]
            )
            row.pack(fill="x", pady=4)

    return frame
```

**Step 3: Register in setup_content_area**

```python
self.sections['experimental'] = self.create_experimental_section()
```

---

### Task 3.4: Create Profile Library Section

**Files:**
- Modify: `hardzilla.py`

**Step 1: Create profile library section**

```python
def create_profile_library_section(self):
    """Create Profile Library section"""
    frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

    self.create_section_header(frame, "Profile Library",
        "Manage preset and custom configuration profiles")

    # Preset profiles section
    presets_card = self.create_card(frame, "Preset Profiles")

    presets_grid = ctk.CTkFrame(presets_card, fg_color="transparent")
    presets_grid.pack(fill="x")

    col = 0
    row_frame = None
    for preset_id, preset in PRESET_PROFILES.items():
        if col % 3 == 0:
            row_frame = ctk.CTkFrame(presets_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)

        card = ctk.CTkFrame(row_frame, fg_color="#2a2a4a", corner_radius=8, width=180)
        card.pack(side="left", padx=4, pady=4)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(inner,
            text=f"{preset['icon']} {preset['name']}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(inner,
            text="PRESET",
            font=ctk.CTkFont(size=9),
            text_color="#808080"
        ).pack(anchor="w")

        ctk.CTkLabel(inner,
            text=preset['description'][:40] + "...",
            font=ctk.CTkFont(size=10),
            text_color="#a0a0a0",
            wraplength=160
        ).pack(anchor="w", pady=(5, 10))

        ctk.CTkButton(inner,
            text="Apply",
            width=70, height=28,
            fg_color="#3B8ED0",
            command=lambda p=preset_id: self.apply_preset_profile(p)
        ).pack(anchor="w")

        col += 1

    # Custom profiles section
    custom_card = self.create_card(frame, "Custom Profiles")

    # Add new profile button
    btn_row = ctk.CTkFrame(custom_card, fg_color="transparent")
    btn_row.pack(fill="x", pady=(0, 10))

    ctk.CTkButton(btn_row,
        text="+ New Profile",
        width=120, height=32,
        fg_color="#2FA572",
        command=self.create_new_profile
    ).pack(side="left")

    ctk.CTkButton(btn_row,
        text="Import from Firefox",
        width=140, height=32,
        fg_color="#3B8ED0",
        command=self.import_from_firefox
    ).pack(side="left", padx=10)

    # List custom profiles
    self.custom_profiles_frame = ctk.CTkFrame(custom_card, fg_color="transparent")
    self.custom_profiles_frame.pack(fill="x")
    self.refresh_custom_profiles()

    return frame
```

**Step 2: Add profile management methods**

```python
def apply_preset_profile(self, preset_id: str):
    """Apply a preset profile"""
    preset = PRESET_PROFILES.get(preset_id)
    if not preset:
        return

    # Map preset levels to settings
    perf_level = preset.get('performance', 'balanced')
    priv_level = preset.get('privacy', 'balanced')
    feat_level = preset.get('features', 'balanced')

    for key, meta in SETTINGS_METADATA.items():
        recommended = meta.get('recommended', {})

        # Determine which level to use based on category
        if meta['category'] == 'performance':
            level = perf_level
        elif meta['category'] in ('privacy', 'security'):
            level = priv_level
        elif meta['category'] == 'features':
            level = feat_level
        else:
            level = 'balanced'

        if level in recommended:
            self.settings_vars[key].set(recommended[level])

    self.profile_state['profile_name'] = preset['name']
    self.update_profile_status()
    messagebox.showinfo("Profile Applied", f"Applied preset: {preset['name']}")

def import_from_firefox(self):
    """Import settings from current Firefox installation"""
    if not self.profile_path:
        messagebox.showerror("Error", "Please select a Firefox profile first!")
        return

    importer = FirefoxImporter(self.profile_path)
    summary = importer.get_import_summary()

    if messagebox.askyesno("Import Firefox Settings",
        f"Found {summary['total_firefox_prefs']} Firefox preferences.\n"
        f"{summary['recognized_by_hardzilla']} are recognized by Hardzilla.\n\n"
        "Import these settings?"):

        settings = importer.import_to_hardzilla()
        for key, value in settings.items():
            if key in self.settings_vars:
                self.settings_vars[key].set(value)

        self.profile_state['profile_name'] = f"Imported {datetime.now().strftime('%Y-%m-%d')}"
        self.update_profile_status()
        messagebox.showinfo("Import Complete",
            f"Imported {len(settings)} settings from Firefox.")

def refresh_custom_profiles(self):
    """Refresh the custom profiles list"""
    for widget in self.custom_profiles_frame.winfo_children():
        widget.destroy()

    profiles = self.profile_manager.list_profiles()

    if not profiles:
        ctk.CTkLabel(self.custom_profiles_frame,
            text="No custom profiles yet. Click '+ New Profile' to create one.",
            text_color="#808080"
        ).pack(anchor="w")
        return

    for profile in profiles:
        row = ctk.CTkFrame(self.custom_profiles_frame, fg_color="#2a2a4a", corner_radius=8)
        row.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(inner,
            text=f"🔧 {profile['name']}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(inner, text="Apply", width=60, height=28,
            command=lambda p=profile['_file']: self.load_custom_profile(p)
        ).pack(side="right", padx=2)

        ctk.CTkButton(inner, text="Edit", width=50, height=28,
            fg_color="#3a3a5a",
            command=lambda p=profile['_file']: self.edit_profile(p)
        ).pack(side="right", padx=2)
```

---

### Task 3.5: Enhanced Quick Start with Sliders

**Files:**
- Modify: `hardzilla.py`

**Step 1: Replace create_quick_start_section**

```python
def create_quick_start_section(self):
    """Create Quick Start section with category sliders and presets"""
    frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

    self.create_section_header(frame, "Quick Start",
        "Configure Firefox quickly using category sliders or preset profiles")

    # Category Sliders card
    sliders_card = self.create_card(frame, "Category Sliders")

    ctk.CTkLabel(sliders_card,
        text="Drag sliders to configure entire categories at once:",
        text_color="#a0a0a0",
        font=ctk.CTkFont(size=11)
    ).pack(anchor="w", pady=(0, 15))

    # Performance slider
    ctk.CTkLabel(sliders_card, text="⚡ PERFORMANCE",
        font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

    self.perf_slider = CategorySlider(
        sliders_card,
        label_left="Battery Saver",
        label_right="Max Power",
        icon_left="🔋",
        icon_right="🚀",
        descriptions=[
            "2 proc, 64MB cache, GPU off",
            "4 proc, 128MB cache",
            "6 proc, 256MB cache (Balanced)",
            "8 proc, 384MB cache",
            "12 proc, 512MB cache, GPU forced"
        ],
        on_change=lambda pos: self.apply_category_slider('performance', pos)
    )
    self.perf_slider.pack(fill="x", pady=(5, 15))

    # Privacy slider
    ctk.CTkLabel(sliders_card, text="🔒 PRIVACY",
        font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

    self.priv_slider = CategorySlider(
        sliders_card,
        label_left="Open",
        label_right="Paranoid",
        icon_left="🌐",
        icon_right="🛡️",
        descriptions=[
            "100% compat, no protection",
            "98% compat, basic protection",
            "95% compat (Balanced)",
            "85% compat, strong protection",
            "65% compat, maximum privacy"
        ],
        on_change=lambda pos: self.apply_category_slider('privacy', pos)
    )
    self.priv_slider.pack(fill="x", pady=(5, 15))

    # Features slider
    ctk.CTkLabel(sliders_card, text="🧪 FEATURES",
        font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

    self.feat_slider = CategorySlider(
        sliders_card,
        label_left="Conservative",
        label_right="Bleeding Edge",
        icon_left="🏛️",
        icon_right="⚡",
        descriptions=[
            "Stable defaults only",
            "Few modern features",
            "Modern + stable (Balanced)",
            "Most experimental features",
            "All experimental enabled"
        ],
        on_change=lambda pos: self.apply_category_slider('features', pos)
    )
    self.feat_slider.pack(fill="x", pady=(5, 15))

    # Apply sliders button
    ctk.CTkButton(sliders_card,
        text="Apply Slider Settings",
        width=160, height=36,
        fg_color="#2FA572",
        command=self.apply_all_sliders
    ).pack(anchor="e", pady=(10, 0))

    # Use-case presets card
    presets_card = self.create_card(frame, "Use-Case Presets")

    ctk.CTkLabel(presets_card,
        text="One-click configurations for common scenarios:",
        text_color="#a0a0a0",
        font=ctk.CTkFont(size=11)
    ).pack(anchor="w", pady=(0, 10))

    presets_frame = ctk.CTkFrame(presets_card, fg_color="transparent")
    presets_frame.pack(fill="x")

    col = 0
    row_frame = None
    for preset_id, preset in PRESET_PROFILES.items():
        if col % 3 == 0:
            row_frame = ctk.CTkFrame(presets_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)

        btn = ctk.CTkButton(row_frame,
            text=f"{preset['icon']} {preset['name']}",
            width=120, height=40,
            fg_color="#3a3a5a",
            hover_color="#4a4a6a",
            command=lambda p=preset_id: self.apply_preset_profile(p)
        )
        btn.pack(side="left", padx=4)
        col += 1

    # Import from Firefox
    import_card = self.create_card(frame, "Import")

    ctk.CTkButton(import_card,
        text="📥 Import Current Firefox Settings",
        width=250, height=40,
        fg_color="#3B8ED0",
        command=self.import_from_firefox
    ).pack(anchor="w")

    return frame
```

**Step 2: Add slider application method**

```python
def apply_category_slider(self, category: str, position: int):
    """Apply settings based on category slider position"""
    # Map positions to preset levels
    level_map = {
        'performance': ['battery', 'battery', 'balanced', 'max_power', 'max_power'],
        'privacy': ['open', 'open', 'balanced', 'paranoid', 'paranoid'],
        'features': ['conservative', 'conservative', 'balanced', 'bleeding_edge', 'bleeding_edge']
    }

    levels = level_map.get(category, ['balanced'] * 5)
    level = levels[position]

    for key, meta in SETTINGS_METADATA.items():
        if meta['category'] == category or (category == 'privacy' and meta['category'] == 'security'):
            recommended = meta.get('recommended', {})
            if level in recommended:
                self.settings_vars[key].set(recommended[level])

def apply_all_sliders(self):
    """Apply all current slider positions"""
    self.apply_category_slider('performance', self.perf_slider.get_position())
    self.apply_category_slider('privacy', self.priv_slider.get_position())
    self.apply_category_slider('features', self.feat_slider.get_position())
    messagebox.showinfo("Settings Applied", "Category slider settings have been applied.")
```

---

### Task 3.6: Update generate_preferences for New Settings

**Files:**
- Modify: `hardzilla.py`

**Step 1: Refactor generate_preferences to use metadata**

```python
def generate_preferences(self):
    """Generate Firefox preferences from settings using metadata"""
    prefs = {}

    for key, meta in SETTINGS_METADATA.items():
        if key not in self.settings_vars:
            continue

        value = self.settings_vars[key].get()
        pref_name = meta['pref']

        # Handle special cases and transformations
        if pref_name == 'browser.startup.page':
            prefs[f'"{pref_name}"'] = "3" if value else "1"
        elif pref_name.startswith('privacy.clearOnShutdown'):
            # Invert for "keep" settings
            if key.startswith('keep_'):
                prefs[f'"{pref_name}"'] = str(not value).lower()
            else:
                prefs[f'"{pref_name}"'] = str(value).lower()
        elif pref_name == 'network.cookie.cookieBehavior':
            cookie_map = {'all': '0', 'cross-site': '5', 'none': '1', 'visited': '3'}
            prefs[f'"{pref_name}"'] = cookie_map.get(value, '5')
        elif pref_name == 'network.trr.mode':
            doh_map = {'off': '0', 'default': '2', 'increased': '3', 'max': '3'}
            prefs[f'"{pref_name}"'] = doh_map.get(value, '2')
        elif pref_name == 'network.trr.uri':
            dns_map = {
                'cloudflare': '"https://cloudflare-dns.com/dns-query"',
                'quad9': '"https://dns.quad9.net/dns-query"',
                'nextdns': '"https://dns.nextdns.io"'
            }
            prefs[f'"{pref_name}"'] = dns_map.get(value, '"https://dns.quad9.net/dns-query"')
        elif pref_name == 'media.autoplay.default':
            prefs[f'"{pref_name}"'] = "5" if value == 'block' else "0"
        elif meta['type'] == 'toggle':
            prefs[f'"{pref_name}"'] = str(value).lower()
        elif meta['type'] == 'choice':
            if isinstance(value, str) and not value.isdigit():
                prefs[f'"{pref_name}"'] = f'"{value}"'
            else:
                prefs[f'"{pref_name}"'] = str(value)
        elif meta['type'] == 'number':
            prefs[f'"{pref_name}"'] = str(value)

    # Add required extensions pref
    prefs['"xpinstall.signatures.required"'] = "false"

    return prefs
```

---

## Phase 4: Testing & Documentation

### Task 4.1: Test All New Features

**Step 1: Run application**

```bash
python hardzilla.py
```

**Step 2: Test checklist**

- [ ] Quick Start sliders work
- [ ] Preset profiles apply correctly
- [ ] Profile Library shows presets
- [ ] Custom profiles can be created
- [ ] Firefox import works
- [ ] Performance settings appear
- [ ] Experimental settings appear
- [ ] Info (ⓘ) button expands details
- [ ] Apply to Firefox generates correct user.js

### Task 4.2: Update README

Update GUI_README.md with new features documentation.

---

## Summary

**Total new files:**
- `hardzilla_metadata.py` - Settings definitions (~700 lines)
- `hardzilla_widgets.py` - Custom UI widgets (~250 lines)
- `hardzilla_profiles.py` - Profile management (~150 lines)

**Modified files:**
- `hardzilla.py` - Main application (significant refactor)

**New features:**
- 100+ settings (up from 50)
- Performance section (cache, processes, GPU)
- Experimental features section
- Profile Library with 6 presets
- Custom profile creation/editing
- Firefox settings import
- Category sliders in Quick Start
- Inline descriptions + expandable details
- Enhanced Summary with impact grouping

---

