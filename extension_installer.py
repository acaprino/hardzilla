#!/usr/bin/env python3
"""
Hardzilla Extension Installer
=============================
Script standalone per installare estensioni Firefox predefinite nel profilo utente.

Uso:
    python extension_installer.py                    # Modalita' interattiva
    python extension_installer.py --profile PATH     # Specifica profilo
    python extension_installer.py --list             # Lista estensioni disponibili
    python extension_installer.py --all              # Installa tutte le estensioni
    python extension_installer.py --privacy          # Solo estensioni privacy/security
    python extension_installer.py --ext ublock,dark  # Installa estensioni specifiche
"""

import argparse
import json
import logging
import os
import platform
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ESTENSIONI PREDEFINITE
# ============================================================================

EXTENSIONS = {
    'ublock': {
        'name': 'uBlock Origin',
        'id': 'uBlock0@raymondhill.net',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi',
        'description': 'Blocco efficiente di ads e tracker',
        'category': 'privacy'
    },
    'privacy_badger': {
        'name': 'Privacy Badger',
        'id': 'jid1-MnnxcxisBPnSXQ@jetpack',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/privacy-badger17/latest.xpi',
        'description': 'Blocca automaticamente i tracker invisibili',
        'category': 'privacy'
    },
    'cookie_autodelete': {
        'name': 'Cookie AutoDelete',
        'id': 'CookieAutoDelete@kennydo.com',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/cookie-autodelete/latest.xpi',
        'description': 'Elimina automaticamente i cookie alla chiusura delle tab',
        'category': 'privacy'
    },
    'canvasblocker': {
        'name': 'CanvasBlocker',
        'id': 'CanvasBlocker@kkapsner.de',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/canvasblocker/latest.xpi',
        'description': 'Previene il fingerprinting via canvas',
        'category': 'privacy'
    },
    'decentraleyes': {
        'name': 'Decentraleyes',
        'id': 'jid1-BoFifL9Vbdl2zQ@jetpack',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/decentraleyes/latest.xpi',
        'description': 'Emulazione CDN locale per prevenire tracking',
        'category': 'privacy'
    },
    'https_everywhere': {
        'name': 'HTTPS Everywhere',
        'id': 'https-everywhere@eff.org',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/https-everywhere/latest.xpi',
        'description': 'Forza HTTPS su molti siti',
        'category': 'security'
    },
    'clearurls': {
        'name': 'ClearURLs',
        'id': '{74145f27-f039-47ce-a470-a662b129930a}',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/clearurls/latest.xpi',
        'description': 'Rimuove elementi di tracking dagli URL',
        'category': 'privacy'
    },
    'bitwarden': {
        'name': 'Bitwarden Password Manager',
        'id': '{446900e4-71c2-419f-a6a7-df9c091e268b}',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/bitwarden-password-manager/latest.xpi',
        'description': 'Gestore password gratuito e open-source',
        'category': 'security'
    },
    'darkreader': {
        'name': 'Dark Reader',
        'id': 'addon@darkreader.org',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/darkreader/latest.xpi',
        'description': 'Modalita dark per ogni sito web',
        'category': 'utility'
    },
    'absolute_enable': {
        'name': 'Absolute Enable Right Click & Copy',
        'id': '{9350bc42-47fb-4598-ae0f-825e3dd9ba16}',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/absolute-enable-right-click/latest.xpi',
        'description': 'Riattiva click destro e copia su siti che li bloccano',
        'category': 'utility'
    },
    'bypass_paywalls': {
        'name': 'Bypass Paywalls Clean',
        'id': 'magnolia@12.34',
        'url': 'https://gitflic.ru/project/magnolia1234/bpc_uploads/blob/raw?file=bypass_paywalls_clean-latest.xpi',
        'description': 'Bypassa i paywall su siti di news e magazine',
        'category': 'utility'
    },
    'tampermonkey': {
        'name': 'Tampermonkey',
        'id': 'firefox@tampermonkey.net',
        'url': 'https://addons.mozilla.org/firefox/downloads/latest/tampermonkey/latest.xpi',
        'description': 'Gestore userscript - esegue script personalizzati sui siti',
        'category': 'utility'
    }
}

