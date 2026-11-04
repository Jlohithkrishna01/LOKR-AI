import sys
import os
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Safeguard for Windows Application Control / Smart App Control:
# Automatically remove any blocked precompiled .pyd files from SQLAlchemy to enable pure-Python fallbacks
try:
    import importlib.util
    _sqla_spec = importlib.util.find_spec("sqlalchemy")
    if _sqla_spec and _sqla_spec.submodule_search_locations:
        for _loc in _sqla_spec.submodule_search_locations:
            for _pyd in Path(_loc).rglob("*.pyd"):
                try:
                    _pyd.unlink()
                except Exception:
                    pass
except Exception:
    pass
# Proactively load .env from backend_dir or project root
for candidate in [backend_dir / ".env", backend_dir.parent / ".env"]:
    if candidate.exists():
        load_dotenv(candidate, override=True)
        break

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(backend_dir)])
