import json

with open(r'c:\Users\spatchava\EoS\eApps\data\apps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

PLATFORM_EXT = {
    'chrome': '.crx', 'firefox': '.xpi', 'safari': '.safariextz',
    'edge': '.crx', 'opera': '.nex', 'brave': '.crx',
    'vscode': '.vsix', 'jetbrains': '.jar',
    'obsidian': '.obsidian', 'neovim': '.nvim',
    'slack': '.slack-app', 'raycast': '.raycast-ext', 'github': '.github-app',
    'google-workspace': '.gs', 'office365': '.officeaddin',
    'android': '.apk', 'android-tv': '.apk',
    'android-tablet': '.apk', 'wear-os': '.apk',
    'ios': '.ipa', 'ipados': '.ipa', 'apple-tv': '.ipa',
    'windows': '.exe', 'windows-x64': '.exe', 'windows-arm64': '.exe',
    'macos': '.dmg', 'macos-intel': '.dmg', 'macos-apple-silicon': '.dmg',
    'linux': '.AppImage', 'linux-x64': '.AppImage', 'linux-arm64': '.AppImage',
    'eos': '.eapp', 'freebsd': '.tar.gz',
    'web': '.tar.gz', 'pwa': '.pwa', 'wasm': '.wasm',
    'docker': '.tar.gz',
    'x86_64': '.tar.gz', 'arm64': '.tar.gz', 'riscv': '.tar.gz',
    'iso': '.iso', 'img': '.img',
    'stm32': '.bin', 'esp32': '.bin', 'rpi': '.img',
    'firmware': '.bin',
    'virtualbox': '.ova', 'vmware': '.vmdk',
    'qemu': '.qcow2', 'ova': '.ova', 'vmdk': '.vmdk', 'qcow2': '.qcow2',
    'firebase': '.tar.gz', 'cloud': '.tar.gz',
}

BASE = 'https://github.com/embeddedos-org/eApps/releases/download'
changed = 0

for app in data['apps']:
    platforms = app.get('platform', [])
    app_id = app['id']
    version = app.get('version', '1.0.0')

    if len(platforms) == 1:
        plat = platforms[0]
        ext = PLATFORM_EXT.get(plat, '.zip')
        tag = f'{app_id}-v{version}'
        filename = f'{app_id}-{version}{ext}'
        app['downloadUrl'] = f'{BASE}/{tag}/{filename}'
        app['releaseUrl'] = f'{BASE}/{tag}'
        changed += 1
    elif len(platforms) > 1:
        downloads = {}
        tag = f'{app_id}-v{version}'
        for plat in platforms:
            ext = PLATFORM_EXT.get(plat, '.zip')
            filename = f'{app_id}-{version}-{plat}{ext}'
            downloads[plat] = f'{BASE}/{tag}/{filename}'
        app['downloads'] = downloads
        app['releaseUrl'] = f'{BASE}/{tag}'
        if 'downloadUrl' in app:
            del app['downloadUrl']
        changed += 1

with open(r'c:\Users\spatchava\EoS\eApps\data\apps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Updated {changed} app entries with platform-specific release files')
print(f'Total apps: {len(data["apps"])}')

for app in data['apps'][:5]:
    print(f'  {app["id"]}: {app.get("downloadUrl", "multi-platform")}')
    if 'downloads' in app:
        for k, v in list(app['downloads'].items())[:3]:
            print(f'    {k}: {v}')
