#!/usr/bin/env python3
"""Download official sources to ignored raw storage; export no voter-level data.

Always refetch 2026. Cache the historical 2022 source unless --refresh-baseline.
"""
import argparse,hashlib,json,shutil,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw/early_voting')
    p.add_argument('--refresh-baseline',action='store_true')
    args=p.parse_args();root=args.raw_dir;root.mkdir(parents=True,exist_ok=True)
    manifest_path=root/'source_manifest.json'
    old={x['url']:x for x in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}
    manifest=[]
    for date in ['20221108','20261103']:
        url=f'https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/{date[:4]}_{date[4:6]}_{date[6:]}/absentee_county_{date}.zip'
        archive=root/f'absentee_county_{date}.zip';cache=old.get(url)
        if date=='20221108' and archive.exists() and cache and not args.refresh_baseline:
            if hashlib.sha256(archive.read_bytes()).hexdigest()!=cache['sha256']:raise ValueError('Cached baseline hash mismatch')
            info=dict(cache)
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'ncsu-campus-voting reporting project','Cache-Control':'no-cache'})
            temporary=archive.with_suffix('.download')
            with urllib.request.urlopen(req,timeout=120) as response,temporary.open('wb') as out:
                headers=dict(response.headers);shutil.copyfileobj(response,out)
            with zipfile.ZipFile(temporary) as z:
                if z.testzip() is not None:raise ValueError('Corrupt source archive')
            temporary.replace(archive)
            info={'url':url,'last_modified':headers.get('Last-Modified'),'downloaded_at':headers.get('Date'),'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size}
        with zipfile.ZipFile(archive) as z:
            hits=[name for name in z.namelist() if 'wake' in Path(name).name.lower() and name.lower().endswith('.csv')]
            if len(hits)!=1:raise ValueError('Expected exactly one Wake County CSV')
            (root/f'wake_{date}.csv').write_bytes(z.read(hits[0]));info['member']=hits[0]
        manifest.append(info)
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Official sources saved to ignored data/raw/early_voting; manifest includes freshness and SHA-256.')
if __name__=='__main__':main()
