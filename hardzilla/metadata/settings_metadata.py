#!/usr/bin/env python3
"""
Hardzilla Settings Metadata
Complete metadata definitions for all Firefox hardening settings.
Part of Task 1.1 of the Hardzilla expansion plan.
"""

from typing import Dict, Any, List, Union

# Module exports
__all__ = [
    'CATEGORIES',
    'PRESET_PROFILES',
    'SETTINGS_METADATA',
    'get_base_settings',
    'get_advanced_settings',
    'get_settings_by_level',
    'get_settings_by_mechanism',
]

# =============================================================================
# CATEGORIES - Organizing settings into logical groups
# =============================================================================

CATEGORIES: Dict[str, Dict[str, Any]] = {
    'performance': {
        'name': 'Performance',
        'icon': 'speedometer',
        'description': 'Optimize Firefox speed, memory usage, and responsiveness',
        'subcategories': {
            'cache': {
                'name': 'Cache & Memory',
                'description': 'Control disk and memory caching behavior',
                'order': 1
            },
            'processes': {
                'name': 'Processes & GPU',
                'description': 'Configure multi-process architecture and GPU acceleration',
                'order': 2
            },
            'network_perf': {
                'name': 'Network Performance',
                'description': 'Tune network connections and prefetching',
                'order': 3
            }
        }
    },
    'privacy': {
        'name': 'Privacy',
        'icon': 'shield',
        'description': 'Control data collection, tracking, and personal information',
        'subcategories': {
            'session': {
                'name': 'Session & Startup',
                'description': 'Control how Firefox handles tabs and sessions between restarts',
                'order': 1
            },
            'data': {
                'name': 'Data & Cleanup',
                'description': 'Control what data to keep or clear on shutdown',
                'order': 2
            },
            'cookies': {
                'name': 'Cookies & Storage',
                'description': 'Manage cookie behavior and site data',
                'order': 3
            },
            'tracking': {
                'name': 'Tracking Protection',
                'description': 'Block trackers and fingerprinting attempts',
                'order': 4
            }
        }
    },
    'security': {
        'name': 'Security',
        'icon': 'lock',
        'description': 'Enhance browser security and protection against threats',
        'subcategories': {
            'network': {
                'name': 'Network Security',
                'description': 'DNS, HTTPS, WebRTC, and network-level protection',
                'order': 1
            },
            'permissions': {
                'name': 'Permissions & Autofill',
                'description': 'Site permissions, search suggestions, and form autofill',
                'order': 2
            }
        }
    },
    'features': {
        'name': 'Features',
        'icon': 'puzzle',
        'description': 'Enable or disable Firefox features and capabilities',
        'subcategories': {
            'media': {
                'name': 'Media & Playback',
                'description': 'Audio, video, and media handling',
                'order': 1
            },
            'permissions': {
                'name': 'Permissions',
                'description': 'Site permission defaults',
                'order': 2
            },
            'ui': {
                'name': 'User Interface',
                'description': 'Browser appearance and behavior',
                'order': 3
            },
            'ai': {
                'name': 'AI Features',
                'description': 'Machine learning and AI-powered capabilities',
                'order': 4
            },
            'graphics': {
                'name': 'Graphics & Media',
                'description': 'Image formats and graphics capabilities',
                'order': 5
            },
            'css': {
                'name': 'CSS Experimental',
                'description': 'Experimental CSS features and layouts',
                'order': 6
            },
            'dom': {
                'name': 'DOM & Network',
                'description': 'DOM APIs and network protocols',
                'order': 7
            }
        }
    }
}

# =============================================================================
# PRESET PROFILES - Quick configuration presets for different use cases
# =============================================================================

PRESET_PROFILES: Dict[str, Dict[str, Any]] = {
    # NEW: Maximum anonymity preset
    'anonymous': {
        'name': 'Anonymous / Tor-like',
        'icon': 'incognito',
        'description': 'Maximum anonymity with Tor Browser-inspired settings. Expect significant breakage.',
        'color': '#6C3483',
        'priority_profile': 'paranoid',  # FIX: Use existing 'paranoid' profile (most aggressive)
        'tags': ['anonymity', 'anti-fingerprinting', 'extreme-privacy'],
        'recommended_for': [
            'Activists and journalists',
            'Users in restrictive countries',
            'Maximum anonymity needs',
            'Whistleblowers'
        ],
        'highlights': [
            '✓ All cookies cleared on exit',
            '✓ WebRTC completely disabled',
            '✓ Canvas/WebGL fingerprinting blocked',
            '✓ First-party isolation enabled',
            '✓ Resist fingerprinting mode ON',
            '✓ No disk cache (privacy)',
            '✗ Many sites will break',
            '✗ Google/Facebook features limited',
            '✗ Video calling may not work'
        ],
        'stats': {
            'settings_changed': '70-75',
            'breakage_risk': 'Very High (9/10)',
            'privacy_score': '10/10'
        }
    },
    'privacy_enthusiast': {
        'name': 'Privacy Enthusiast',
        'icon': 'shield',
        'description': 'Maximum privacy protection with aggressive blocking. Some sites may break.',
        'color': '#9B59B6',
        'priority_profile': 'paranoid',
        'tags': ['privacy', 'security', 'anonymity'],
        'recommended_for': [
            'Privacy-conscious users',
            'Security researchers',
            'Journalists'
        ],
        'highlights': [
            '✓ All tracking cookies blocked',
            '✓ Fingerprinting resistance enabled',
            '✓ WebRTC disabled',
            '✓ Referrer headers minimized',
            '✓ DNS over HTTPS (DoH) enabled',
            '✗ Some logins may require re-entry',
            '✗ Maps and video calling affected'
        ],
        'stats': {
            'settings_changed': '60-65',
            'breakage_risk': 'High (7/10)',
            'privacy_score': '9/10'
        }
    },
    # NEW: Intermediate privacy preset
    'privacy_pro': {
        'name': 'Privacy Pro',
        'icon': 'shield-check',
        'description': 'Strong privacy protection while maintaining most site functionality.',
        'color': '#8E44AD',
        'priority_profile': 'balanced',  # FIX: Use existing 'balanced' profile (midpoint between open and paranoid)
        'tags': ['privacy', 'tracking-protection', 'balanced'],
        'recommended_for': [
            'Privacy-conscious users',
            'People who want strong protection without major breakage',
            'General users concerned about tracking'
        ],
        'highlights': [
            '✓ Blocks all third-party tracking cookies',
            '✓ Enhanced Tracking Protection (strict mode)',
            '✓ Blocks known fingerprinting scripts',
            '✓ HTTPS-only mode enabled',
            '✓ Minimal site breakage',
            '✗ Does not clear cookies on exit',
            '✗ WebRTC still enabled (for video calls)'
        ],
        'stats': {
            'settings_changed': '45-50',
            'breakage_risk': 'Low (2/10)',
            'privacy_score': '7/10'
        }
    },
    # NEW: Banking/financial preset
    'banking': {
        'name': 'Banking & Financial',
        'icon': 'bank',
        'description': 'Security-focused for online banking with anti-fingerprinting but functional forms.',
        'color': '#117A65',
        'priority_profile': 'balanced',  # FIX: Use existing 'balanced' profile (good mix of security and functionality)
        'tags': ['banking', 'security', 'anti-fraud'],
        'recommended_for': [
            'Online banking users',
            'Financial transactions',
            'E-commerce shoppers'
        ],
        'highlights': [
            '✓ Strong anti-fingerprinting',
            '✓ HTTPS-only enforced',
            '✓ Third-party cookies blocked',
            '✓ Form autofill enabled (convenience)',
            '✓ WebRTC disabled (security)',
            '✓ Password manager friendly',
            '✗ Some payment providers may need whitelisting'
        ],
        'stats': {
            'settings_changed': '40-45',
            'breakage_risk': 'Low-Medium (3/10)',
            'privacy_score': '8/10'
        }
    },
    'office': {
        'name': 'Office Worker',
        'icon': 'briefcase',
        'description': 'Balanced settings for corporate environments with compatibility for web apps and services.',
        'color': '#2FA572',
        'priority_profile': 'balanced',
        'tags': ['work', 'compatibility', 'productivity'],
        'recommended_for': [
            'Office workers',
            'Business users',
            'Web app users'
        ],
        'highlights': [
            '✓ Web app compatibility maintained',
            '✓ Moderate tracking protection',
            '✓ Form autofill enabled',
            '✓ Balanced performance/privacy',
            '✗ Some tracking still allowed',
            '✗ Third-party cookies permitted for functionality'
        ],
        'stats': {
            'settings_changed': '35-40',
            'breakage_risk': 'Very Low (1/10)',
            'privacy_score': '5/10'
        }
    },
    'developer': {
        'name': 'Developer',
        'icon': 'code',
        'description': 'Optimized for web development with DevTools performance and debugging features enabled.',
        'color': '#3B8ED0',
        'priority_profile': 'max_power',
        'tags': ['development', 'debugging', 'performance'],
        'recommended_for': [
            'Web developers',
            'Frontend engineers',
            'DevTools users'
        ],
        'highlights': [
            '✓ DevTools performance optimized',
            '✓ Source maps enabled',
            '✓ Remote debugging allowed',
            '✓ Cache persistence enabled',
            '✗ Minimal privacy protections',
            '✗ Tracking allowed for compatibility'
        ],
        'stats': {
            'settings_changed': '30-35',
            'breakage_risk': 'None (0/10)',
            'privacy_score': '2/10'
        }
    },
    'laptop': {
        'name': 'Laptop / Battery Saver',
        'icon': 'battery',
        'description': 'Optimized for battery life with reduced resource usage and background activity.',
        'color': '#27AE60',
        'priority_profile': 'battery',
        'tags': ['battery', 'efficiency', 'mobile'],
        'recommended_for': [
            'Laptop users',
            'Mobile workers',
            'Battery-conscious users'
        ],
        'highlights': [
            '✓ Reduced background activity',
            '✓ Lower GPU usage',
            '✓ Smaller cache sizes',
            '✓ Network prefetching disabled',
            '✗ Slightly slower page loads',
            '✗ Some animations reduced'
        ],
        'stats': {
            'settings_changed': '25-30',
            'breakage_risk': 'None (0/10)',
            'privacy_score': '4/10'
        }
    },
    'gaming': {
        'name': 'Gaming / Streaming',
        'icon': 'gamepad',
        'description': 'Maximum performance for gaming sites and streaming with GPU acceleration enabled.',
        'color': '#E74C3C',
        'priority_profile': 'max_power',
        'tags': ['gaming', 'streaming', 'performance'],
        'recommended_for': [
            'Gamers',
            'Streamers',
            'Media enthusiasts'
        ],
        'highlights': [
            '✓ GPU acceleration maximized',
            '✓ WebGL/WebRTC enabled',
            '✓ Large cache sizes',
            '✓ Hardware video decoding',
            '✗ No privacy protections',
            '✗ Full tracking exposure'
        ],
        'stats': {
            'settings_changed': '30-35',
            'breakage_risk': 'None (0/10)',
            'privacy_score': '1/10'
        }
    },
    'casual': {
        'name': 'Casual Browser',
        'icon': 'globe',
        'description': 'Default-like experience with minor privacy improvements. Maximum compatibility.',
        'color': '#F39C12',
        'priority_profile': 'open',
        'tags': ['casual', 'compatibility', 'easy'],
        'recommended_for': [
            'General users',
            'Non-technical users',
            'Maximum compatibility needs'
        ],
        'highlights': [
            '✓ Firefox defaults maintained',
            '✓ Basic tracking protection only',
            '✓ Maximum site compatibility',
            '✓ All features enabled',
            '✗ Minimal privacy improvements',
            '✗ Tracking mostly allowed'
        ],
        'stats': {
            'settings_changed': '10-15',
            'breakage_risk': 'None (0/10)',
            'privacy_score': '3/10'
        }
    }
}

# =============================================================================
# SETTINGS METADATA - Complete metadata for all performance settings
# =============================================================================

