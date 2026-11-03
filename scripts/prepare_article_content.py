"""Copy authored article content and its shared map dependencies into a prepared app."""
import argparse,re,shutil
from pathlib import Path
from apply_voting_palette import apply_palette
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-dir',type=Path,required=True);args=p.parse_args()
target=args.project_dir/'src/content/report';target.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'report-source/article',target,dirs_exist_ok=True)
shared=ROOT/'report-source/report';pending=[shared/'CampusWalkingMap.jsx',shared/'CampusPassbyMap.jsx'];done=set()
while pending:
 source=pending.pop().resolve()
 if source in done:continue
 done.add(source);relative=source.relative_to(shared.resolve());dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 if source.suffix not in {'.jsx','.js','.css'}:continue
 for name in re.findall(r'''(?:from\s+|import\s*)['"](\.[^'"]+)['"]''',source.read_text(encoding='utf-8')):
  dependency=(source.parent/name).resolve()
  if dependency.is_relative_to(shared.resolve()) and dependency.is_file():pending.append(dependency)
shutil.copyfile(ROOT/'report-source/article-snapshot.json',args.project_dir/'src/data.json')
apply_palette(args.project_dir)
print('Prepared article and',len(done),'shared authored map files; identity and runtime preserved.')
