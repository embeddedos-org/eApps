import json

with open(r'c:\Users\spatchava\EoS\eApps\data\apps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

zips = 0
proper = 0
zip_apps = []

for app in data['apps']:
    url = app.get('downloadUrl', '')
    downloads = app.get('downloads', {})
    if url.endswith('.zip'):
        zips += 1
        zip_apps.append(f"  ZIP: {app['id']} -> {url.split('/')[-1]}")
    elif url and not url.endswith('.zip'):
        proper += 1
    for plat, dl in downloads.items():
        if dl.endswith('.zip'):
            zips += 1
            zip_apps.append(f"  ZIP: {app['id']}:{plat} -> {dl.split('/')[-1]}")
        else:
            proper += 1

for z in zip_apps:
    print(z)
print(f"\nTotal: {proper} platform-specific, {zips} still .zip")
