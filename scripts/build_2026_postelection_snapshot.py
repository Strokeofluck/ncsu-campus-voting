#!/usr/bin/env python3
"""Independent November 2026 NCSBE snapshot: Talley 2022 vs Western Blvd 2026.
Original voter files remain in ignored data/raw. Output is aggregate-only.
"""
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, date, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data/raw/early_voting"
OUT=ROOT/"data/processed/nov2026"
ELECTION={2022:"20221108",2026:"20261103"}
START={2022:date(2022,10,20),2026:date(2026,10,15)}
SITE={2022:"TA - NCSU TALLEY STUDENT CENTER",2026:"NCSU WESTERN BLVD BUSINESS SERVICES"}
BANDS=[(18,24,"18-24"),(25,34,"25-34"),(35,44,"35-44"),(45,64,"45-64"),(65,120,"65+")]

def pct(a,b):
    return round(a/b*100,3) if b else None

def change_pct(a,b):
    return round((b-a)/a*100,3) if a else None

def age_band(age):
    for lo,hi,label in BANDS:
        if age is not None and lo<=age<=hi:return label
    return "Unknown"

def write_csv(filename,fields,rows):
    with (OUT/filename).open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def read_year(year):
    stamp=ELECTION[year]
    url=f"https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/{stamp[:4]}_{stamp[4:6]}_{stamp[6:]}/absentee_county_{stamp}.zip"
    RAW.mkdir(parents=True,exist_ok=True)
    archive=RAW/f"nov_snapshot_{stamp}.zip"
    request=urllib.request.Request(url,headers={"User-Agent":"ncsu-campus-voting reporter","Cache-Control":"no-cache"})
    with urllib.request.urlopen(request,timeout=180) as response:
        last_modified=response.headers.get("Last-Modified")
        with archive.open("wb") as destination:shutil.copyfileobj(response,destination)
    sha=hashlib.sha256()
    with archive.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):sha.update(block)
    with zipfile.ZipFile(archive) as z:
        names=[name for name in z.namelist() if Path(name).name.upper()==f"WAKE_ABSENTEE_{stamp}.CSV"]
        if len(names)!=1:raise RuntimeError(f"Cannot identify Wake CSV member: {names}")
        source_name=names[0]
        raw_csv=RAW/f"nov_snapshot_wake_{stamp}.csv"
        with z.open(source_name) as src, raw_csv.open("wb") as dst:shutil.copyfileobj(src,dst)

    totals=Counter()
    profiles=Counter()
    precincts=defaultdict(Counter)
    daily=Counter()
    seen=set()
    dates=set()
    all_site_names=Counter()
    with raw_csv.open(encoding="latin-1",newline="") as f:
        reader=csv.DictReader(f)
        required={"county_desc","ncid","ballot_req_type","ballot_rtn_status","ballot_rtn_dt",
                  "site_name","age","sdr","voter_party_code","race","ethnicity","gender","precinct_desc"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing NCSBE columns {year}: {required-set(reader.fieldnames or [])}")
        for r in reader:
            if r["county_desc"].strip().upper()!="WAKE":continue
            if r["ballot_req_type"].strip().upper() not in {"ONE-STOP","ONE STOP","EARLY VOTING"}:continue
            if r["ballot_rtn_status"].strip().upper()!="ACCEPTED":continue
            ident=r["ncid"].strip()
            if not ident or ident in seen:raise ValueError(f"Missing/duplicate accepted early-voter NCID {year}")
            seen.add(ident)
            voting_date=datetime.strptime(r["ballot_rtn_dt"].strip(),"%m/%d/%Y").date()
            day=(voting_date-START[year]).days
            if day<0 or day>16:raise ValueError(f"Out of range early date {voting_date} in {year}")
            dates.add(voting_date.isoformat())
            site_name=r["site_name"].strip()
            all_site_names[site_name]+=1
            is_site=site_name==SITE[year]
            precinct=r["precinct_desc"].strip() or "Unknown"
            try:age=int(r["age"].strip())
            except ValueError:age=None
            scopes=["Wake County"]+(["Campus site"] if is_site else [])
            for scope in scopes:
                totals[scope]+=1
                daily[(day,scope)]+=1
                precincts[precinct][scope]+=1
                if 18<=age<=24 if age is not None else False:totals[(scope,"18-24")]+=1
                for dimension,value in [
                    ("age_band",age_band(age)),("party",r["voter_party_code"].strip()),
                    ("race",r["race"].strip()),("ethnicity",r["ethnicity"].strip()),
                    ("gender",r["gender"].strip())]:
                    profiles[(scope,dimension,value or "Unknown")]+=1
                if r["sdr"].strip().upper() in {"Y","YES"}:totals[(scope,"sdr")]+=1
    if SITE[year] not in all_site_names:raise ValueError(f"Missing campus-site name {year}; names {all_site_names.most_common(12)}")
    if year==2022 and (totals["Campus site"]!=10390 or totals["Wake County"]!=219169):
        raise ValueError("2022 Talley/Wake totals fail official historical validation")
    if year==2026 and "2026-10-31" not in dates:
        raise ValueError(f"2026 file not yet complete through final early voting day; latest {max(dates)}")
    if sum(v["Wake County"] for v in precincts.values())!=totals["Wake County"]:
        raise ValueError("Precinct aggregation does not reconcile with Wake total")
    return {"totals":totals,"profiles":profiles,"precincts":precincts,"daily":daily,
            "dates":sorted(dates),"source":{"year":year,"url":url,"zip_sha256":sha.hexdigest(),
                "zip_last_modified_utc":last_modified,"zip_bytes":archive.stat().st_size,
                "csv_member":source_name,"retrieved_utc":datetime.now(timezone.utc).isoformat()},
            "unique_voters":len(seen),"site_name":SITE[year]}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    d={y:read_year(y) for y in (2022,2026)}
    a,b=d[2022]["totals"],d[2026]["totals"]
    metrics=[]
    for measure,k in [("Campus-site accepted early ballots","Campus site"),
                      ("Wake accepted early ballots","Wake County"),
                      ("Campus-site accepted early ballots, age 18-24",("Campus site","18-24")),
                      ("Wake accepted early ballots, age 18-24",("Wake County","18-24")),
                      ("Campus-site accepted same-day-registration ballots",("Campus site","sdr"))]:
        metrics.append({"measure":measure,"2022":a[k],"2026":b[k],
                        "difference":b[k]-a[k],"change_type":"percent","change":change_pct(a[k],b[k])})
    for measure,numerator,denominator in [
        ("Campus site share of Wake early ballots","Campus site","Wake County"),
        ("Age 18-24 share of campus-site ballots",("Campus site","18-24"),"Campus site"),
        ("Campus site share of Wake age 18-24 ballots",("Campus site","18-24"),("Wake County","18-24")),
        ("Same-day registration share of campus-site ballots",("Campus site","sdr"),"Campus site")]:
        old,new=pct(a[numerator],a[denominator]),pct(b[numerator],b[denominator])
        metrics.append({"measure":measure,"2022":old,"2026":new,
                        "difference":None,"change_type":"percentage points","change":round(new-old,3)})
    write_csv("2022_vs_2026_summary.csv",list(metrics[0]),metrics)

    profiles=[]
    for year in (2022,2026):
        for (scope,dim,val),count in sorted(d[year]["profiles"].items()):
            profiles.append({"year":year,"scope":scope,"dimension":dim,"value":val,
                             "ballots":count,"share_pct":pct(count,d[year]["totals"][scope])})
    write_csv("2022_vs_2026_demographics.csv",list(profiles[0]),profiles)

    daily=[]
    for year in (2022,2026):
        for day in range(17):
            for scope in ("Campus site","Wake County"):
                daily.append({"year":year,"day":day+1,"date":(START[year].toordinal()+day),
                              "scope":scope,"accepted_early_ballots":d[year]["daily"][(day,scope)]})
    for row in daily:row["date"]=date.fromordinal(row["date"]).isoformat()
    write_csv("2022_vs_2026_daily.csv",list(daily[0]),daily)

    precinct_rows=[]
    precinct_keys=sorted(set(d[2022]["precincts"])|set(d[2026]["precincts"]))
    for precinct in precinct_keys:
        row={"residential_precinct":precinct}
        for year in (2022,2026):
            counts=d[year]["precincts"][precinct]
            row[f"site_ballots_{year}"]=counts["Campus site"]
            row[f"all_wake_early_ballots_{year}"]=counts["Wake County"]
            row[f"site_use_share_pct_{year}"]=pct(counts["Campus site"],counts["Wake County"])
        row["site_ballot_change"]=row["site_ballots_2026"]-row["site_ballots_2022"]
        old,new=row["site_use_share_pct_2022"],row["site_use_share_pct_2026"]
        row["site_use_share_change_pp"]=round(new-old,3) if old is not None and new is not None else None
        precinct_rows.append(row)
    write_csv("2022_vs_2026_residential_precincts.csv",list(precinct_rows[0]),precinct_rows)

    summary={"snapshot_date":"2026-11-04","status":"PRELIMINARY: post-election source can change until canvass",
             "period_2022":"2022-10-20 to 2022-11-05 (17 days)",
             "period_2026":"2026-10-15 to 2026-10-31 (17 days)",
             "metrics":metrics,"sources":[d[y]["source"] for y in (2022,2026)],
             "qa":{str(y):{"wake_early":d[y]["totals"]["Wake County"],
                           "campus_early":d[y]["totals"]["Campus site"],
                           "unique_early_voters":d[y]["unique_voters"],
                           "last_voting_date":d[y]["dates"][-1],
                           "site_name":d[y]["site_name"]} for y in (2022,2026)},
             "notes":["Party is voter registration, not candidate selection.",
                      "Ages 18-24 are a proxy, not verified NC State students.",
                      "Residential-precinct changes compare separate populations, not same-person movement.",
                      "Poll site move cannot be causally evaluated from these counts alone.",
                      "Election Day voting is excluded; 2024 is excluded from this midterm study.",
                      "Names, addresses and voter identifiers are omitted from published outputs."]}
    (OUT/"research_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")

    lines=["# November 4, 2026: Talley versus Western Boulevard", "",
           "PRELIMINARY accepted early-voting records; subject to later changes during canvass.",
           "Comparison: all 17 days, 2022 midterm versus 2026 midterm. 2024 not included.", "",
           "| Measure | 2022 | 2026 | Change |","|---|---:|---:|---:|"]
    for r in metrics:
        x,y=r["2022"],r["2026"]
        c=f'{r["change"]:+.1f} pp' if r["change_type"]=="percentage points" else f'{r["change"]:+.1f}%'
        lines.append(f'| {r["measure"]} | {x} | {y} | {c} |')
    lines+=["","See CSVs in this directory for age/party/race/ethnicity/gender, daily counts, and",
            "residential-precinct changes in preference for the campus site versus other Wake sites.",
            "The precinct file uses a recorded HOME precinct, not precinct of ballot casting.",
            "It does not show the same people moving sites, prove a causal effect, or identify students.",
            "Check altered precinct boundaries, eligible-voter denominators and final canvass data",
            "before making stronger claims. 2026 file is an election-night-period snapshot.","",
            "Official original files (raw originals are NOT in Git):"]
    lines += [f'- {s["year"]}: {s["url"]}; SHA-256 {s["zip_sha256"]}; last modified {s["zip_last_modified_utc"]}' for s in summary["sources"]]
    (OUT/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"qa":summary["qa"],"metrics":metrics},indent=2))

if __name__=="__main__":main()
