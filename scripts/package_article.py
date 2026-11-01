"""Copy a verified Data app build into the existing site's article/ route."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def package(dist,target):
 manifest=json.loads((dist/'data-app-build.json').read_text(encoding='utf-8'))
 for key in ['html','snapshot']:
  item=manifest[key]
  assert hashlib.sha256((dist/item['path']).read_bytes()).hexdigest()==item['sha256']
 target.mkdir(parents=True,exist_ok=True)
 for name in ['index.html','data-app-build.json',manifest['snapshot']['path']]:shutil.copyfile(dist/name,target/name)
 if target.resolve()==(ROOT/'article').resolve():
  for stale in target.glob('snapshot.*.json'):
   if stale.name==manifest['snapshot']['path']:continue
   tracked=subprocess.run(['git','ls-files','--error-unmatch','--',str(stale.relative_to(ROOT))],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
   if not tracked:stale.unlink()
 print('Packaged verified article build:',target)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dist',type=Path,required=True);p.add_argument('--preview-root',type=Path)
 args=p.parse_args();package(args.dist,ROOT/'article')
 if args.preview_root:package(args.dist,args.preview_root/'article')
