import json

with open(r'c:\Users\spatchava\EoS\eApps\data\apps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Platform-specific formats for remaining .zip entries
FIXES = {
    'obsidian': '.obsidian',       # Obsidian plugin format
    'neovim': '.nvim',             # Neovim plugin format
    'slack': '.slack-app',         # Slack app manifest
    'raycast': '.raycast-ext',     # Raycast extension
    'github': '.github-app',      # GitHub App
    'google-workspace': '.gs',     # Google Apps Script
    'office365': '.officeaddin',   # Office Add-in
    'pwa': '.pwa',                 # Progressive Web App
}

BASE = 'https://github.com/embeddedos-org/eApps/releases/download'
changed = 0

for app in data['apps']:
    # Fix single downloadUrl
    url = app.get('downloadUrl', '')
    if url.endswith('.zip'):
        platforms = app.get('platform', [])
        if platforms:
            plat = platforms[0]
            ext = FIXES.get(plat, '')
            if ext:
                app_id = app['id']
                version = app.get('version', '1.0.0')
                tag = f'{app_id}-v{version}'
                filename = f'{app_id}-{version}{ext}'
                app['downloadUrl'] = f'{BASE}/{tag}/{filename}'
                changed += 1
                print(f'Fixed: {app_id} -> {filename}')

    # Fix multi-platform downloads
    downloads = app.get('downloads', {})
    for plat, dl in list(downloads.items()):
        if dl.endswith('.zip'):
            ext = FIXES.get(plat, '')
            if ext:
                app_id = app['id']
                version = app.get('version', '1.0.0')
                tag = f'{app_id}-v{version}'
                filename = f'{app_id}-{version}-{plat}{ext}'
                downloads[plat] = f'{BASE}/{tag}/{filename}'
                changed += 1
                print(f'Fixed: {app_id}:{plat} -> {filename}')

with open(r'c:\Users\spatchava\EoS\eApps\data\apps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\nFixed {changed} remaining .zip entries')
