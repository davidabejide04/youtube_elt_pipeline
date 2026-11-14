import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from yt_pipeline import config  # noqa: E402,F401  (loads .env)

key = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
if key:
    os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"] = config.resolve_path(key)

dbt_dir = ROOT / "dbt_project"
cmd = ["dbt", *sys.argv[1:], "--profiles-dir", str(dbt_dir), "--project-dir", str(dbt_dir)]
raise SystemExit(subprocess.run(cmd, cwd=dbt_dir).returncode)
