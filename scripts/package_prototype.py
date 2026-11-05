"""Copy the verified research prototype build to its existing root route."""
import argparse
from pathlib import Path
from package_article import ROOT,package

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dist',type=Path,required=True)
args=parser.parse_args()
package(args.dist,ROOT)
