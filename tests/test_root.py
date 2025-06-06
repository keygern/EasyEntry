import importlib.util
import sys
from pathlib import Path
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
spec = importlib.util.spec_from_file_location('main', ROOT / 'main.py')
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
create_app = main.create_app


def test_root_status():
    app = create_app()
    assert isinstance(app, FastAPI)




