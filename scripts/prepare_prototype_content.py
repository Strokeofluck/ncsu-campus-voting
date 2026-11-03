"""Prepare the existing prototype with its reviewed snapshot and white palette."""
import argparse, shutil
from pathlib import Path
from apply_voting_palette import apply_palette

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project-dir', type=Path, required=True)
args = parser.parse_args()
shutil.copytree(ROOT / 'report-source/report', args.project_dir / 'src/content/report', dirs_exist_ok=True)
shutil.copyfile(ROOT / 'report-source/snapshot.json', args.project_dir / 'src/data.json')
apply_palette(args.project_dir)
print('Prepared the existing prototype content, identity, evidence and publication palette.')
