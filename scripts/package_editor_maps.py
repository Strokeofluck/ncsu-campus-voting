"""Package the verified maps-and-charts editor preview."""
import argparse
from pathlib import Path
from package_article import ROOT,package

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dist',type=Path,required=True)
package(parser.parse_args().dist,ROOT/'editor-maps')