# Preset di estensioni per categoria
PRESETS = {
    'privacy': ['ublock', 'privacy_badger', 'cookie_autodelete', 'canvasblocker',
                'decentraleyes', 'clearurls'],
    'security': ['ublock', 'https_everywhere', 'bitwarden', 'clearurls'],
    'essential': ['ublock', 'bitwarden', 'darkreader'],
    'all': list(EXTENSIONS.keys())
}


# ============================================================================
# FUNZIONI DI UTILITA'
# ============================================================================

def get_firefox_profiles_dir() -> Optional[Path]:
    """Trova la directory dei profili Firefox in base al sistema operativo."""
    system = platform.system()
    home = Path.home()

    if system == 'Windows':
        profiles_dir = home / 'AppData' / 'Roaming' / 'Mozilla' / 'Firefox' / 'Profiles'
    elif system == 'Darwin':  # macOS
        profiles_dir = home / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
    else:  # Linux e altri
        profiles_dir = home / '.mozilla' / 'firefox'

    if profiles_dir.exists():
        return profiles_dir
    return None


def find_firefox_profiles() -> list[dict]:
    """Trova tutti i profili Firefox disponibili."""
    profiles = []

    # Cerca profili standard
    profiles_dir = get_firefox_profiles_dir()
    if profiles_dir:
        for item in profiles_dir.iterdir():
            if item.is_dir():
                # Verifica se e' un profilo valido (contiene prefs.js o times.json)
                if (item / 'prefs.js').exists() or (item / 'times.json').exists():
                    profiles.append({
                        'name': item.name,
                        'path': item,
                        'type': 'standard'
                    })

    # Cerca Firefox Portable nella home
    portable_paths = [
        Path.home() / 'FirefoxPortable' / 'Data' / 'profile',
        Path.home() / 'FirefoxPortable' / 'Data' / 'Profile',
        Path.home() / 'Desktop' / 'FirefoxPortable' / 'Data' / 'profile',
    ]

    for portable_path in portable_paths:
        if portable_path.exists():
            profiles.append({
                'name': 'Firefox Portable',
                'path': portable_path,
                'type': 'portable'
            })
            break

    return profiles


def download_file_safely(url: str, dest_path: Path, max_size_mb: int = 50,
                         timeout: int = 60) -> bool:
    """
    Scarica un file in modo sicuro con limiti di dimensione e timeout.

    Args:
        url: URL da cui scaricare (HTTPS preferito)
        dest_path: Percorso dove salvare il file
        max_size_mb: Dimensione massima in MB (default 50MB)
        timeout: Timeout in secondi (default 60s)

    Returns:
        True se download riuscito

    Raises:
        ValueError: Se il file e' troppo grande
        urllib.error.URLError: Per errori di rete
    """
    max_bytes = max_size_mb * 1024 * 1024

    # Avvisa per URL non-HTTPS
    if not url.startswith('https://'):
        logger.warning(f"URL non-HTTPS: {url}")

    # Crea contesto SSL
    context = ssl.create_default_context()

    # Crea richiesta con User-Agent
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Hardzilla/3.0 Firefox-Extension-Installer'}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            # Controlla dimensione se disponibile
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > max_bytes:
                raise ValueError(
                    f"File troppo grande: {int(content_length) / 1024 / 1024:.1f}MB > {max_size_mb}MB"
                )

            # Download con limite di dimensione
            downloaded = 0
            chunks = []

            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    raise ValueError(f"Download supera il limite di {max_size_mb}MB")
                chunks.append(chunk)

            # Scrivi file solo dopo download completo
            with open(dest_path, 'wb') as out_file:
                for chunk in chunks:
                    out_file.write(chunk)

            logger.info(f"Scaricato {downloaded / 1024:.1f}KB da {url}")
            return True

    except Exception as e:
        # Pulisci file parziale se esiste
        if dest_path.exists():
            try:
                dest_path.unlink()
            except OSError:
                pass
        logger.error(f"Download fallito per {url}: {e}")
        raise


