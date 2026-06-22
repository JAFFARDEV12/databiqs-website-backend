"""Vercel entrypoint — exposes the Flask app from databiqs-website.py."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_module_path = Path(__file__).resolve().parent / "databiqs-website.py"
_spec = spec_from_file_location("databiqs_website", _module_path)
_module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)

app = _module.app
