"""Package the verified maps-and-charts editor preview."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
from package_article import ROOT,package

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dist',type=Path,required=True)
parser.add_argument('--source-project',type=Path,help='Package the authorized source build with an embedded snapshot.')
args=parser.parse_args()
if args.source_project:
    html=(args.dist/'index.html').read_bytes()
    snapshot=(args.source_project/'src/data.json').read_bytes()
    snapshot_hash=hashlib.sha256(snapshot).hexdigest()
    assert re.search(rb'<meta\s+name="data-app-snapshot-sha256"\s+content="'+snapshot_hash.encode()+rb'"',html), 'Source build snapshot metadata does not match reviewed input'
    reviewed=json.loads(snapshot)
    assert reviewed['report']['hideTopbar'] is True and reviewed['buildStatus']=='complete'
    target=ROOT/'editor-maps'
    shutil.copyfile(args.dist/'index.html',target/'index.html')
    # A source build embeds its reviewed snapshot; a previous split-build receipt is stale.
    (target/'data-app-build.json').unlink(missing_ok=True)
    receipt={'buildKind':'authorized-source-build','htmlSha256':hashlib.sha256(html).hexdigest(),'reviewedSnapshotSha256':snapshot_hash,'protectedRuntimeManifestSha256':hashlib.sha256((args.source_project/'protected-runtime.json').read_bytes()).hexdigest(),'authorizedRuntimeFiles':['src/DataAppShell.jsx'],'authorization':'User requested removal of the entire preview toolbar; omitted only in opted-in report view mode.'}
    (target/'source-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('Packaged authorized source build:',target)
else:
    package(args.dist,ROOT/'editor-maps')