def install_extension(ext_key: str, profile_path: Path) -> tuple[bool, str]:
    """
    Installa una singola estensione nel profilo Firefox.

    Args:
        ext_key: Chiave dell'estensione nel dizionario EXTENSIONS
        profile_path: Percorso del profilo Firefox

    Returns:
        Tupla (successo, messaggio)
    """
    if ext_key not in EXTENSIONS:
        return False, f"Estensione '{ext_key}' non trovata"

    ext = EXTENSIONS[ext_key]

    # Crea directory estensioni
    ext_dir = profile_path / 'extensions'
    ext_dir.mkdir(exist_ok=True)

    xpi_path = ext_dir / f"{ext['id']}.xpi"

    try:
        logger.info(f"Scaricando {ext['name']}...")
        download_file_safely(ext['url'], xpi_path)
        return True, f"Installata: {ext['name']}"
    except Exception as e:
        return False, f"Errore {ext['name']}: {str(e)}"


def check_installed_extensions(profile_path: Path) -> dict:
    """
    Controlla quali estensioni sono gia' installate nel profilo.

    Args:
        profile_path: Percorso del profilo Firefox

    Returns:
        Dict con stato di ogni estensione
    """
    ext_dir = profile_path / 'extensions'
    status = {}

    for key, ext in EXTENSIONS.items():
        xpi_path = ext_dir / f"{ext['id']}.xpi"
        status[key] = {
            'name': ext['name'],
            'installed': xpi_path.exists()
        }

    return status


def list_extensions(show_status: bool = False, profile_path: Optional[Path] = None):
    """Mostra lista delle estensioni disponibili."""
    print("\n" + "=" * 60)
    print("ESTENSIONI DISPONIBILI")
    print("=" * 60)

    status = {}
    if show_status and profile_path:
        status = check_installed_extensions(profile_path)

    # Raggruppa per categoria
    categories = {}
    for key, ext in EXTENSIONS.items():
        cat = ext.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((key, ext))

    for cat, exts in sorted(categories.items()):
        print(f"\n[{cat.upper()}]")
        for key, ext in exts:
            installed_mark = ""
            if show_status and key in status:
                installed_mark = " [INSTALLATA]" if status[key]['installed'] else ""
            print(f"  {key:20} - {ext['name']}{installed_mark}")
            print(f"  {' '*20}   {ext['description']}")

    print("\n" + "=" * 60)
    print("PRESET DISPONIBILI:")
    print("=" * 60)
    for preset_name, preset_exts in PRESETS.items():
        print(f"  --{preset_name:15} : {', '.join(preset_exts[:4])}...")
    print()


def select_profile_interactive(profiles: list[dict]) -> Optional[Path]:
    """Permette all'utente di selezionare un profilo in modo interattivo."""
    if not profiles:
        print("Nessun profilo Firefox trovato!")
        return None

    print("\nProfili Firefox trovati:")
    print("-" * 50)
    for i, p in enumerate(profiles, 1):
        print(f"  [{i}] {p['name']} ({p['type']})")
        print(f"      {p['path']}")
    print("-" * 50)

    while True:
        try:
            choice = input("\nSeleziona profilo (numero) o 'q' per uscire: ").strip()
            if choice.lower() == 'q':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                return profiles[idx]['path']
            print("Selezione non valida. Riprova.")
        except ValueError:
            print("Inserisci un numero valido.")


