import re
from pathlib import Path

for path in Path('templates').rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    if 'method="POST"' not in text:
        continue
    if 'csrf_field()' in text:
        continue
    new, n = re.subn(
        r'(<form[^>]*method="POST"[^>]*>)',
        r'\1\n                        {{ csrf_field() }}',
        text,
    )
    if n:
        path.write_text(new, encoding='utf-8')
        print(f'patched {path} ({n} forms)')
