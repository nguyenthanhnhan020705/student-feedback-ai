"""After suite: retain refreshed browser evidence and verify original bytes."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory = json.loads((OUT/'preexisting.json').read_text(encoding='utf-8'))
    browser = []
    for name in inventory:
        if ((name.startswith('reports/evidence/frontend/') and name.endswith(('.png','.json')))
                or (name.startswith('reports/evidence/phase-4/') and name.endswith('-mobile-mock.png'))):
            browser.append(name)
    snapshots = {}
    for name in browser:
        original = ROOT/name
        destination = OUT/'browser'/original.name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(original, destination)
        snapshots[destination.relative_to(OUT).as_posix()] = sha(destination)
    restored = []
    for name in browser:
        original = ROOT/name
        if sha(original) != inventory[name]:
            backup = ROOT/'.local-tools/ct5-preexisting-backup'/name
            if (original.resolve() != original or not original.resolve().is_relative_to(ROOT)
                    or sha(backup) != inventory[name]):
                raise ValueError('Cannot safely restore verified browser bytes: '+name)
            shutil.copyfile(backup, original)
            restored.append(name)
    changed = [name for name, expected in inventory.items()
               if not (ROOT/name).is_file() or sha(ROOT/name) != expected]
    report = dict(total=len(inventory), matched=len(inventory)-len(changed), changed=changed,
                  restored=restored, browser_snapshots=snapshots)
    (OUT/'preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if changed:
        raise ValueError('Unexpected preexisting file changes; preserved for investigation')


if __name__ == '__main__': main()