def select_extensions_interactive() -> list[str]:
    """Permette all'utente di selezionare le estensioni in modo interattivo."""
    list_extensions()

    print("\nOpzioni:")
    print("  - Inserisci le chiavi separate da virgola (es: ublock,darkreader)")
    print("  - Inserisci 'all' per tutte le estensioni")
    print("  - Inserisci 'privacy' per preset privacy")
    print("  - Inserisci 'security' per preset security")
    print("  - Inserisci 'essential' per preset essenziale")

    choice = input("\nEstensioni da installare: ").strip().lower()

    if choice in PRESETS:
        return PRESETS[choice]

    # Parse lista separata da virgola
    selected = [e.strip() for e in choice.split(',') if e.strip()]

    # Valida selezione
    valid = []
    for ext in selected:
        if ext in EXTENSIONS:
            valid.append(ext)
        else:
            print(f"Avviso: '{ext}' non trovata, ignorata.")

    return valid


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Hardzilla Extension Installer - Installa estensioni Firefox predefinite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  %(prog)s --list                    # Mostra estensioni disponibili
  %(prog)s --profile ~/firefox/prof  # Usa profilo specifico
  %(prog)s --all                     # Installa tutte le estensioni
  %(prog)s --privacy                 # Installa solo estensioni privacy
  %(prog)s --ext ublock,darkreader   # Installa estensioni specifiche
  %(prog)s --check                   # Controlla estensioni installate
        """
    )

    parser.add_argument('--profile', '-p', type=str,
                        help='Percorso del profilo Firefox')
    parser.add_argument('--list', '-l', action='store_true',
                        help='Mostra lista estensioni disponibili')
    parser.add_argument('--check', '-c', action='store_true',
                        help='Controlla estensioni installate nel profilo')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Installa tutte le estensioni')
    parser.add_argument('--privacy', action='store_true',
                        help='Installa preset privacy')
    parser.add_argument('--security', action='store_true',
                        help='Installa preset security')
    parser.add_argument('--essential', action='store_true',
                        help='Installa preset essenziale')
    parser.add_argument('--ext', '-e', type=str,
                        help='Lista estensioni separate da virgola')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Modalita silenziosa (meno output)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simula installazione senza scaricare')

    args = parser.parse_args()

    # Modalita silenziosa
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Solo lista estensioni
    if args.list:
        profile_path = Path(args.profile) if args.profile else None
        list_extensions(show_status=bool(profile_path), profile_path=profile_path)
        return 0

    # Determina profilo
    profile_path = None
    if args.profile:
        profile_path = Path(args.profile)
        if not profile_path.exists():
            print(f"Errore: Profilo non trovato: {profile_path}")
            return 1
    else:
        profiles = find_firefox_profiles()
        profile_path = select_profile_interactive(profiles)
        if not profile_path:
            print("Nessun profilo selezionato. Uscita.")
            return 0

    print(f"\nProfilo selezionato: {profile_path}")

    # Solo controllo stato
    if args.check:
        status = check_installed_extensions(profile_path)
        print("\nStato estensioni:")
        print("-" * 50)
        installed_count = 0
        for key, info in status.items():
            mark = "[X]" if info['installed'] else "[ ]"
            print(f"  {mark} {info['name']}")
            if info['installed']:
                installed_count += 1
        print("-" * 50)
        print(f"Installate: {installed_count}/{len(status)}")
        return 0

    # Determina estensioni da installare
    extensions_to_install = []

    if args.all:
        extensions_to_install = PRESETS['all']
    elif args.privacy:
        extensions_to_install = PRESETS['privacy']
    elif args.security:
        extensions_to_install = PRESETS['security']
    elif args.essential:
        extensions_to_install = PRESETS['essential']
    elif args.ext:
        extensions_to_install = [e.strip() for e in args.ext.split(',') if e.strip()]
        # Valida
        valid = []
        for ext in extensions_to_install:
            if ext in EXTENSIONS:
                valid.append(ext)
            else:
                print(f"Avviso: '{ext}' non trovata, ignorata.")
        extensions_to_install = valid
    else:
        # Modalita interattiva
        extensions_to_install = select_extensions_interactive()

    if not extensions_to_install:
        print("Nessuna estensione selezionata. Uscita.")
        return 0

    # Mostra riepilogo
    print(f"\nEstensioni da installare ({len(extensions_to_install)}):")
    for ext_key in extensions_to_install:
        ext = EXTENSIONS.get(ext_key, {})
        print(f"  - {ext.get('name', ext_key)}")

    if args.dry_run:
        print("\n[DRY-RUN] Simulazione completata. Nessun file scaricato.")
        return 0

    # Conferma
    confirm = input("\nProcedere con l'installazione? [s/N]: ").strip().lower()
    if confirm not in ('s', 'si', 'y', 'yes'):
        print("Installazione annullata.")
        return 0

    # Installa estensioni
    print("\n" + "=" * 60)
    print("INSTALLAZIONE")
    print("=" * 60)

    installed = []
    failed = []

    for ext_key in extensions_to_install:
        success, message = install_extension(ext_key, profile_path)
        if success:
            installed.append(message)
            print(f"  [OK] {message}")
        else:
            failed.append(message)
            print(f"  [ERRORE] {message}")

    # Riepilogo finale
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    print(f"  Installate con successo: {len(installed)}")
    print(f"  Fallite: {len(failed)}")

    if failed:
        print("\n  Errori:")
        for err in failed:
            print(f"    - {err}")

    print("\n  IMPORTANTE: Riavvia Firefox per caricare le estensioni!")
    print("=" * 60)

    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
