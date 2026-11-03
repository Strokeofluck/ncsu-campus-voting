"""Apply the shared publication palette through the supported theme file."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = '/* BEGIN VOTING PUBLICATION PALETTE */'

def apply_palette(project_dir):
    path = Path(project_dir) / 'src/theme.css'
    base = path.read_text(encoding='utf-8').split(MARKER)[0].rstrip()
    palette = (ROOT / 'report-source/palette.css').read_text(encoding='utf-8')
    path.write_text(base + '\n\n' + MARKER + '\n' + palette, encoding='utf-8')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir', type=Path, required=True)
    apply_palette(parser.parse_args().project_dir)
