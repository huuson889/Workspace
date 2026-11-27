"""Download pinned build dependencies only. The delivered HTML never fetches them."""
from pathlib import Path
import argparse, hashlib, json, urllib.request
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
a = p.parse_args()
lock = json.loads(Path(__file__).with_name('dependencies.json').read_text())
out = Path(a.output)
out.mkdir(parents=True, exist_ok=True)
for name, item in lock['files'].items():
    path = out / name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']:
        print('Verified', name)
        continue
    url = f"https://raw.githubusercontent.com/{lock['repository']}/{lock['commit']}/{item['path']}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit('SHA256 mismatch: ' + name)
    path.write_bytes(data)
    print('Downloaded and verified', name)
