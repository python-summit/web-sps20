'''
Refactoring the (older) dir name of recordings to spsYY-<name>
Year will be parsed out of the contents.lr in that folder
'''

from pathlib import Path

path = Path('sps20/content/talk-recordings')

for p in path.iterdir():
    if p.is_dir() and not p.name.startswith('sps'):
        contents = p / 'contents.lr'
        if contents.exists():
            with contents.open() as f:
                for line in f:
                    if 'year' in line:
                        year = line.split()[-1]
                        break
            new_name = f'sps{year[2:]}-{p.name}'
            p.rename(path / new_name) # <- DANGER ZONE
            print(f'{p.name} -> {new_name}')