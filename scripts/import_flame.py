"""Import a Flutter ZIP while retaining the site's device gate and page shell."""
import sys
from pathlib import Path
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]
with ZipFile(sys.argv[1]) as archive:
    entries = archive.infolist()
    for entry in entries:
        path = Path(entry.filename)
        if path.is_absolute() or '..' in path.parts or path.parts[0] != 'flame':
            raise ValueError(f'Unexpected archive path: {entry.filename}')
    for entry in entries:
        if entry.is_dir() or entry.filename == 'flame/index.html':
            continue
        destination = root / entry.filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = archive.read(entry)
        if entry.filename == 'flame/privacy.html':
            html = content.decode('utf-8')
            if 'name="description"' not in html:
                html = html.replace('</head>', '<meta name="description" content="Learn how Flame stores progress and handles optional analytics, and how to change your privacy choice."></head>')
            if 'rel="canonical"' not in html:
                html = html.replace('</head>', '<link rel="canonical" href="https://mobilebraingames.com/flame/privacy.html"></head>')
            content = html.encode('utf-8')
        destination.write_bytes(content)
print('Imported Flame build; preserved flame/index.html and its device gate.')
