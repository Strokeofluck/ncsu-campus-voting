"""Validate the current focused reference page."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('test_article_references.py')),run_name='__main__')
