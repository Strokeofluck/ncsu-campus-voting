"""Prepare the maps-and-charts interview preview from the article's reviewed data."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project-dir',type=Path,required=True)
args=parser.parse_args()
identity_path=ROOT/'report-source/editor-maps/identity.json'
current=json.loads((args.project_dir/'src/data.json').read_text(encoding='utf-8'))
if identity_path.is_file():
    identity=json.loads(identity_path.read_text(encoding='utf-8'))
else:
    identity={'id':current['id']}
    identity_path.write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'scripts/prepare_article_content.py'),'--project-dir',str(args.project_dir)],check=True)
shutil.copytree(ROOT/'report-source/editor-maps',args.project_dir/'src/content/report',dirs_exist_ok=True)
snapshot=json.loads((args.project_dir/'src/data.json').read_text(encoding='utf-8'))
snapshot.update(id=identity['id'],title='NC State voting visuals — editor preview',authoredRevision=3,buildStatus='complete')
(args.project_dir/'src/data.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert snapshot['id']!=json.loads((ROOT/'report-source/article-snapshot.json').read_text(encoding='utf-8'))['id']
print('Prepared independent visual editor preview; shared maps, age-growth chart and benchmark use the same reviewed evidence as the article.')
