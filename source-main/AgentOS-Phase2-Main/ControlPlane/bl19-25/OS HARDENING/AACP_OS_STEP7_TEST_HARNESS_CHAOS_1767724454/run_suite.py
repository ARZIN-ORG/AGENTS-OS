from __future__ import annotations
import argparse
import json
import os
import time

from suite.context import make_ctx
from suite.tests import TESTS
from lib.assertions import TestFail

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to json config")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    ctx = make_ctx(cfg)

    os.makedirs("reports", exist_ok=True)
    started = time.time()

    results = []
    passed = 0
    for name, fn in TESTS:
        t0 = time.time()
        try:
            fn(ctx)
            ok = True
            err = None
            passed += 1
        except TestFail as e:
            ok = False
            err = str(e)
        except Exception as e:
            ok = False
            err = f"UNEXPECTED: {e}"
        dt = int((time.time() - t0) * 1000)
        results.append({"name": name, "ok": ok, "ms": dt, "error": err})

    total_ms = int((time.time() - started) * 1000)
    report = {
        "env": cfg.get("env"),
        "total_ms": total_ms,
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
        "timestamp_ms": int(time.time() * 1000),
    }

    with open("reports/latest.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append(f"ENV={report['env']} total_ms={report['total_ms']} passed={report['passed']} failed={report['failed']}")
    for r in results:
        mark = "OK" if r["ok"] else "FAIL"
        line = f"{mark:4} {r['name']:<28} {r['ms']:>5}ms"
        if r["error"]:
            line += f" | {r['error']}"
        lines.append(line)

    with open("reports/latest.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
