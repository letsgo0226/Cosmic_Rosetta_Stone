#!/usr/bin/env python3
"""Read-only-by-default verified research-machine loader (TM-009)."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "deployment/research_machine_loader.json"

def check():
    profile = json.loads(CONFIG.read_text(encoding="utf-8"))
    paths = []
    for key in ("entrypoint", "archive"):
        relative = Path(profile[key])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid path in research profile")
        file = (ROOT / relative).resolve()
        if ROOT not in file.parents:
            raise ValueError("Research entry is outside repository")
        blob = file.read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        if len(blob) != profile["size_bytes"] or digest != profile["source_blob_sha1"]:
            raise ValueError("SHA/size mismatch: refusing research entry")
        paths.append(file)
    if paths[0].read_bytes() != paths[1].read_bytes():
        raise ValueError("Archive is different from loadable copy")
    return profile, paths[0]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="store_true", help="Run a SHA-verified local research script explicitly")
    args, rest = ap.parse_known_args()
    if rest and not args.run:
        ap.error("Parameter arguments require --run")
    profile, file = check()
    if not args.run:
        print(json.dumps({"verified": True, "id": profile["registry_id"],
                          "name": profile["display_name_zh"],
                          "entrypoint": profile["entrypoint"],
                          "status": profile["status"],
                          "execution": "not_run"}, ensure_ascii=False))
        return
    result = subprocess.run(["bash", str(file), *rest], cwd=str(ROOT), timeout=30)
    raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