SETTINGS_METADATA: Dict[str, Dict[str, Any]] = {

    # =========================================================================
    # CACHE & MEMORY (subcategory: 'cache')
    # =========================================================================

    'disk_cache_enabled': {
        'name': 'Disk Cache',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Store cached files on disk for faster page loads on revisits.',
        'full': (
            'When enabled, Firefox stores website resources (images, scripts, stylesheets) '
            'on your hard drive. This significantly speeds up loading of frequently visited '
            'sites since resources can be loaded from disk instead of downloaded again. '
            'Disabling this reduces disk writes (good for SSDs) but increases bandwidth usage '
            'and slower repeat visits. Privacy-conscious users may disable this to prevent '
            'leaving traces of browsing activity on disk.'
        ),
        'pref': 'browser.cache.disk.enable',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
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
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Maximum disk space for cached web content.',
        'full': (
            'Sets the maximum amount of disk space Firefox will use for caching web content. '
            'Larger cache sizes allow more content to be stored, improving load times for '
            'frequently visited sites with lots of resources. Smaller sizes use less disk space '
            'but may result in more frequent cache evictions. The default auto-sizing usually '
            'works well, but power users may want to increase this for faster browsing or '
            'decrease it to save disk space.'
        ),
        'pref': 'browser.cache.disk.capacity',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [102400, 262144, 524288, 1048576],
        'labels': ['100 MB', '256 MB', '512 MB', '1 GB'],
        'default': 262144,
        'recommended': {
            'max_power': 1048576,
            'balanced': 524288,
            'battery': 262144,
            'paranoid': 102400,
            'open': 524288
        }
    },

    'memory_cache_enabled': {
        'name': 'Memory Cache',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Store cached content in RAM for fastest possible access.',
        'full': (
            'When enabled, Firefox keeps frequently accessed web content in system memory (RAM) '
            'for instant access. This provides the fastest possible cache performance since RAM '
            'is much faster than disk storage. The memory cache works alongside the disk cache, '
            'storing the most recently and frequently used items. Disabling this can save memory '
            'but will slow down page loads and navigation.'
        ),
        'pref': 'browser.cache.memory.enable',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'memory_cache_size': {
        'name': 'Memory Cache Size',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Maximum RAM for cached web content.',
        'full': (
            'Sets the maximum amount of system memory (RAM) Firefox will use for caching. '
            'A value of -1 lets Firefox automatically determine the size based on available '
            'system memory. Larger values improve performance for users who frequently switch '
            'between tabs or revisit pages, while smaller values conserve memory for other '
            'applications. Users with 16GB+ RAM can safely increase this, while users with '
            'limited RAM may want to reduce it.'
        ),
        'pref': 'browser.cache.memory.capacity',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [65536, 262144, 524288, 1048576],
        'labels': ['64 MB', '256 MB', '512 MB', '1 GB'],
        'default': -1,  # -1 means auto in Firefox
        'recommended': {
            'max_power': 1048576,
            'balanced': 524288,
            'battery': 262144,
            'paranoid': 262144,
            'open': 524288
        }
    },

    'session_history_entries': {
        'name': 'Session History Entries',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Number of back/forward history entries per tab.',
        'full': (
            'Controls how many pages Firefox remembers in the back/forward history for each tab. '
            'Higher values let you navigate further back but use more memory per tab. Each entry '
            'stores page state, scroll position, and form data. Reducing this value saves memory, '
            'especially with many open tabs. Power users who frequently navigate back through '
            'long browsing sessions may want higher values, while memory-conscious users should '
            'keep it lower.'
        ),
        'pref': 'browser.sessionhistory.max_entries',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [5, 25, 50],
        'labels': ['5 entries', '25 entries', '50 entries'],
        'default': 50,
        'recommended': {
            'max_power': 50,
            'balanced': 25,
            'battery': 5,
            'paranoid': 5,
            'open': 50
        }
    },

    'cached_pages': {
        'name': 'Cached Pages in Memory',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Number of pages kept fully rendered in memory for instant back/forward.',
        'full': (
            'Controls the Back-Forward Cache (bfcache), which keeps recently visited pages '
            'fully rendered in memory. This enables instant back/forward navigation without '
            'reloading. A value of 0 disables bfcache entirely, saving memory but requiring '
            'page reloads. Higher values keep more pages cached for faster navigation. Each '
            'cached page can use significant memory (10-50MB+), so balance between performance '
            'and memory usage based on your system resources.'
        ),
        'pref': 'browser.sessionhistory.max_total_viewers',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'none',
        'values': [0, 1, 4, 8],
        'labels': ['Disabled', '1 page', '4 pages', '8 pages'],
        'default': -1,  # -1 means auto in Firefox
        'recommended': {
            'max_power': 8,
            'balanced': 4,
            'battery': 1,
            'paranoid': 0,
            'open': 4
        }
    },

    'session_save_interval': {
        'name': 'Session Save Interval',
        'category': 'performance',
        'subcategory': 'cache',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'How often Firefox saves session data to disk.',
        'full': (
            'Controls how frequently Firefox saves your current session (open tabs, windows, '
            'form data) to disk. More frequent saves provide better crash recovery but increase '
            'disk I/O and can cause brief freezes, especially with many tabs. Less frequent '
            'saves reduce disk activity and improve responsiveness but risk losing more data '
            'if Firefox crashes. SSD users can safely use shorter intervals, while HDD users '
            'may prefer longer intervals to reduce disk wear.'
        ),
        'pref': 'browser.sessionstore.interval',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [10000, 60000, 120000, 600000],
        'labels': ['10 seconds', '1 minute', '2 minutes', '10 minutes'],
        'default': 15000,
        'recommended': {
            'max_power': 60000,
            'balanced': 60000,
            'battery': 600000,
            'paranoid': 600000,
            'open': 15000
        }
    },

    # =========================================================================
    # PROCESSES & GPU (subcategory: 'processes')
    # =========================================================================

    'content_processes': {
        'name': 'Content Processes',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Number of separate processes for rendering web content.',
        'full': (
            'Firefox uses multiple processes to render web pages, isolating tabs for stability '
            'and security. More processes allow better parallelization on multi-core CPUs and '
            'prevent one misbehaving tab from affecting others. However, each process has memory '
            'overhead (50-100MB+). Systems with 8+ cores and 16GB+ RAM benefit from 8+ processes, '
            'while systems with fewer resources should use fewer. The optimal value depends on '
            'your CPU cores and available RAM.'
        ),
        'pref': 'dom.ipc.processCount',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'none',
        'values': [2, 4, 6, 8, 12],
        'labels': ['2 processes', '4 processes', '6 processes', '8 processes', '12 processes'],
        'default': 8,
        'recommended': {
            'max_power': 12,
            'balanced': 8,
            'battery': 4,
            'paranoid': 8,
            'open': 8
        }
    },

    'isolated_processes': {
        'name': 'Isolated Web Processes',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Number of isolated processes per site for enhanced security.',
        'full': (
            'Controls how many isolated content processes Firefox uses for Site Isolation '
            '(Fission). Site Isolation places each site in its own process, preventing Spectre-'
            'style attacks and cross-site data leaks. More processes provide stronger isolation '
            'but increase memory usage. This is separate from the main content process count and '
            'adds additional security layers. Users handling sensitive information should use '
            'higher values, while memory-constrained systems may need to reduce this.'
        ),
        'pref': 'dom.ipc.processCount.webIsolated',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [1, 2, 4],
        'labels': ['1 process', '2 processes', '4 processes'],
        'default': 4,
        'recommended': {
            'max_power': 4,
            'balanced': 4,
            'battery': 2,
            'paranoid': 4,
            'open': 2
        }
    },

    'webrender_enabled': {
        'name': 'WebRender',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Use GPU-accelerated rendering engine for smoother graphics.',
        'full': (
            'WebRender is a GPU-based rendering engine that offloads page rendering to your '
            'graphics card. This provides smoother scrolling, animations, and overall '
            'responsiveness, especially on high-DPI displays and complex pages. WebRender '
            'works best with modern GPUs (2015+) and up-to-date drivers. On older or '
            'unsupported hardware, it may cause visual glitches or reduced performance. '
            'If you experience rendering issues, try disabling this setting.'
        ),
        'pref': 'gfx.webrender.all',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False,
            'paranoid': True,
            'open': True
        }
    },

    'gpu_acceleration': {
        'name': 'Force GPU Acceleration',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Force hardware acceleration even on unsupported configurations.',
        'full': (
            'Forces Firefox to use GPU acceleration for compositing and rendering, bypassing '
            'the automatic hardware compatibility checks. This can improve performance on '
            'systems where Firefox incorrectly blacklists the GPU. However, forcing acceleration '
            'on truly incompatible hardware can cause crashes, visual corruption, or system '
            'instability. Only enable this if you know your GPU should be supported and Firefox '
            'is not using it. Test thoroughly after enabling.'
        ),
        'pref': 'layers.acceleration.force-enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Forced', 'Auto'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    },

    'gpu_process': {
        'name': 'GPU Process',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Run GPU operations in a separate process for stability.',
        'full': (
            'Isolates GPU operations into a dedicated process separate from the main browser '
            'process. This improves stability by preventing GPU driver crashes from taking down '
            'the entire browser. If the GPU process crashes, Firefox can recover without losing '
            'your tabs. This adds slight overhead but significantly improves reliability, '
            'especially with less stable GPU drivers. Recommended for most users unless '
            'troubleshooting specific GPU issues.'
        ),
        'pref': 'layers.gpu-process.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'hardware_video': {
        'name': 'Hardware Video Decoding',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Use GPU for video decoding to reduce CPU usage.',
        'full': (
            'Enables hardware-accelerated video decoding, offloading video processing from the '
            'CPU to the GPU. This dramatically reduces CPU usage during video playback, improves '
            'battery life on laptops, and enables smooth playback of high-resolution (4K/8K) '
            'content. Most modern GPUs support H.264, VP9, and AV1 decoding. Disable only if '
            'you experience video playback issues, color problems, or crashes during video playback.'
        ),
        'pref': 'media.hardware-video-decoding.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'webgl_enabled': {
        'name': 'Force WebGL',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Force WebGL support for 3D graphics in web pages.',
        'full': (
            'WebGL enables hardware-accelerated 3D graphics in web pages, required for 3D games, '
            'data visualizations, Google Maps 3D, and many interactive experiences. This setting '
            'forces WebGL to be enabled even on blacklisted GPU configurations. Note that WebGL '
            'can be used for fingerprinting since it exposes GPU information. Privacy-focused '
            'users may want to keep this disabled unless needed, while gamers and developers '
            'should enable it for full functionality.'
        ),
        'pref': 'webgl.force-enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Forced', 'Auto'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    },

    'webgpu_enabled': {
        'name': 'WebGPU',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable next-generation GPU API for advanced graphics and compute.',
        'full': (
            'WebGPU is a modern graphics API providing low-level GPU access for advanced 3D '
            'graphics and GPU compute in web pages. It offers better performance than WebGL '
            'for compatible applications but is still experimental. WebGPU is used by some '
            'cutting-edge web games, AI/ML demos, and graphics applications. Enable this if '
            'you need access to WebGPU content. Note this is still maturing and may have '
            'compatibility issues with some sites or drivers.'
        ),
        'pref': 'dom.webgpu.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    },

    'frame_rate': {
        'name': 'Frame Rate Limit',
        'category': 'performance',
        'subcategory': 'processes',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Maximum frame rate for rendering and animations.',
        'full': (
            'Sets the maximum frames per second (FPS) for page rendering, animations, and '
            'scrolling. Higher values provide smoother visuals but increase GPU and CPU usage. '
            'A value of -1 removes the limit, allowing Firefox to render as fast as possible '
            '(useful for high-refresh-rate monitors). 60 FPS is sufficient for most users, '
            'while 144 FPS benefits users with 120Hz+ displays. Lower values like 30 FPS '
            'significantly reduce power consumption but may feel less smooth.'
        ),
        'pref': 'layout.frame_rate',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [30, 60, 144, -1],
        'labels': ['30 FPS', '60 FPS', '144 FPS', 'Unlimited'],
        'default': -1,
        'recommended': {
            'max_power': -1,
            'balanced': 60,
            'battery': 30,
            'paranoid': 60,
            'open': 60
        }
    },

    # =========================================================================
    # NETWORK PERFORMANCE (subcategory: 'network_perf')
    # =========================================================================

    'max_connections': {
        'name': 'Maximum Connections',
        'category': 'performance',
        'subcategory': 'network_perf',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Maximum total simultaneous network connections.',
        'full': (
            'Sets the maximum number of simultaneous HTTP connections Firefox can open across '
            'all sites. Higher values allow more parallel downloads and faster loading of '
            'pages with many resources, but may strain network equipment or trigger rate '
            'limiting. The default of 900 works well for most users. Power users with fast '
            'connections may benefit from higher values, while users on constrained networks '
            '(mobile hotspots, shared connections) may want lower values to avoid issues.'
        ),
        'pref': 'network.http.max-connections',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [256, 900, 1200, 1800],
        'labels': ['256 (Conservative)', '900 (Default)', '1200 (High)', '1800 (Maximum)'],
        'default': 900,
        'recommended': {
            'max_power': 1800,
            'balanced': 900,
            'battery': 256,
            'paranoid': 256,
            'open': 900
        }
    },

    'connections_per_server': {
        'name': 'Connections Per Server',
        'category': 'performance',
        'subcategory': 'network_perf',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Maximum simultaneous connections to each server.',
        'full': (
            'Limits concurrent connections to a single server (domain). HTTP/1.1 benefits from '
            'multiple connections for parallel resource loading, while HTTP/2 and HTTP/3 '
            'multiplex requests over fewer connections. Higher values speed up loading from '
            'sites with many resources but may trigger server-side rate limiting. Most modern '
            'sites use HTTP/2+, making this less impactful. The default of 6 balances '
            'performance with server friendliness.'
        ),
        'pref': 'network.http.max-persistent-connections-per-server',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [4, 6, 8, 10],
        'labels': ['4 connections', '6 connections', '8 connections', '10 connections'],
        'default': 6,
        'recommended': {
            'max_power': 10,
            'balanced': 6,
            'battery': 4,
            'paranoid': 4,
            'open': 6
        }
    },

    'speculative_connections': {
        'name': 'Speculative Connections',
        'category': 'performance',
        'subcategory': 'network_perf',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Pre-open connections to links you might click.',
        'full': (
            'Firefox can speculatively open connections to links when you hover over them or '
            'the page predicts you might click them. This reduces latency when you do click, '
            'making navigation feel faster. However, this generates extra network traffic and '
            'leaks information about your browsing behavior (sites know when you hover). '
            'Privacy-focused users should set this to 0 to disable. Performance-focused users '
            'can increase it for faster perceived navigation.'
        ),
        'pref': 'network.http.speculative-parallel-limit',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [0, 4, 8, 20],
        'labels': ['Disabled', '4 connections', '8 connections', '20 connections'],
        'default': 6,
        'recommended': {
            'max_power': 20,
            'balanced': 8,
            'battery': 0,
            'paranoid': 0,
            'open': 8
        }
    },

    # =========================================================================
    # EXPERIMENTAL FEATURES - UI & TABS (subcategory: 'ui')
    # =========================================================================

    'tab_groups': {
        'name': 'Tab Groups',
        'category': 'features',
        'subcategory': 'ui',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable tab grouping to organize tabs into collapsible groups.',
        'full': (
            'Tab Groups allow you to organize your open tabs into named, collapsible groups. '
            'This helps manage many open tabs by grouping related tabs together (e.g., work, '
            'research, shopping). Groups can be collapsed to save tab bar space and expanded '
            'when needed. This is a newer Firefox feature that improves tab management for '
            'users who work with many tabs. Enable this for better tab organization.'
        ),
        'pref': 'browser.tabs.groups.enabled',
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

    'smart_tab_groups': {
        'name': 'Smart Tab Groups',
        'category': 'features',
        'subcategory': 'ui',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'AI-powered automatic tab grouping based on content.',
        'full': (
            'Smart Tab Groups uses machine learning to automatically organize your tabs into '
            'logical groups based on their content and your browsing patterns. Firefox analyzes '
            'page topics, domains, and your behavior to suggest or create groups automatically. '
            'This experimental feature requires the base Tab Groups feature to be enabled. '
            'It may use additional system resources for ML inference. Enable for automatic '
            'tab organization without manual effort.'
        ),
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
        'name': 'New Sidebar Design',
        'category': 'features',
        'subcategory': 'ui',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable the redesigned Firefox sidebar interface.',
        'full': (
            'The sidebar revamp introduces a modernized sidebar design with improved aesthetics '
            'and functionality. The new design includes better integration with vertical tabs, '
            'bookmarks, history, and other sidebar panels. It features a cleaner look, smoother '
            'animations, and improved accessibility. This experimental redesign may change in '
            'future Firefox versions. Enable to preview the new sidebar experience.'
        ),
        'pref': 'sidebar.revamp',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    'vertical_tabs': {
        'name': 'Vertical Tabs',
        'category': 'features',
        'subcategory': 'ui',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Display tabs vertically in the sidebar instead of horizontally.',
        'full': (
            'Vertical Tabs moves the tab bar from the top of the browser to a sidebar on the '
            'left. This provides more space for tab titles, better visibility with many tabs, '
            'and takes advantage of modern widescreen displays. Vertical tabs work well with '
            'the sidebar revamp feature. This layout is particularly useful for users who '
            'keep many tabs open and want to see more of each tab title. Requires the new '
            'sidebar design to be enabled for full functionality.'
        ),
        'pref': 'sidebar.verticalTabs',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    # =========================================================================
    # EXPERIMENTAL FEATURES - AI FEATURES (subcategory: 'ai')
    # =========================================================================

    'ml_enabled': {
        'name': 'Machine Learning Features',
        'category': 'features',
        'subcategory': 'ai',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable Firefox machine learning capabilities.',
        'full': (
            'This master toggle enables Firefox machine learning features that run locally '
            'on your device. ML features include smart suggestions, content analysis, and '
            'AI-powered assistance. All ML inference happens on-device for privacy - no data '
            'is sent to external servers. Enabling this allows other ML-based features to '
            'function. May increase CPU/memory usage during inference. This is the foundation '
            'for AI-powered features in Firefox.'
        ),
        'pref': 'browser.ml.enable',
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

    'ai_chat': {
        'name': 'Built-in AI Assistant',
        'category': 'features',
        'subcategory': 'ai',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable the integrated AI chat assistant in Firefox.',
        'full': (
            'The built-in AI assistant provides conversational AI capabilities directly in '
            'Firefox. You can ask questions, get help with content, summarize pages, and '
            'more. The assistant integrates with your browsing context to provide relevant '
            'help. This feature requires the ML Features toggle to be enabled. The AI can '
            'help with writing, research, and understanding web content. Enable for AI-powered '
            'browsing assistance.'
        ),
        'pref': 'browser.ml.chat.enabled',
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

    'ai_chat_sidebar': {
        'name': 'AI Chat in Sidebar',
        'category': 'features',
        'subcategory': 'ai',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Show the AI assistant in the browser sidebar.',
        'full': (
            'When enabled, the AI chat assistant appears in the browser sidebar for easy access '
            'while browsing. This allows you to interact with the AI without leaving your '
            'current page or opening a new tab. The sidebar provides a persistent chat interface '
            'that stays available as you navigate. Requires both ML Features and AI Chat to be '
            'enabled. Disable if you prefer accessing AI chat through other means or want to '
            'save sidebar space.'
        ),
        'pref': 'browser.ml.chat.sidebar',
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

    'link_preview': {
        'name': 'AI Link Previews',
        'category': 'features',
        'subcategory': 'ai',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Show AI-generated previews when hovering over links.',
        'full': (
            'AI Link Previews uses machine learning to generate quick summaries of linked '
            'pages when you hover over them. This helps you decide whether to click a link '
            'without loading the full page. The AI analyzes link context and may fetch '
            'partial page content to generate previews. This feature requires ML Features '
            'to be enabled and may increase network activity. Enable for smarter link '
            'browsing and quick content previews.'
        ),
        'pref': 'browser.ml.linkPreview.enabled',
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

    'visual_search': {
        'name': 'Visual Search',
        'category': 'features',
        'subcategory': 'ai',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Search the web using images instead of text.',
        'full': (
            'Visual Search allows you to search using images by right-clicking on any image '
            'or selecting a region of the page. Firefox uses ML to analyze the image and '
            'find similar images or related information on the web. This is useful for '
            'identifying products, finding image sources, or learning about objects in '
            'photos. The feature integrates with your default search engine visual search '
            'capabilities. Enable for image-based web searching.'
        ),
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

    # =========================================================================
    # EXPERIMENTAL FEATURES - GRAPHICS & MEDIA (subcategory: 'graphics')
    # =========================================================================

    'avif_enabled': {
        'name': 'AVIF Image Format',
        'category': 'features',
        'subcategory': 'graphics',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable support for AVIF image format.',
        'full': (
            'AVIF (AV1 Image File Format) is a modern image format based on the AV1 video '
            'codec. It offers significantly better compression than JPEG and PNG while '
            'maintaining high quality, resulting in faster page loads and reduced bandwidth. '
            'AVIF also supports features like HDR, wide color gamut, and transparency. '
            'Most modern websites now offer AVIF images. This format is well-supported and '
            'stable. Enable for better image quality and faster loading.'
        ),
        'pref': 'image.avif.enabled',
        'type': 'toggle',
        'impact': 'medium',
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

    'avif_animated': {
        'name': 'Animated AVIF',
        'category': 'features',
        'subcategory': 'graphics',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable support for animated AVIF images.',
        'full': (
            'Animated AVIF (AVIF sequences) allows AVIF images to contain multiple frames, '
            'similar to animated GIFs but with much better compression and quality. This '
            'enables smoother animations with smaller file sizes and support for more colors. '
            'Some websites are starting to use animated AVIF as a modern replacement for GIFs. '
            'Decoding animated AVIF requires more CPU power than static images. Enable for '
            'support of animated content in the AVIF format.'
        ),
        'pref': 'image.avif.sequence.enabled',
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

    'jxl_enabled': {
        'name': 'JPEG XL Format',
        'category': 'features',
        'subcategory': 'graphics',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable JPEG XL image format support (Nightly only).',
        'full': (
            'JPEG XL (JXL) is a next-generation image format designed to replace JPEG with '
            'better compression, quality, and features. It supports lossless transcoding from '
            'JPEG, progressive decoding, HDR, and animations. JXL offers superior compression '
            'compared to JPEG at the same quality level. Note: This feature is experimental '
            'and primarily available in Firefox Nightly builds. The format is still gaining '
            'adoption. Enable to test JPEG XL support on compatible Firefox versions.'
        ),
        'pref': 'image.jxl.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': False,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    # =========================================================================
    # EXPERIMENTAL FEATURES - CSS EXPERIMENTAL (subcategory: 'css')
    # =========================================================================

    'scroll_animations': {
        'name': 'Scroll-Driven Animations',
        'category': 'features',
        'subcategory': 'css',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable CSS animations triggered by scroll position.',
        'full': (
            'Scroll-driven animations allow CSS animations to progress based on scroll '
            'position rather than time. This enables effects like parallax scrolling, '
            'scroll-linked progress bars, and elements that animate as they enter the viewport. '
            'This modern CSS feature provides smooth, performant scroll effects without '
            'JavaScript. Websites using this feature will have enhanced scrolling experiences. '
            'Enable to experience scroll-based animations on supporting websites.'
        ),
        'pref': 'layout.css.scroll-driven-animations.enabled',
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

    'css_masonry': {
        'name': 'CSS Masonry Layout',
        'category': 'features',
        'subcategory': 'css',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable CSS Grid masonry layout support.',
        'full': (
            'CSS Masonry layout extends CSS Grid to allow items to flow into gaps left by '
            'shorter items, creating Pinterest-style layouts without JavaScript. This '
            'provides native browser support for a popular layout pattern previously requiring '
            'JavaScript libraries like Masonry.js. The feature is still experimental and being '
            'standardized. Enable to see native masonry layouts on websites that support it, '
            'with better performance than JavaScript alternatives.'
        ),
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
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable the CSS :has() parent selector.',
        'full': (
            'The CSS :has() selector (also known as the parent selector) allows selecting '
            'elements based on their descendants. For example, styling a card differently '
            'if it contains an image. This powerful selector enables styling patterns that '
            'previously required JavaScript. The :has() selector is now widely supported '
            'in modern browsers. Enable for full CSS :has() functionality on websites that '
            'use this modern selector for enhanced styling.'
        ),
        'pref': 'layout.css.has-selector.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On', 'Off'],
        'default': True,
        'recommended': {
            'bleeding_edge': True,
            'balanced': False,
            'conservative': False
        }
    },

    # =========================================================================
    # EXPERIMENTAL FEATURES - DOM & NETWORK (subcategory: 'dom')
    # =========================================================================

    'sanitizer_api': {
        'name': 'Sanitizer API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable the HTML Sanitizer API for safe content injection.',
        'full': (
            'The Sanitizer API provides a built-in way to safely insert untrusted HTML content '
            'into web pages by removing potentially dangerous elements and attributes. This '
            'helps prevent XSS (cross-site scripting) attacks when websites need to display '
            'user-generated content. The API is standardized and provides consistent sanitization '
            'across browsers. Enable to support websites using the native Sanitizer API for '
            'enhanced security when handling dynamic content.'
        ),
        'pref': 'dom.security.sanitizer.enabled',
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

    'http3_enabled': {
        'name': 'HTTP/3 Protocol',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable HTTP/3 (QUIC) for faster, more reliable connections.',
        'full': (
            'HTTP/3 is the latest version of HTTP, built on the QUIC transport protocol instead '
            'of TCP. It provides faster connection establishment, better performance on unreliable '
            'networks, and reduced latency. HTTP/3 is especially beneficial on mobile networks '
            'and high-latency connections. Many major websites (Google, Facebook, Cloudflare) '
            'already support HTTP/3. This protocol is stable and widely deployed. Enable for '
            'improved connection performance and reliability.'
        ),
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
            'conservative': False
        }
    },

    'webtransport': {
        'name': 'WebTransport API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable WebTransport for low-latency client-server communication.',
        'full': (
            'WebTransport is a modern API for bidirectional, low-latency communication between '
            'web clients and servers using HTTP/3. It provides better performance than WebSockets '
            'for use cases like real-time gaming, live streaming, and collaborative applications. '
            'WebTransport supports both reliable and unreliable data channels, making it suitable '
            'for applications where occasional packet loss is acceptable for lower latency. Enable '
            'for access to WebTransport-powered applications and services.'
        ),
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

    # =========================================================================
    # PRIVACY - SESSION (subcategory: 'session')
    # =========================================================================

    'restore_session': {
        'name': 'Restore Session',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Restore tabs from your last session when Firefox starts.',
        'full': (
            'When enabled, Firefox will restore all windows and tabs from your previous browsing '
            'session when you start the browser. This is convenient for continuing where you left '
            'off, but stores session data on disk. For privacy, disabling this prevents Firefox '
            'from remembering what tabs you had open. Works with the "Keep session data" setting '
            'to fully preserve your browsing state between restarts.'
        ),
        'pref': 'browser.startup.page',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [3, 1],  # 3 = restore session, 1 = homepage
        'labels': ['Restore Session', 'Open Homepage'],
        'default': 3,
        'recommended': {
            'balanced': 3,
            'paranoid': 1,
            'open': 3
        }
    },

    'restore_pinned': {
        'name': 'Restore Pinned Tabs on Demand',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Load pinned tabs only when you click on them.',
        'full': (
            'When enabled, pinned tabs from your previous session are not loaded immediately on '
            'startup. Instead, they remain unloaded until you click on them. This speeds up Firefox '
            'startup time, reduces initial memory usage, and saves bandwidth. Useful if you have '
            'many pinned tabs but do not need them all immediately. Disable for instant access to '
            'all pinned tabs when Firefox starts.'
        ),
        'pref': 'browser.sessionstore.restore_pinned_tabs_on_demand',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On Demand', 'Immediate'],
        'default': False,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    'restore_from_crash': {
        'name': 'Restore After Crash',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Automatically restore your session after Firefox crashes.',
        'full': (
            'When enabled, if Firefox crashes unexpectedly, it will offer to restore your previous '
            'session including all open tabs, windows, and form data. This prevents data loss from '
            'crashes but requires Firefox to continuously save session state to disk. For maximum '
            'privacy, disable this to prevent session data from being stored. Most users should '
            'keep this enabled for crash recovery.'
        ),
        'pref': 'browser.sessionstore.resume_from_crash',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    'lazy_restore': {
        'name': 'Lazy Session Restore',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Load tabs on demand instead of all at once.',
        'full': (
            'When enabled, tabs from your restored session are not loaded until you click on them. '
            'This dramatically speeds up Firefox startup time when you have many tabs, reduces '
            'initial memory and CPU usage, and saves bandwidth. Tabs show their title and favicon '
            'but do not fetch content until selected. Highly recommended for users with many tabs. '
            'Disable only if you need all tabs loaded immediately on startup.'
        ),
        'pref': 'browser.sessionstore.restore_on_demand',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['On Demand', 'All at Once'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    # =========================================================================
    # PRIVACY - SESSION: Home Page & New Tab Settings
    # =========================================================================

    'newtab_topsites': {
        'name': 'Show Frequently Visited Sites',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display your most visited sites on the new tab page.',
        'full': (
            'When enabled, Firefox shows a grid of your most frequently visited websites on the '
            'new tab page and home page. While convenient for quick access, this reveals your '
            'browsing habits to anyone who can see your screen. For privacy, disable this to '
            'prevent your browsing patterns from being displayed. Top sites are stored locally '
            'and not sent to Mozilla.'
        ),
        'pref': 'browser.newtabpage.activity-stream.feeds.topsites',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    'newtab_highlights': {
        'name': 'Show Recent Activity',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display recent downloads, bookmarks, and visited pages.',
        'full': (
            'When enabled, Firefox shows "Highlights" on the new tab page - a section featuring '
            'your recent downloads, newly bookmarked pages, and recently visited sites. This '
            'provides quick access to recent activity but exposes your browsing history on screen. '
            'Disable for privacy to prevent recent activity from being displayed on the new tab page.'
        ),
        'pref': 'browser.newtabpage.activity-stream.feeds.section.highlights',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'newtab_pocket': {
        'name': 'Show Pocket Recommendations',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display recommended articles from Pocket on the new tab page.',
        'full': (
            'When enabled, Firefox shows "Recommended by Pocket" stories on your new tab page. '
            'These are curated articles selected by Pocket (owned by Mozilla). While the selection '
            'is not personalized based on your browsing, displaying third-party content recommendations '
            'may be unwanted. Disable to remove Pocket stories from your new tab page entirely.'
        ),
        'pref': 'browser.newtabpage.activity-stream.feeds.section.topstories',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'newtab_sponsored': {
        'name': 'Show Sponsored Shortcuts',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display sponsored/advertising shortcuts on the new tab page.',
        'full': (
            'When enabled, Firefox may show sponsored shortcuts (paid placements) in your top '
            'sites section. These are advertisements that Mozilla receives payment for displaying. '
            'While they help fund Firefox development, they represent advertising content. '
            'Disable to remove all sponsored shortcuts from your new tab page.'
        ),
        'pref': 'browser.newtabpage.activity-stream.showSponsoredTopSites',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'newtab_sponsored_stories': {
        'name': 'Show Sponsored Stories',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display sponsored articles in Pocket recommendations.',
        'full': (
            'When enabled, sponsored (paid) articles may appear among the Pocket recommendations '
            'on your new tab page. These are advertisements disguised as article recommendations. '
            'Disable to ensure only organic Pocket recommendations are shown, or disable Pocket '
            'entirely with the "Show Pocket Recommendations" setting.'
        ),
        'pref': 'browser.newtabpage.activity-stream.showSponsored',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'newtab_search': {
        'name': 'Show Search on New Tab',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display a search bar on the new tab page.',
        'full': (
            'When enabled, Firefox displays a prominent search bar on the new tab page. This '
            'provides quick access to search but is redundant with the address bar which also '
            'supports search. Some users prefer a minimal new tab page without the search bar. '
            'Disable to remove the search bar from the new tab page (you can still search via '
            'the address bar).'
        ),
        'pref': 'browser.newtabpage.activity-stream.showSearch',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },

    'newtab_weather': {
        'name': 'Show Weather Widget',
        'category': 'privacy',
        'subcategory': 'session',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Display weather information on the new tab page.',
        'full': (
            'When enabled, Firefox shows current weather information on the new tab page. This '
            'requires Firefox to know your approximate location to fetch relevant weather data. '
            'While convenient, this involves location-based data requests. Disable to remove the '
            'weather widget and prevent location-based weather lookups.'
        ),
        'pref': 'browser.newtabpage.activity-stream.showWeather',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show', 'Hide'],
        'default': True,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    # =========================================================================
    # PRIVACY - DATA (subcategory: 'data')
    # =========================================================================

    'sanitize_on_shutdown': {
        'name': 'Clear Data on Shutdown (Master Switch)',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Enable clearing of selected data when Firefox closes.',
        'full': (
            'MASTER SWITCH: This must be enabled for ANY of the individual shutdown clearing '
            'settings to take effect (cookies, history, cache, downloads, form data, etc.). '
            'Without this enabled, all privacy.clearOnShutdown.* preferences are silently ignored '
            'by Firefox. Enable this first, then configure which data types to clear below.'
        ),
        'pref': 'privacy.sanitize.sanitizeOnShutdown',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    'keep_cookies': {
        'name': 'Keep Cookies on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Preserve website cookies when Firefox closes.',
        'full': (
            'When enabled, cookies are NOT cleared when Firefox shuts down. Cookies store login '
            'sessions, site preferences, and shopping carts. Keeping cookies means you stay logged '
            'into websites between browser sessions. For privacy, disable this to clear all cookies '
            'on exit, but you will need to log in again to all websites each time you start Firefox. '
            'Consider using container tabs or cookie exceptions for important logins.'
        ),
        'pref': 'privacy.clearOnShutdown.cookies',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [False, True],  # Inverted: False = keep (don't clear), True = clear
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,  # Keep cookies
            'paranoid': True,   # Clear cookies
            'open': False       # Keep cookies
        }
    },

    'keep_sessions': {
        'name': 'Keep Session Data on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Preserve open tabs and windows data when Firefox closes.',
        'full': (
            'When enabled, session data (open tabs, windows, scroll positions, form data) is NOT '
            'cleared on shutdown. This is required for session restore to work properly. Disabling '
            'this clears all session information when Firefox closes, providing privacy but losing '
            'your tab state. Works together with "Restore Session" setting to preserve your '
            'browsing state between restarts.'
        ),
        'pref': 'privacy.clearOnShutdown.sessions',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [False, True],  # Inverted: False = keep, True = clear
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,  # Keep sessions
            'paranoid': True,   # Clear sessions
            'open': False       # Keep sessions
        }
    },

    'keep_logins': {
        'name': 'Remember Logins',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Allow Firefox to save and remember website passwords.',
        'full': (
            'When enabled, Firefox offers to save passwords you enter on websites and can auto-fill '
            'them on future visits. Saved passwords are stored encrypted in Firefox profile. This '
            'is convenient but stores sensitive credentials on disk. For maximum security, disable '
            'this and use a dedicated password manager. Firefox passwords can be protected with a '
            'Primary Password for additional security.'
        ),
        'pref': 'signon.rememberSignons',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Remember', 'Never Save'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    'keep_formdata': {
        'name': 'Keep Form Data on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Preserve form autocomplete history when Firefox closes.',
        'full': (
            'When enabled, form data (text entered in search boxes, forms, etc.) is NOT cleared '
            'on shutdown. This enables autocomplete suggestions based on your previous entries. '
            'Convenient for frequently-used forms but stores your input history on disk. For '
            'privacy, disable this to clear all form data when Firefox closes. Note this is '
            'separate from saved passwords which have their own setting.'
        ),
        'pref': 'privacy.clearOnShutdown.formdata',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [False, True],  # Inverted
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': True,
            'open': False
        }
    },

    'keep_history': {
        'name': 'Keep History on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Preserve browsing history when Firefox closes.',
        'full': (
            'When enabled, your browsing history is NOT cleared when Firefox shuts down. History '
            'enables the awesome bar suggestions, recently visited sites, and history search. '
            'For privacy, disable this to clear all browsing history on exit. Note that this '
            'affects the history sidebar and History menu. Consider using Private Browsing mode '
            'for sensitive browsing instead of clearing all history.'
        ),
        'pref': 'privacy.clearOnShutdown.history',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [False, True],  # Inverted
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': True,
            'open': False
        }
    },

    'keep_downloads': {
        'name': 'Keep Download History on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Preserve download history when Firefox closes.',
        'full': (
            'When enabled, the list of downloaded files is NOT cleared when Firefox shuts down. '
            'Download history shows in the Downloads panel and Library. This does not affect the '
            'actual downloaded files, only the record of downloads in Firefox. For privacy, disable '
            'this to clear download history on exit. The downloaded files themselves remain on your '
            'computer regardless of this setting.'
        ),
        'pref': 'privacy.clearOnShutdown.downloads',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [False, True],  # Inverted
        'labels': ['Keep', 'Clear'],
        'default': False,
        'recommended': {
            'balanced': True,   # Clear downloads
            'paranoid': True,   # Clear downloads
            'open': False       # Keep downloads
        }
    },

    'clear_cache': {
        'name': 'Clear Cache on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Delete cached web content when Firefox closes.',
        'full': (
            'When enabled, the browser cache (stored images, scripts, stylesheets) is cleared '
            'when Firefox shuts down. This prevents cached content from revealing your browsing '
            'activity but means websites load slower on the next visit since everything must be '
            'downloaded again. For privacy, enable this. For performance, disable it to keep '
            'cache for faster browsing. Cache can also be cleared manually anytime.'
        ),
        'pref': 'privacy.clearOnShutdown.cache',
        'type': 'toggle',
        'impact': 'medium',
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
        'name': 'Clear Offline Data on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Delete offline website data when Firefox closes.',
        'full': (
            'When enabled, offline website data (data stored by web apps for offline use) is '
            'cleared when Firefox shuts down. This includes data stored by Progressive Web Apps '
            'and websites that cache content for offline access. Clearing this may require '
            'web apps to re-download their data. For privacy, enable this. For convenience with '
            'offline-capable web apps, disable it.'
        ),
        'pref': 'privacy.clearOnShutdown.offlineApps',
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

    'clear_siteprefs': {
        'name': 'Clear Site Preferences on Shutdown',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Reset site-specific permissions when Firefox closes.',
        'full': (
            'When enabled, site-specific preferences (zoom levels, notification permissions, '
            'pop-up exceptions, etc.) are cleared when Firefox shuts down. This resets all '
            'per-site permissions you have granted or denied. For privacy, this prevents sites '
            'from being "remembered." Most users should disable this to keep their permission '
            'choices. Enable only for maximum privacy where you want to re-decide permissions '
            'for every site on each session.'
        ),
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

    # =========================================================================
    # PRIVACY - COOKIES (subcategory: 'cookies')
    # =========================================================================

    'cookie_lifetime': {
        'name': 'Cookie Lifetime',
        'category': 'privacy',
        'subcategory': 'cookies',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Control how long cookies are kept.',
        'full': (
            'Controls the default lifetime policy for cookies. "Normal" keeps cookies until they '
            'expire naturally (set by the website). "Session" deletes all cookies when Firefox '
            'closes, regardless of their expiration date. "Days" lets you set a maximum age for '
            'cookies. Shorter lifetimes improve privacy but require more frequent logins. This '
            'applies to all cookies; use cookie exceptions for sites you want to stay logged into.'
        ),
        'pref': 'network.cookie.lifetimePolicy',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [0, 2, 3],  # 0 = normal, 2 = session, 3 = days
        'labels': ['Normal', 'Session Only', 'Custom Days'],
        'default': 0,
        'recommended': {
            'balanced': 0,
            'paranoid': 2,
            'open': 0
        }
    },

    'cookie_days': {
        'name': 'Cookie Maximum Age',
        'category': 'privacy',
        'subcategory': 'cookies',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Maximum number of days to keep cookies.',
        'full': (
            'When cookie lifetime is set to "Custom Days," this controls the maximum age in days '
            'for cookies. Cookies older than this limit are automatically deleted. Shorter periods '
            'improve privacy by limiting long-term tracking. Longer periods are more convenient '
            'for staying logged in. Common values: 1 day (maximum privacy), 7 days (weekly), '
            '30 days (monthly), 90 days (quarterly), 365 days (yearly).'
        ),
        'pref': 'network.cookie.lifetime.days',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [1, 7, 30, 90, 365],
        'labels': ['1 Day', '7 Days', '30 Days', '90 Days', '365 Days'],
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
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Control cookies from sites other than the one you are visiting.',
        'full': (
            'Third-party cookies are set by domains other than the site you are visiting, typically '
            'used for cross-site tracking by advertisers. "All" allows all third-party cookies '
            '(least private). "Cross-site only" blocks cookies that track across sites. "Visited" '
            'only allows third-party cookies from sites you have directly visited. "None" blocks '
            'all third-party cookies (most private but may break some sites like embedded content).'
        ),
        'pref': 'network.cookie.cookieBehavior',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [0, 4, 3, 1],  # 0=all, 4=cross-site blocked, 3=visited, 1=block all 3rd party
        'labels': ['Allow All', 'Block Cross-Site', 'Visited Sites Only', 'Block All Third-Party'],
        'default': 4,
        'recommended': {
            'balanced': 4,
            'paranoid': 1,
            'open': 0
        }
    },

    # =========================================================================
    # PRIVACY - TRACKING (subcategory: 'tracking')
    # =========================================================================

    'tracking_protection': {
        'name': 'Tracking Protection Level',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Choose the level of tracking protection.',
        'full': (
            'Firefox Enhanced Tracking Protection blocks trackers, cryptominers, and fingerprinters. '
            '"Standard" provides balanced protection that works with most sites. "Strict" blocks '
            'more trackers including all cross-site cookies, which may break some sites. "Custom" '
            'lets you configure individual protections. Strict mode provides better privacy but '
            'may require adding exceptions for sites that break. Start with Strict and add '
            'exceptions as needed.'
        ),
        'pref': 'browser.contentblocking.category',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'moderate',
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
        'name': 'Fingerprint Resistance',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block fingerprinting attempts by websites.',
        'full': (
            'Fingerprinting is a technique to identify you based on your browser configuration, '
            'fonts, screen size, and other characteristics. When enabled, Firefox actively blocks '
            'known fingerprinting scripts. This is included in Strict tracking protection but can '
            'be enabled separately. Some legitimate sites may have reduced functionality. Enable '
            'for enhanced privacy against sophisticated tracking.'
        ),
        'pref': 'privacy.trackingprotection.fingerprinting.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    'cryptomining_block': {
        'name': 'Block Cryptominers',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block cryptocurrency mining scripts.',
        'full': (
            'Cryptomining scripts run in your browser to mine cryptocurrency using your CPU and '
            'electricity without your consent. These scripts slow down your computer, drain battery, '
            'and increase power consumption. Firefox can block known cryptomining scripts. There '
            'is no legitimate reason to allow cryptomining in most cases. Keep this enabled to '
            'protect your resources.'
        ),
        'pref': 'privacy.trackingprotection.cryptomining.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Block', 'Allow'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },

    'fix_major_site_issues': {
        'name': 'Fix Major Site Issues',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Allow exceptions to tracking protection for essential domains that would cause major site breakage.',
        'full': (
            'Helps load sites and features by unblocking only essential elements that may '
            'contain trackers. Covers most common problems like sites that fail to load or '
            'major functionality that is broken. This is the baseline tier of web compatibility '
            'exceptions in Firefox Enhanced Tracking Protection Strict mode. Disable for '
            'maximum tracking protection at the cost of significant site breakage.'
        ),
        'pref': 'privacy.trackingprotection.allow_list.baseline.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'high',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'fix_minor_site_issues': {
        'name': 'Fix Minor Site Issues',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Restore elements like videos or comment sections by allowing exceptions for domains that may include trackers.',
        'full': (
            'Restores things like videos in an article or comment sections by allowing '
            'exceptions for domains that may contain trackers. This can reduce site issues but '
            'offers less protection. Only effective when used together with Fix Major Site '
            'Issues. This is the convenience tier of web compatibility exceptions in Firefox '
            'Enhanced Tracking Protection Strict mode.'
        ),
        'pref': 'privacy.trackingprotection.allow_list.convenience.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_enabled': {
        'name': 'Telemetry',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Send usage data to Mozilla.',
        'full': (
            'When enabled, Firefox collects and sends anonymous usage data to Mozilla to help '
            'improve the browser. This includes performance metrics, feature usage, and crash '
            'information. Mozilla uses this data to identify issues and prioritize improvements. '
            'The data is anonymized and Mozilla has a strong privacy policy. Disable if you prefer '
            'not to share any data, but consider that this data helps improve Firefox for everyone.'
        ),
        'pref': 'toolkit.telemetry.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
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
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Allow Mozilla to run studies in Firefox.',
        'full': (
            'Firefox Studies let Mozilla test new features and changes with a subset of users '
            'before wider release. Studies can modify Firefox behavior temporarily. Mozilla uses '
            'this to gather data on new features and improvements. Studies are opt-in and can be '
            'disabled. Some users prefer to disable studies for maximum control over their browser '
            'behavior, while others enable them to help improve Firefox.'
        ),
        'pref': 'app.shield.optoutstudies.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
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
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Send crash reports to Mozilla.',
        'full': (
            'When Firefox crashes, it can send a report to Mozilla containing technical information '
            'about the crash. This helps Mozilla identify and fix bugs. Crash reports may contain '
            'URLs of open tabs and other browsing information. For privacy, you can disable this. '
            'However, crash reports are valuable for improving Firefox stability. Mozilla handles '
            'crash data according to their privacy policy.'
        ),
        'pref': 'browser.tabs.crashReporting.sendReport',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Send', 'Do Not Send'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'health_report': {
        'name': 'Health Report Upload',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Send health report data to Mozilla.',
        'full': (
            'Controls whether Firefox sends health report data to Mozilla. This includes '
            'information about browser performance, hardware, usage patterns, and customizations. '
            'Mozilla uses this to understand how Firefox performs across different configurations. '
            'Disable for maximum privacy. This is separate from crash reports and telemetry.'
        ),
        'pref': 'datareporting.healthreport.uploadEnabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'data_submission': {
        'name': 'Data Submission Policy',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Allow Firefox to submit data to Mozilla.',
        'full': (
            'Master switch for all data reporting to Mozilla. When disabled, it prevents Firefox '
            'from sending any telemetry, health reports, or usage data to Mozilla. This is the '
            'most effective single toggle to stop all data collection. Disable for complete '
            'data privacy from Mozilla.'
        ),
        'pref': 'datareporting.policy.dataSubmissionEnabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'normandy_enabled': {
        'name': 'Normandy / Remote Settings',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow Mozilla to remotely modify Firefox settings and run experiments.',
        'full': (
            'Normandy (also known as Shield) allows Mozilla to push remote changes to Firefox, '
            'including A/B experiments, feature rollouts, and hotfixes. When enabled, Mozilla can '
            'modify browser behavior between updates. This is used for studies, Pocket integration, '
            'and gradual feature rollouts. Disable for full control over your browser configuration. '
            'Note: disabling may delay receiving some security hotfixes.'
        ),
        'pref': 'app.normandy.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'ping_centre': {
        'name': 'Ping Centre Telemetry',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send daily usage pings to Mozilla.',
        'full': (
            'Ping Centre sends structured telemetry pings to Mozilla servers including daily '
            'active usage data, new tab interactions, and other usage metrics. This helps Mozilla '
            'estimate active users and measure feature engagement. Disable to prevent sending '
            'these usage pings.'
        ),
        'pref': 'browser.ping-centre.telemetry',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'extension_recommendations': {
        'name': 'Extension Recommendations',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Show personalized extension recommendations.',
        'full': (
            'When enabled, Firefox sends browsing data to Mozilla to receive personalized '
            'extension recommendations. This requires sharing information about your browsing '
            'habits. Disable to prevent Firefox from collecting this data and showing extension '
            'suggestions based on your activity.'
        ),
        'pref': 'browser.discovery.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'autofill_addresses': {
        'name': 'Autofill Addresses',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Save and autofill postal addresses in forms.',
        'full': (
            'When enabled, Firefox saves postal addresses you enter in web forms and can '
            'automatically fill them in on future visits. This stores personal information '
            'including your name, street address, city, and postal code on disk. Convenient '
            'for frequent online shopping but stores sensitive personal data. Disable if you '
            'prefer not to have your address information stored in the browser.'
        ),
        'pref': 'extensions.formautofill.addresses.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'autofill_creditcards': {
        'name': 'Autofill Credit Cards',
        'category': 'privacy',
        'subcategory': 'data',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Save and autofill credit card information in forms.',
        'full': (
            'When enabled, Firefox can save and autofill credit card numbers, expiration dates, '
            'and cardholder names. Card data is stored encrypted on disk. While convenient for '
            'online shopping, storing payment information in the browser carries security risks. '
            'Consider using a dedicated password manager for payment information instead. '
            'Disable for maximum financial security.'
        ),
        'pref': 'extensions.formautofill.creditCards.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': False
        }
    },

    # =========================================================================
    # SECURITY - NETWORK (subcategory: 'network')
    # =========================================================================

    'dns_over_https': {
        'name': 'DNS over HTTPS',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Encrypt DNS queries for privacy and security.',
        'full': (
            'DNS over HTTPS (DoH) encrypts your DNS queries, preventing your ISP or network from '
            'seeing what websites you visit. "Off" disables DoH entirely. "Increased Protection" '
            'uses DoH when available but falls back to regular DNS if needed. "Max Protection" '
            'enforces DoH-only and blocks connections if DoH is unavailable. "Explicitly Off" '
            'prevents Firefox from auto-enabling DoH. Increased or Max protection is recommended '
            'for privacy. Choose a trusted DoH provider.'
        ),
        'pref': 'network.trr.mode',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [0, 2, 3, 5],  # 0=off, 2=increased, 3=max, 5=explicitly off
        'labels': ['Off', 'Increased Protection', 'Max Protection', 'Explicitly Off'],
        'default': 2,
        'recommended': {
            'max_power': 0,      # Performance - DoH disabled
            'balanced': 2,       # Privacy with fallback
            'battery': 2,        # Reasonable privacy
            'paranoid': 3,       # Maximum privacy
            'open': 0            # No restrictions
        }
    },

    'dns_provider': {
        'name': 'DoH Provider',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Choose your DNS over HTTPS provider.',
        'full': (
            'Select which DNS provider to use for encrypted DNS queries. '
            'Cloudflare (1.1.1.1): Fast, privacy-focused, global network. '
            'Quad9 (9.9.9.9): Blocks malicious domains, nonprofit, no logging. '
            'NextDNS: Customizable filtering and analytics. '
            'Google (8.8.8.8): Fast, reliable, but Google privacy policy applies. '
            'AdGuard: Blocks ads/trackers at DNS level, privacy-focused. '
            'Mullvad: Run by VPN provider, no logging, privacy-first. '
            'OpenDNS/Cisco: Enterprise-grade, content filtering options. '
            'Control D: Privacy-focused, customizable blocking. '
            'Each provider has different privacy policies and features. Research providers to '
            'choose one that aligns with your privacy needs.'
        ),
        'pref': 'network.trr.uri',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [
            'https://mozilla.cloudflare-dns.com/dns-query',
            'https://dns.quad9.net/dns-query',
            'https://firefox.dns.nextdns.io/',
            'https://dns.google/dns-query',
            'https://dns.adguard-dns.com/dns-query',
            'https://doh.mullvad.net/dns-query',
            'https://doh.opendns.com/dns-query',
            'https://freedns.controld.com/p0'
        ],
        'labels': [
            'Cloudflare (1.1.1.1)',
            'Quad9 (9.9.9.9)',
            'NextDNS',
            'Google (8.8.8.8)',
            'AdGuard DNS',
            'Mullvad DNS',
            'OpenDNS (Cisco)',
            'Control D'
        ],
        'default': 'https://dns.quad9.net/dns-query',
        'recommended': {
            'max_power': 'https://mozilla.cloudflare-dns.com/dns-query',  # Fastest
            'balanced': 'https://dns.quad9.net/dns-query',               # Security + privacy
            'battery': 'https://mozilla.cloudflare-dns.com/dns-query',   # Fast, low overhead
            'paranoid': 'https://doh.mullvad.net/dns-query',             # No logging, privacy-first VPN provider
            'open': 'https://mozilla.cloudflare-dns.com/dns-query'       # Fast, reliable
        }
    },

    'dns_disable_ecs': {
        'name': 'Disable EDNS Client Subnet (ECS)',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Prevent partial IP address from being sent to DNS servers.',
        'full': (
            'EDNS Client Subnet (ECS) sends part of your IP address to DNS servers to enable '
            'geo-located responses. While this can improve CDN performance, it reduces privacy by '
            'revealing your approximate location to DNS providers and authoritative nameservers. '
            'Disabling ECS improves privacy but may result in slightly slower CDN performance for '
            'some websites. Recommended for privacy-conscious users.'
        ),
        'pref': 'network.trr.disable-ECS',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['ECS Off (More Private)', 'ECS On (Faster CDN)'],
        'default': True,
        'recommended': {
            'max_power': False,  # Faster CDN
            'balanced': True,    # Privacy
            'battery': True,     # Privacy
            'paranoid': True,    # Maximum privacy
            'open': False        # Performance
        }
    },

    'dns_fallback_behavior': {
        'name': 'DoH Fallback to Native DNS',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow fallback to system DNS when DoH fails.',
        'full': (
            'Controls how aggressively Firefox falls back to system DNS when the DoH provider '
            'encounters issues. "Allow Fallback" permits fallback on any TRR failure or timeout, '
            'maintaining connectivity but potentially exposing DNS queries. "Block Fallback" '
            'restricts fallback to only critical cases (provider confirmed down, connection '
            'failures after TRR resolution, or NXDOMAIN), keeping most DNS queries encrypted '
            'while maintaining basic connectivity. Only relevant when DoH mode is "Increased Protection".'
        ),
        'pref': 'network.trr.strict_native_fallback',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'major',
        'values': [False, True],  # Inverted: False = allows fallback
        'labels': ['Allow Fallback (Reliable)', 'Block Fallback (Private)'],
        'default': False,
        'recommended': {
            'max_power': False,  # Allow fallback
            'balanced': False,   # Allow fallback
            'battery': False,    # Allow fallback
            'paranoid': True,    # Block fallback for privacy
            'open': False        # Allow fallback
        }
    },

    'dns_captive_portal': {
        'name': 'Wait for Captive Portal Detection',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Delay DoH until captive portal login completes.',
        'full': (
            'On public WiFi networks with login pages (captive portals), Firefox waits for you '
            'to complete login before enabling DoH. This prevents DoH from breaking the login '
            'process. "Wait for Login" ensures captive portals work smoothly. "Force DoH Immediately" '
            'enables DoH right away, which may prevent captive portal login. WARNING: Disabling '
            'this will make hotel/airport WiFi logins fail. Only disable if you never use public '
            'WiFi with login pages.'
        ),
        'pref': 'network.trr.wait-for-portal',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Wait for Login (Compatible)', 'Force DoH Immediately'],
        'default': True,
        'recommended': {
            'max_power': True,   # Compatibility
            'balanced': True,    # Compatibility
            'battery': True,     # Compatibility
            'paranoid': True,    # Even paranoid users need captive portals
            'open': True         # Compatibility
        }
    },

    'https_only': {
        'name': 'HTTPS-Only Mode',
        'category': 'security',
        'subcategory': 'network',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Force all connections to use HTTPS.',
        'full': (
            'HTTPS-Only Mode upgrades all connections to HTTPS and warns before loading sites '
            'over unencrypted HTTP. This protects against eavesdropping and man-in-the-middle '
            'attacks. Most modern websites support HTTPS. When a site does not support HTTPS, '
            'Firefox shows a warning and lets you proceed if you choose. Highly recommended for '
            'security. Rare sites without HTTPS can be exempted individually.'
        ),
        'pref': 'dom.security.https_only_mode',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    'https_only_pbm': {
        'name': 'HTTPS-Only in Private Browsing',
        'category': 'security',
        'subcategory': 'network',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Force HTTPS in private browsing mode.',
        'full': (
            'Enables HTTPS-Only Mode specifically for Private Browsing windows. Even if HTTPS-Only '
            'is disabled for normal browsing, this ensures private browsing sessions always use '
            'encrypted connections. Private browsing is often used for sensitive activities where '
            'encryption is especially important. Enable this for enhanced privacy in private '
            'browsing mode.'
        ),
        'pref': 'dom.security.https_only_mode_pbm',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },

    'mixed_content_block': {
        'name': 'Block Mixed Content',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block insecure content on HTTPS pages.',
        'full': (
            'Mixed content occurs when an HTTPS page loads resources (scripts, images, etc.) over '
            'insecure HTTP. This can compromise the security of the entire page. When enabled, '
            'Firefox blocks active mixed content (scripts, iframes) that could be exploited. This '
            'protects against attacks where an attacker injects malicious content into an otherwise '
            'secure page. Keep enabled for security.'
        ),
        'pref': 'security.mixed_content.block_active_content',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Block', 'Allow'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': True
        }
    },

    'webrtc_enabled': {
        'name': 'WebRTC',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enable WebRTC for video calls and P2P communication.',
        'full': (
            'WebRTC (Web Real-Time Communication) enables video calling, voice chat, and peer-to-peer '
            'file sharing directly in the browser. Used by Google Meet, Discord, Zoom web client, '
            'and many other services. Disabling WebRTC breaks these services but prevents potential '
            'IP address leaks. For VPN users concerned about IP leaks, consider disabling or using '
            'the IP leak prevention setting instead of completely disabling WebRTC.'
        ),
        'pref': 'media.peerconnection.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    'webrtc_ip_leak': {
        'name': 'WebRTC IP Leak Prevention',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Prevent WebRTC from leaking your real IP address.',
        'full': (
            'WebRTC can reveal your real IP address even when using a VPN, through ICE candidate '
            'gathering. When enabled, this setting limits WebRTC to only use the default network '
            'interface, preventing it from discovering and leaking your real IP through alternative '
            'interfaces. This is essential for VPN users who want to prevent IP leaks while still '
            'using WebRTC services. Enable if you use a VPN.'
        ),
        'pref': 'media.peerconnection.ice.default_address_only',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Prevent Leaks', 'Allow All'],
        'default': False,
        'recommended': {
            'balanced': True,
            'paranoid': True,
            'open': False
        }
    },

    'prefetch_dns': {
        'name': 'DNS Prefetching',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Pre-resolve DNS for links on the page.',
        'full': (
            'DNS prefetching resolves domain names for links on a page before you click them, '
            'reducing latency when you do navigate. However, this leaks information about your '
            'browsing to DNS servers (you are looking at pages containing these links). For '
            'privacy, disable DNS prefetching. For performance, enable it. Note: This pref is '
            'inverted - True disables prefetching, False enables it.'
        ),
        'pref': 'network.dns.disablePrefetch',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],  # Inverted: True = disabled (more private)
        'labels': ['Disabled', 'Enabled'],
        'default': True,
        'recommended': {
            'balanced': True,   # Disabled
            'paranoid': True,   # Disabled
            'open': False       # Enabled
        }
    },

    'prefetch_links': {
        'name': 'Link Prefetching',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Pre-load linked pages in the background.',
        'full': (
            'Link prefetching loads pages that you might navigate to in the background, making '
            'them appear to load instantly when clicked. Sites can hint which links to prefetch. '
            'This uses bandwidth and leaks browsing information since you fetch pages you may '
            'never visit. For privacy and bandwidth savings, disable this. For perceived speed '
            'on well-designed sites, enable it.'
        ),
        'pref': 'network.prefetch-next',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'predictor': {
        'name': 'Network Predictor',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Predict and pre-connect to sites you might visit.',
        'full': (
            'The network predictor learns your browsing patterns and pre-connects to sites it '
            'predicts you will visit, reducing connection time. It also pre-resolves DNS and '
            'pre-opens connections for links you hover over. This improves perceived performance '
            'but leaks browsing behavior information. For privacy, disable the predictor. For '
            'speed, enable it.'
        ),
        'pref': 'network.predictor.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    # =========================================================================
    # SECURITY - PERMISSIONS (subcategory: 'permissions')
    # =========================================================================

    'location_permission': {
        'name': 'Location Permission',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Default permission for location access.',
        'full': (
            'Controls the default behavior when websites request your location. "Allow" grants '
            'location access to all sites without asking. "Ask" prompts you each time a site '
            'requests location (recommended). "Block" denies all location requests. Location '
            'data can reveal your home, work, and frequently visited places. Most users should '
            'use "Ask" to decide per-site. Block if you never want to share location.'
        ),
        'pref': 'geo.enabled',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, True, False],  # For allow/ask, geo must be enabled. For block, disabled.
        'labels': ['Allow', 'Ask', 'Block'],
        'default': True,  # geo.enabled = True, then per-site permission Ask is default
        'recommended': {
            'balanced': True,   # Enabled (Ask per site)
            'paranoid': False,  # Disabled (Block all)
            'open': True        # Enabled
        }
    },

    'camera_permission': {
        'name': 'Camera Permission',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Default permission for camera access.',
        'full': (
            'Controls the default behavior when websites request camera access. "Allow" grants '
            'camera to all sites (dangerous). "Ask" prompts you each time (recommended). "Block" '
            'denies all camera requests. Camera access is needed for video calls and some web apps. '
            'Always use "Ask" or "Block" - never "Allow" to prevent unauthorized camera access.'
        ),
        'pref': 'permissions.default.camera',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [1, 0, 2],  # 0=allow, 1=ask, 2=block
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 0,  # Ask
        'recommended': {
            'balanced': 0,   # Ask
            'paranoid': 2,   # Block
            'open': 0        # Ask
        }
    },

    'microphone_permission': {
        'name': 'Microphone Permission',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Default permission for microphone access.',
        'full': (
            'Controls the default behavior when websites request microphone access. "Allow" grants '
            'microphone to all sites (dangerous). "Ask" prompts you each time (recommended). "Block" '
            'denies all microphone requests. Microphone is needed for voice calls, voice search, '
            'and some web apps. Use "Ask" to decide per-site or "Block" for maximum privacy.'
        ),
        'pref': 'permissions.default.microphone',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [1, 0, 2],  # 0=allow, 1=ask, 2=block
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 0,  # Ask
        'recommended': {
            'balanced': 0,   # Ask
            'paranoid': 2,   # Block
            'open': 0        # Ask
        }
    },

    'notifications_permission': {
        'name': 'Notifications Permission',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Default permission for desktop notifications.',
        'full': (
            'Controls whether websites can send desktop notifications. "Allow" enables notifications '
            'from all sites (spammy). "Ask" prompts you each time (default). "Block" denies all '
            'notification requests. Many sites abuse notifications for marketing. Consider "Block" '
            'to prevent notification spam, or "Ask" if you use web apps that need notifications '
            'like email or messaging.'
        ),
        'pref': 'permissions.default.desktop-notification',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [1, 0, 2],  # 0=allow, 1=ask, 2=block
        'labels': ['Allow', 'Ask', 'Block'],
        'default': 0,  # Ask
        'recommended': {
            'balanced': 2,   # Block
            'paranoid': 2,   # Block
            'open': 0        # Ask
        }
    },

    'autoplay_permission': {
        'name': 'Autoplay Permission',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Control automatic video and audio playback.',
        'full': (
            'Controls whether websites can automatically play audio and video content. "Allow" '
            'permits autoplay (can be annoying). "Block" prevents all autoplay, requiring you '
            'to click play. Blocking autoplay saves bandwidth, prevents surprise sounds, and '
            'improves page load times. Some sites with legitimate video content may require '
            'you to click play. Most users prefer blocking autoplay.'
        ),
        'pref': 'media.autoplay.default',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [0, 1],  # 0=allow, 1=block
        'labels': ['Allow', 'Block'],
        'default': 1,
        'recommended': {
            'balanced': 1,   # Block
            'paranoid': 1,   # Block
            'open': 0        # Allow
        }
    },

    'search_suggestions': {
        'name': 'Search Suggestions',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Show search suggestions as you type.',
        'full': (
            'When enabled, Firefox sends your keystrokes to your search engine as you type, '
            'showing suggestions before you press Enter. This is convenient but sends everything '
            'you type in the address bar to your search engine, even if you do not search. For '
            'privacy, disable this to only send searches when you explicitly submit them. Affects '
            'what data your search engine collects about your browsing.'
        ),
        'pref': 'browser.search.suggest.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'url_suggestions': {
        'name': 'URL Bar Suggestions',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Suggest URLs from history in the address bar.',
        'full': (
            'When enabled, the address bar suggests URLs from your browsing history as you type. '
            'This makes it easy to revisit sites but exposes your browsing history in suggestions. '
            'This data stays local and is not sent anywhere. For convenience, keep enabled. For '
            'privacy (especially on shared computers), disable to prevent history appearing in '
            'the address bar dropdown.'
        ),
        'pref': 'browser.urlbar.suggest.history',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    'autofill_forms': {
        'name': 'Autofill Forms',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Automatically fill in form fields.',
        'full': (
            'When enabled, Firefox can automatically fill in form fields based on your previous '
            'entries. This includes names, addresses, and other commonly-entered information. '
            'Convenient but stores form data that could reveal personal information if someone '
            'accesses your browser. Consider whether the convenience outweighs the privacy risk '
            'on your system.'
        ),
        'pref': 'browser.formfill.enable',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'balanced': False,
            'paranoid': False,
            'open': True
        }
    },

    'autofill_passwords': {
        'name': 'Autofill Passwords',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Automatically fill in saved passwords.',
        'full': (
            'When enabled and you have saved passwords, Firefox automatically fills them into '
            'login forms. This is convenient but means anyone with access to your browser can '
            'log into your accounts. For security on shared computers, disable this to require '
            'manual password selection. Consider using a Primary Password to protect saved logins.'
        ),
        'pref': 'signon.autofillForms',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'balanced': True,
            'paranoid': False,
            'open': True
        }
    },

    # =========================================================================
    # PRIVACY - TRACKING: Enhanced Tracking & Fingerprinting
    # =========================================================================

    'tracking_protection_enabled': {
        'name': 'Enhanced Tracking Protection',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Enable Enhanced Tracking Protection to block known trackers.',
        'full': (
            'Master switch for Firefox Enhanced Tracking Protection. When enabled, Firefox '
            'blocks known trackers from tracking your activity across websites. This works with '
            'the Tracking Protection Level setting to determine which trackers to block. '
            'Disabling this removes all ETP protections. Keep enabled for basic privacy protection.'
        ),
        'pref': 'privacy.trackingprotection.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'resist_fingerprinting': {
        'name': 'Resist Fingerprinting (RFP)',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Spoof browser properties to resist fingerprinting.',
        'full': (
            'Resist Fingerprinting (RFP) makes Firefox actively lie about many browser properties '
            'to prevent fingerprinting. It spoofs timezone to UTC, rounds window dimensions, '
            'reports a generic user agent, disables font enumeration, and normalizes many APIs. '
            'This is the most powerful anti-fingerprinting measure but causes significant site '
            'breakage: timezone-dependent sites break, video may be limited to 30fps, and some '
            'sites may look different. Inspired by Tor Browser settings.'
        ),
        'pref': 'privacy.resistFingerprinting',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'first_party_isolate': {
        'name': 'First-Party Isolation (FPI)',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Isolate all browser data per first-party domain.',
        'full': (
            'First-Party Isolation (FPI) restricts cookies, cache, and other browser state to '
            'the first-party domain. This prevents trackers embedded on multiple sites from '
            'correlating your activity. For example, a Facebook Like button on different sites '
            'cannot share cookies to track you. This is very effective against cross-site '
            'tracking but breaks some SSO logins, embedded content, and payment flows. '
            'WARNING: Firefox 86+ uses Dynamic FPI (dFPI) via Enhanced Tracking Protection. '
            'Enabling legacy FPI alongside dFPI can cause double-isolation issues. Prefer using '
            'Tracking Protection Level "Strict" mode instead, which enables dFPI automatically.'
        ),
        'pref': 'privacy.firstparty.isolate',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'social_tracking_block': {
        'name': 'Block Social Trackers',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block tracking by social media platforms.',
        'full': (
            'Blocks social media trackers (Facebook, Twitter, LinkedIn, etc.) that are embedded '
            'on third-party websites. Social media companies use these trackers (like/share '
            'buttons, pixels, SDKs) to track your browsing activity across the web. Blocking '
            'these prevents social media from building a profile of your browsing. Some embedded '
            'social features (comments, sharing) may break.'
        ),
        'pref': 'privacy.trackingprotection.socialtracking.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Block', 'Allow'],
        'default': True,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': False
        }
    },

    'do_not_track': {
        'name': 'Do Not Track Header',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Send a Do Not Track request to websites.',
        'full': (
            'Sends a DNT (Do Not Track) header with every request, asking websites not to track '
            'you. Most websites ignore this header, and it can actually make you more fingerprintable '
            'since few users enable it. Some privacy advocates recommend disabling it because '
            'it provides no real protection while adding to your fingerprint. The Global Privacy '
            'Control (GPC) header is a more effective alternative.'
        ),
        'pref': 'privacy.donottrackheader.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Send', 'Do Not Send'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    # =========================================================================
    # PRIVACY - TRACKING: Additional Telemetry Controls
    # =========================================================================

    'telemetry_unified': {
        'name': 'Unified Telemetry',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Master switch for the unified telemetry system.',
        'full': (
            'Controls the unified telemetry framework that collects and sends all types of '
            'telemetry data. When disabled, it prevents the collection of most telemetry data '
            'at the source. This is more thorough than disabling individual telemetry toggles. '
            'Disable for maximum privacy from Mozilla data collection.'
        ),
        'pref': 'toolkit.telemetry.unified',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_archive': {
        'name': 'Telemetry Archive',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Store telemetry data locally before sending.',
        'full': (
            'When enabled, Firefox stores telemetry pings locally in an archive before sending '
            'them to Mozilla. Disabling prevents telemetry data from being stored on disk. '
            'This reduces disk usage and prevents telemetry data from persisting on your system.'
        ),
        'pref': 'toolkit.telemetry.archive.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_new_profile_ping': {
        'name': 'New Profile Ping',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send ping when a new profile is created.',
        'full': (
            'Firefox sends a telemetry ping to Mozilla when a new browser profile is created. '
            'This helps Mozilla track new installations and profile creation patterns. Disable '
            'to prevent Mozilla from being notified when you create new profiles.'
        ),
        'pref': 'toolkit.telemetry.newProfilePing.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_shutdown_ping': {
        'name': 'Shutdown Ping Sender',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send telemetry data when Firefox shuts down.',
        'full': (
            'When enabled, Firefox sends pending telemetry pings during shutdown. This ensures '
            'telemetry data collected during the session reaches Mozilla even if Firefox would '
            'not be opened again soon. Disable to prevent telemetry from being sent at shutdown.'
        ),
        'pref': 'toolkit.telemetry.shutdownPingSender.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_update_ping': {
        'name': 'Update Ping',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send telemetry when Firefox updates.',
        'full': (
            'Firefox sends a telemetry ping to Mozilla when the browser is updated. This helps '
            'Mozilla track update adoption rates and identify update issues. Disable to prevent '
            'update notifications from being sent to Mozilla.'
        ),
        'pref': 'toolkit.telemetry.updatePing.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_bhr_ping': {
        'name': 'Background Hang Reporter',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Report browser hangs to Mozilla.',
        'full': (
            'The Background Hang Reporter (BHR) detects when Firefox hangs or becomes '
            'unresponsive and sends reports to Mozilla. This helps identify performance issues. '
            'Disable if you prefer not to send hang reports. This data helps Mozilla fix '
            'performance regressions but involves sending diagnostic data.'
        ),
        'pref': 'toolkit.telemetry.bhrPing.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'telemetry_first_shutdown_ping': {
        'name': 'First Shutdown Ping',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send telemetry on first browser shutdown.',
        'full': (
            'Sends a special telemetry ping the first time Firefox is shut down after installation '
            'or profile creation. This provides Mozilla with initial usage data. Disable to '
            'prevent this first-run telemetry from being sent.'
        ),
        'pref': 'toolkit.telemetry.firstShutdownPing.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'coverage_opt_out': {
        'name': 'Coverage Opt-Out',
        'category': 'privacy',
        'subcategory': 'tracking',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Opt out of Mozilla coverage measurement.',
        'full': (
            'Mozilla uses coverage pings to estimate the number of active Firefox users. '
            'This setting opts out of coverage measurement. When enabled (opted out), Firefox '
            'does not send coverage pings. This is separate from regular telemetry and is used '
            'purely for user counting purposes.'
        ),
        'pref': 'toolkit.coverage.opt-out',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Opt Out', 'Participate'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': False
        }
    },

    # =========================================================================
    # SECURITY - NETWORK: TLS, Certificates & Safe Browsing
    # =========================================================================

    'mixed_content_block_display': {
        'name': 'Block Passive Mixed Content',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block insecure images and media on HTTPS pages.',
        'full': (
            'Blocks passive mixed content like images, audio, and video loaded over HTTP on '
            'HTTPS pages. While less dangerous than active mixed content (scripts), passive '
            'mixed content can still reveal browsing information and be tampered with. Enabling '
            'this may break some older sites that serve images over HTTP. Most modern sites '
            'serve all content over HTTPS.'
        ),
        'pref': 'security.mixed_content.block_display_content',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Block', 'Allow'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'tls_min_version': {
        'name': 'Minimum TLS Version',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Set minimum required TLS protocol version.',
        'full': (
            'Sets the minimum TLS version Firefox will accept for HTTPS connections. TLS 1.2 '
            'is the recommended minimum as older versions have known vulnerabilities. TLS 1.3 '
            'is the most secure but some older servers only support TLS 1.2. Setting to TLS 1.3 '
            'only may break connections to older websites and services. TLS 1.0 and 1.1 are '
            'deprecated and should never be used.'
        ),
        'pref': 'security.tls.version.min',
        'type': 'choice',
        'impact': 'high',
        'compatibility': 'minor',
        'values': [3, 4],  # 3 = TLS 1.2, 4 = TLS 1.3
        'labels': ['TLS 1.2 (Recommended)', 'TLS 1.3 Only'],
        'default': 3,
        'recommended': {
            'max_power': 3,
            'balanced': 3,
            'battery': 3,
            'paranoid': 3,
            'open': 3
        }
    },

    'ssl_safe_negotiation': {
        'name': 'Require Safe SSL Negotiation',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Require RFC 5746 safe renegotiation for TLS connections.',
        'full': (
            'Requires servers to support RFC 5746 safe renegotiation, which prevents a class '
            'of man-in-the-middle attacks during TLS renegotiation. Most modern servers support '
            'this. Enabling may break connections to very old or misconfigured servers. This is '
            'a low-risk security improvement that protects against a specific attack vector.'
        ),
        'pref': 'security.ssl.require_safe_negotiation',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Required', 'Optional'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'ssl_unsafe_negotiation_warning': {
        'name': 'Warn on Unsafe SSL Negotiation',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Show warning indicator for connections without safe negotiation.',
        'full': (
            'Shows a broken lock icon for HTTPS connections that do not support RFC 5746 safe '
            'renegotiation. This visually warns you when a connection might be vulnerable to '
            'renegotiation attacks. Useful for identifying servers with weak TLS configurations.'
        ),
        'pref': 'security.ssl.treat_unsafe_negotiation_as_broken',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show Warning', 'Hide Warning'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'ocsp_enabled': {
        'name': 'OCSP Certificate Checking',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Check if TLS certificates have been revoked.',
        'full': (
            'OCSP (Online Certificate Status Protocol) checks whether a website certificate '
            'has been revoked by its issuer. This protects against compromised certificates. '
            '"Disabled" skips checks (fast but less secure). "Enabled" checks when possible '
            'but allows connection if check fails. Checking adds slight latency to new '
            'connections but significantly improves security.'
        ),
        'pref': 'security.OCSP.enabled',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [0, 1],
        'labels': ['Disabled', 'Enabled'],
        'default': 1,
        'recommended': {
            'max_power': 1,
            'balanced': 1,
            'battery': 1,
            'paranoid': 1,
            'open': 1
        }
    },

    'ocsp_require': {
        'name': 'Require OCSP Response',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block connections when OCSP check fails.',
        'full': (
            'When enabled (hard-fail), Firefox blocks connections if it cannot verify the '
            'certificate status via OCSP. This is more secure but may prevent access to sites '
            'when OCSP servers are temporarily unavailable. When disabled (soft-fail), Firefox '
            'allows the connection even if OCSP check fails. Hard-fail provides better security '
            'but may cause intermittent access issues.'
        ),
        'pref': 'security.OCSP.require',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Hard-Fail (Strict)', 'Soft-Fail (Lenient)'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'cert_pinning': {
        'name': 'Certificate Pinning',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Enforce certificate pinning for known sites.',
        'full': (
            'Certificate pinning ensures that connections to specific high-value sites (like '
            'Google, Mozilla, Twitter) only accept certificates from expected Certificate '
            'Authorities. This prevents attacks using rogue certificates. Level 0 disables '
            'pinning. Level 1 allows user-added CAs to override pins (for corporate proxies). '
            'Level 2 enforces strict pinning (may break corporate SSL inspection).'
        ),
        'pref': 'security.cert_pinning.enforcement_level',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [0, 1, 2],
        'labels': ['Disabled', 'Allow Exceptions', 'Strict'],
        'default': 1,
        'recommended': {
            'max_power': 1,
            'balanced': 1,
            'battery': 1,
            'paranoid': 2,
            'open': 1
        }
    },

    'sha1_enforcement': {
        'name': 'SHA-1 Certificate Enforcement',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Reject certificates signed with weak SHA-1 algorithm.',
        'full': (
            'SHA-1 is a cryptographically broken hash algorithm. Certificates signed with SHA-1 '
            'are vulnerable to collision attacks. Most Certificate Authorities stopped issuing '
            'SHA-1 certificates in 2016. Level 0 allows all SHA-1 certs. Level 1 blocks SHA-1 '
            'for public CAs only. Level 2 blocks all SHA-1 certs. Level 4 blocks SHA-1 '
            'everywhere including local CAs. Use level 1+ for security.'
        ),
        'pref': 'security.pki.sha1_enforcement_level',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [0, 1, 2, 4],
        'labels': ['Allow All', 'Block Public CA', 'Block All', 'Block Everywhere'],
        'default': 1,
        'recommended': {
            'max_power': 1,
            'balanced': 1,
            'battery': 1,
            'paranoid': 2,
            'open': 1
        }
    },

    'safe_browsing_malware': {
        'name': 'Safe Browsing: Malware',
        'category': 'security',
        'subcategory': 'network',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Block known malware sites using Google Safe Browsing.',
        'full': (
            'Uses Google Safe Browsing to warn you when you visit sites known to distribute '
            'malware. Firefox checks URLs against a locally stored list (updated periodically). '
            'No browsing data is sent to Google for this check. This provides important security '
            'against malware infections. Disabling removes this protection layer. Keep enabled '
            'unless you have a specific reason to disable it.'
        ),
        'pref': 'browser.safebrowsing.malware.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'safe_browsing_phishing': {
        'name': 'Safe Browsing: Phishing',
        'category': 'security',
        'subcategory': 'network',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Warn about deceptive phishing sites.',
        'full': (
            'Uses Google Safe Browsing to warn you about deceptive sites that try to steal '
            'credentials or personal information. Firefox checks against a locally stored list. '
            'This is one of the most effective protections against phishing attacks. Keep enabled '
            'to be warned when you encounter known phishing sites.'
        ),
        'pref': 'browser.safebrowsing.phishing.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'safe_browsing_downloads': {
        'name': 'Safe Browsing: Downloads',
        'category': 'security',
        'subcategory': 'network',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Scan downloads for known malware.',
        'full': (
            'Checks downloaded files against a list of known malware. This provides an extra '
            'layer of protection against downloading malicious software. The check uses a locally '
            'stored blocklist. This is separate from the remote download checking feature. '
            'Keep enabled to be warned about known malicious downloads.'
        ),
        'pref': 'browser.safebrowsing.downloads.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    'safe_browsing_downloads_remote': {
        'name': 'Remote Download Scanning',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Send download metadata to Google for advanced malware checking.',
        'full': (
            'When enabled, Firefox sends metadata about downloaded files (hash, size, source URL) '
            'to Google for analysis against a broader database of known malware. This provides '
            'better protection but sends download information to Google. Privacy-conscious users '
            'may want to disable this while keeping local download scanning enabled.'
        ),
        'pref': 'browser.safebrowsing.downloads.remote.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    # =========================================================================
    # SECURITY - NETWORK: Referrer & Link Tracking
    # =========================================================================

    'referer_cross_origin_policy': {
        'name': 'Cross-Origin Referrer Policy',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Control what referrer information is sent to other sites.',
        'full': (
            'Controls when Firefox sends the Referer header for cross-origin requests. '
            '0 = Always send full referrer. '
            '1 = Send referrer only for same base domain (e.g., sub.example.com to example.com). '
            '2 = Send referrer only for exact same host. '
            'Restricting cross-origin referrers prevents sites from knowing which page you came '
            'from, improving privacy. Setting to 1 is a good balance of privacy and compatibility.'
        ),
        'pref': 'network.http.referer.XOriginPolicy',
        'type': 'choice',
        'impact': 'medium',
        'compatibility': 'minor',
        'values': [0, 1, 2],
        'labels': ['Always Send', 'Same Base Domain Only', 'Same Host Only'],
        'default': 0,
        'recommended': {
            'max_power': 0,
            'balanced': 1,
            'battery': 0,
            'paranoid': 2,
            'open': 0
        }
    },

    'referer_cross_origin_trimming': {
        'name': 'Cross-Origin Referrer Trimming',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Control how much referrer information is sent cross-origin.',
        'full': (
            'Controls how much of the URL is included in the Referer header for cross-origin '
            'requests. 0 = Send full URL (e.g., https://site.com/page?query). 1 = Send URL '
            'without query string. 2 = Send only the origin (https://site.com/). Trimming '
            'reduces information leakage while maintaining basic referrer functionality.'
        ),
        'pref': 'network.http.referer.XOriginTrimmingPolicy',
        'type': 'choice',
        'impact': 'low',
        'compatibility': 'none',
        'values': [0, 1, 2],
        'labels': ['Full URL', 'No Query String', 'Origin Only'],
        'default': 0,
        'recommended': {
            'max_power': 0,
            'balanced': 2,
            'battery': 0,
            'paranoid': 2,
            'open': 0
        }
    },

    'send_pings': {
        'name': 'Hyperlink Auditing Pings',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow tracking pings when clicking links.',
        'full': (
            'Hyperlink auditing allows websites to track which links you click by sending a '
            'ping (HTTP request) to a specified URL when you click a link. This is used for '
            'click tracking and analytics. Disabling prevents websites from being notified '
            'when you click their tracked links. This has no impact on normal browsing.'
        ),
        'pref': 'browser.send_pings',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Allow', 'Block'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    },

    'speculative_connect_urlbar': {
        'name': 'URL Bar Speculative Connections',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Pre-connect to URLs as you type in the address bar.',
        'full': (
            'Firefox opens speculative connections to URLs as you type them in the address bar, '
            'before you press Enter. This reduces perceived latency but leaks information about '
            'what you are typing to the destination server before you decide to visit. Disable '
            'for privacy to prevent premature connections.'
        ),
        'pref': 'browser.urlbar.speculativeConnect.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'punycode_display': {
        'name': 'Show Punycode for IDN Domains',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Show punycode instead of Unicode in domain names to prevent phishing.',
        'full': (
            'Internationalized Domain Names (IDN) can contain Unicode characters that look '
            'identical to ASCII characters (homograph attacks). For example, "аpple.com" using '
            'Cyrillic "а" looks like "apple.com". Showing punycode (xn--...) instead reveals '
            'the real domain and prevents these phishing attacks. Enable for security, especially '
            'if you visit sites in multiple languages.'
        ),
        'pref': 'network.IDN_show_punycode',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show Punycode', 'Show Unicode'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    'socks_remote_dns': {
        'name': 'SOCKS Proxy Remote DNS',
        'category': 'security',
        'subcategory': 'network',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Resolve DNS through SOCKS proxy to prevent DNS leaks.',
        'full': (
            'When using a SOCKS proxy (like Tor or a VPN SOCKS proxy), DNS queries can bypass '
            'the proxy and go directly to your ISP DNS server, revealing which sites you visit. '
            'Enabling this sends DNS queries through the SOCKS proxy, preventing DNS leaks. '
            'Essential for privacy when using SOCKS proxies. Has no effect without a SOCKS proxy.'
        ),
        'pref': 'network.proxy.socks_remote_dns',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Proxy DNS (Secure)', 'Local DNS (Leaky)'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': True,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    # =========================================================================
    # FEATURES - DOM & NETWORK: Web APIs
    # =========================================================================

    'beacon_api': {
        'name': 'Beacon API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow sites to send analytics data when you leave a page.',
        'full': (
            'The Beacon API allows websites to send small amounts of data to a server when you '
            'leave a page, without delaying navigation. It is primarily used for analytics and '
            'tracking (sending page view duration, click data, etc.). Disabling prevents this '
            'background data sending but may affect some legitimate analytics and session '
            'management. Most users will not notice any difference with it disabled.'
        ),
        'pref': 'beacon.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'device_sensors': {
        'name': 'Device Sensors API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to access device motion and orientation sensors.',
        'full': (
            'The Device Sensors API provides access to accelerometer, gyroscope, and ambient '
            'light sensor data. Used by some web games, VR experiences, and fitness apps. '
            'However, sensor data can be used for fingerprinting and tracking. On desktop '
            'computers these sensors are rarely useful. Disabling improves privacy with minimal '
            'impact on regular browsing.'
        ),
        'pref': 'device.sensors.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'battery_api': {
        'name': 'Battery Status API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to read your battery level.',
        'full': (
            'The Battery Status API lets websites read your device battery level, charging '
            'status, and estimated time remaining. This data can be used for fingerprinting '
            '(unique battery level combinations identify users) and behavioral tracking '
            '(adjusting prices based on low battery urgency). No legitimate website needs '
            'your battery information. Disable for privacy.'
        ),
        'pref': 'dom.battery.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'clipboard_events': {
        'name': 'Clipboard Events',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow sites to detect copy/cut/paste events.',
        'full': (
            'When enabled, websites can detect and intercept clipboard events (copy, cut, paste). '
            'Some sites use this to add attribution text to copied content, prevent copying, '
            'or modify pasted content. Disabling prevents websites from interfering with your '
            'clipboard but may break paste functionality on some web apps (like code editors). '
            'Consider leaving enabled unless you encounter annoying clipboard modifications.'
        ),
        'pref': 'dom.event.clipboardevents.enabled',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'push_notifications_api': {
        'name': 'Push API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to receive push messages from servers.',
        'full': (
            'The Push API enables websites to receive push notifications from their servers '
            'even when the site is not open. This is used by web apps for real-time updates '
            '(email notifications, chat messages, etc.). It requires a persistent connection '
            'to Mozilla push servers. Disabling prevents all web push notifications but also '
            'breaks Progressive Web App (PWA) notifications. Consider using the notifications '
            'permission setting for finer control.'
        ),
        'pref': 'dom.push.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'service_workers': {
        'name': 'Service Workers',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to run background scripts.',
        'full': (
            'Service Workers are scripts that run in the background, enabling offline '
            'functionality, push notifications, and background sync for web apps. They are '
            'essential for Progressive Web Apps (PWAs) and many modern web features. However, '
            'they can also be used for tracking and running code after you leave a site. '
            'Disabling breaks PWAs, offline-capable sites, and push notifications.'
        ),
        'pref': 'dom.serviceWorkers.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'web_notifications': {
        'name': 'Web Notifications API',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to display system notifications.',
        'full': (
            'The Web Notifications API allows websites to display native desktop notifications. '
            'This is the underlying API that powers notification popups from web apps. Disabling '
            'this completely prevents any website from showing notifications, regardless of '
            'individual permission settings. This is more aggressive than the notifications '
            'permission which only controls the default behavior.'
        ),
        'pref': 'dom.webnotifications.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'popup_blocking': {
        'name': 'Block Popups During Page Load',
        'category': 'features',
        'subcategory': 'dom',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Block popup windows that open during page loading.',
        'full': (
            'Prevents websites from opening popup windows automatically while a page is loading. '
            'This blocks many types of unwanted popups, advertisement windows, and redirect '
            'tricks. Keep enabled to prevent popup spam. Some legitimate sites (like banking '
            'or payment gateways) may require popups to function, which can be allowed per-site.'
        ),
        'pref': 'dom.disable_open_during_load',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'minor',
        'values': [True, False],
        'labels': ['Block Popups', 'Allow Popups'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': True,
            'open': True
        }
    },

    # =========================================================================
    # FEATURES - MEDIA: DRM, WebGL, Navigator
    # =========================================================================

    'drm_enabled': {
        'name': 'DRM (Encrypted Media Extensions)',
        'category': 'features',
        'subcategory': 'media',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Enable DRM for streaming services like Netflix and Spotify.',
        'full': (
            'Encrypted Media Extensions (EME) enables DRM-protected content playback. Required '
            'for Netflix, Amazon Prime Video, Disney+, Spotify, and other streaming services. '
            'Firefox uses the Widevine CDM (Content Decryption Module) from Google for DRM. '
            'Disabling breaks all DRM-protected streaming but removes the closed-source Widevine '
            'component. Free software advocates may prefer to disable this.'
        ),
        'pref': 'media.eme.enabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'media_devices_enumeration': {
        'name': 'Media Device Enumeration',
        'category': 'features',
        'subcategory': 'media',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Allow websites to list your audio/video devices.',
        'full': (
            'When enabled, websites can enumerate your media devices (cameras, microphones, '
            'speakers) using the MediaDevices API. This is needed for video calling sites to '
            'let you select which camera/microphone to use. However, the list of devices can '
            'be used for fingerprinting since it is unique to your hardware setup. Disabling '
            'prevents device enumeration but may break device selection in video call apps.'
        ),
        'pref': 'media.navigator.enabled',
        'type': 'toggle',
        'impact': 'medium',
        'compatibility': 'moderate',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': True,
        'recommended': {
            'max_power': True,
            'balanced': True,
            'battery': True,
            'paranoid': False,
            'open': True
        }
    },

    'webgl_disabled': {
        'name': 'Disable WebGL',
        'category': 'features',
        'subcategory': 'media',
        'level': 'advanced',
        'mechanism': 'userjs',
        'short': 'Completely disable WebGL rendering.',
        'full': (
            'Disabling WebGL completely prevents all WebGL content from rendering. WebGL '
            'can be used for GPU fingerprinting by rendering specific graphics and measuring '
            'the output. This is one of the most effective fingerprinting techniques. Disabling '
            'WebGL breaks 3D content, games, Google Maps 3D view, and some data visualizations. '
            'This is separate from "Force WebGL" which forces it on unsupported hardware.'
        ),
        'pref': 'webgl.disabled',
        'type': 'toggle',
        'impact': 'high',
        'compatibility': 'major',
        'values': [True, False],
        'labels': ['WebGL Off', 'WebGL On'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': True,
            'open': False
        }
    },

    # =========================================================================
    # SECURITY - PERMISSIONS: Browser Behavior
    # =========================================================================

    'urlbar_search_suggestions': {
        'name': 'URL Bar Search Suggestions',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Show search suggestions in the address bar dropdown.',
        'full': (
            'When enabled, the address bar shows search suggestions from your search engine '
            'as you type. This sends your partial queries to the search engine in real-time. '
            'This is separate from the main search suggestions toggle and specifically controls '
            'the address bar integration. Disable to prevent sending keystrokes to search engines '
            'when typing in the address bar.'
        ),
        'pref': 'browser.urlbar.suggest.searches',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Enabled', 'Disabled'],
        'default': False,
        'recommended': {
            'max_power': True,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': True
        }
    },

    'aboutconfig_warning': {
        'name': 'about:config Warning Page',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Show warning when opening about:config.',
        'full': (
            'Controls whether Firefox shows a warning page when you open about:config. '
            'The warning page exists to prevent accidental changes to advanced settings. '
            'Experienced users may want to disable this for faster access to about:config. '
            'Disable if you frequently access about:config and understand the risks.'
        ),
        'pref': 'browser.aboutConfig.showWarning',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Show Warning', 'Skip Warning'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    },

    'check_default_browser': {
        'name': 'Check Default Browser',
        'category': 'security',
        'subcategory': 'permissions',
        'level': 'base',
        'mechanism': 'prefs',
        'short': 'Check if Firefox is the default browser on startup.',
        'full': (
            'When enabled, Firefox checks if it is the default browser each time it starts '
            'and prompts you to set it as default if it is not. This can be annoying for users '
            'who intentionally use another browser as default. Disable to stop the default '
            'browser check and prompts.'
        ),
        'pref': 'browser.shell.checkDefaultBrowser',
        'type': 'toggle',
        'impact': 'low',
        'compatibility': 'none',
        'values': [True, False],
        'labels': ['Check', 'Do Not Check'],
        'default': False,
        'recommended': {
            'max_power': False,
            'balanced': False,
            'battery': False,
            'paranoid': False,
            'open': False
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_settings_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all settings for a specific category."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('category') == category
    }


def get_settings_by_subcategory(category: str, subcategory: str) -> Dict[str, Dict[str, Any]]:
    """Get all settings for a specific category and subcategory."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('category') == category and value.get('subcategory') == subcategory
    }


def get_recommended_value(setting_key: str, profile: str) -> Any:
    """Get the recommended value for a setting based on profile type."""
    if setting_key not in SETTINGS_METADATA:
        return None
    setting = SETTINGS_METADATA[setting_key]
    return setting.get('recommended', {}).get(profile, setting.get('default'))


def get_profile_settings(profile_key: str) -> Dict[str, Any]:
    """Get all recommended settings for a preset profile."""
    if profile_key not in PRESET_PROFILES:
        return {}

    priority = PRESET_PROFILES[profile_key].get('priority_profile', 'balanced')
    return {
        key: get_recommended_value(key, priority)
        for key in SETTINGS_METADATA.keys()
    }


def validate_setting_value(setting_key: str, value: Any) -> bool:
    """Validate if a value is valid for a given setting."""
    if setting_key not in SETTINGS_METADATA:
        return False
    setting = SETTINGS_METADATA[setting_key]
    return value in setting.get('values', [])


def get_base_settings() -> Dict[str, Dict[str, Any]]:
    """Get all settings that should be applied via prefs.js (base level)."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('level') == 'base'
    }


def get_advanced_settings() -> Dict[str, Dict[str, Any]]:
    """Get all settings that should be applied via user.js (advanced level)."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('level') == 'advanced'
    }


def get_settings_by_level(level: str) -> Dict[str, Dict[str, Any]]:
    """Get all settings for a specific level ('base' or 'advanced')."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('level') == level
    }


def get_settings_by_mechanism(mechanism: str) -> Dict[str, Dict[str, Any]]:
    """Get all settings for a specific mechanism ('prefs' or 'userjs')."""
    return {
        key: value for key, value in SETTINGS_METADATA.items()
        if value.get('mechanism') == mechanism
    }


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == '__main__':
    print(f"Hardzilla Metadata Module")
    print(f"=" * 50)
    print(f"Loaded {len(SETTINGS_METADATA)} settings")
    print(f"Loaded {len(PRESET_PROFILES)} preset profiles")
    print(f"Loaded {len(CATEGORIES)} categories")
    print()

    # Show settings breakdown by category/subcategory
    print("Settings by Category:")
    for cat_key, cat_data in CATEGORIES.items():
        cat_settings = get_settings_by_category(cat_key)
        print(f"  {cat_data['name']}: {len(cat_settings)} settings")
        for subcat_key, subcat_data in cat_data.get('subcategories', {}).items():
            subcat_settings = get_settings_by_subcategory(cat_key, subcat_key)
            print(f"    - {subcat_data['name']}: {len(subcat_settings)} settings")

    print()
    print("Preset Profiles:")
    for profile_key, profile_data in PRESET_PROFILES.items():
        print(f"  - {profile_data['name']}: {profile_data['description'][:50]}...")
