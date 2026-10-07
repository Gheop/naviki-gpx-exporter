#!/usr/bin/env python3
"""
Banc de mesure : alterne les variantes run par run contre le serveur mock.

Chaque variante est une révision git (ou WORKTREE pour l'arbre de travail).
Le script de la variante est copié dans un dossier isolé, sans .env, pour que
les identifiants locaux n'influencent pas la mesure.

Scénarios :
  incremental  login Selenium + pagination, 431 traces déjà présentes
  full         --token, dossier vide, 431 téléchargements

Usage :
  python bench/bench.py --scenario full --runs 10 HEAD WORKTREE
  python bench/bench.py --scenario incremental --runs 10 --json out.json HEAD
"""

import argparse
import hashlib
import json
import os
import pathlib
import platform
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mock_naviki import TOKEN, MockNaviki  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = ROOT / "bench" / "run_scenario.py"
SCRIPT = "naviki-gpx-exporter.py"


def materialize(variant, workdir):
    target = workdir / variant.replace("/", "_") / SCRIPT
    target.parent.mkdir(parents=True)
    if variant == "WORKTREE":
        shutil.copy(ROOT / SCRIPT, target)
    else:
        content = subprocess.check_output(
            ["git", "show", f"{variant}:{SCRIPT}"], cwd=ROOT
        )
        target.write_bytes(content)
    return target


def dir_digest(path):
    h = hashlib.sha256()
    for f in sorted(path.iterdir()):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest(), sum(1 for _ in path.iterdir())


def run_once(script, base_url, script_args):
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [sys.executable, str(RUNNER), str(script), base_url, "--", *script_args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout.read()
    _, status, rusage = os.wait4(proc.pid, 0)
    wall = time.perf_counter() - t0
    if os.waitstatus_to_exitcode(status) != 0:
        sys.stderr.write(output.decode(errors="replace")[-3000:])
        raise SystemExit(f"échec de {script}")
    return {
        "wall_s": wall,
        "cpu_s": rusage.ru_utime + rusage.ru_stime,
        "maxrss_mb": rusage.ru_maxrss / 1024,
    }


def summarize(values):
    ordered = sorted(values)
    p95 = ordered[max(0, round(0.95 * len(ordered)) - 1)]
    median = statistics.median(ordered)
    stdev = statistics.stdev(ordered) if len(ordered) > 1 else 0.0
    return {
        "median": round(median, 4),
        "stdev": round(stdev, 4),
        "cv_pct": round(100 * stdev / median, 1) if median else 0.0,
        "p95": round(p95, 4),
        "min": round(ordered[0], 4),
        "max": round(ordered[-1], 4),
    }


def paired_delta(base_runs, cand_runs, key, resamples=5000):
    """Écart relatif candidat/baseline apparié par run, IC bootstrap 95 %."""
    deltas = [c[key] / b[key] - 1 for b, c in zip(base_runs, cand_runs)]
    rng = random.Random(0)
    medians = sorted(
        statistics.median(rng.choices(deltas, k=len(deltas))) for _ in range(resamples)
    )
    return {
        "median_pct": round(100 * statistics.median(deltas), 2),
        "ci95_pct": [
            round(100 * medians[int(0.025 * resamples)], 2),
            round(100 * medians[int(0.975 * resamples) - 1], 2),
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("variants", nargs="+")
    parser.add_argument("--scenario", choices=["incremental", "full"], required=True)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--json")
    args = parser.parse_args()

    work = pathlib.Path(tempfile.mkdtemp(prefix="naviki-bench-"))
    scripts = {v: materialize(v, work) for v in args.variants}
    results = {v: [] for v in args.variants}
    digests = {}

    with MockNaviki() as mock:
        prefilled = work / "prefilled"
        if args.scenario == "incremental":
            prefilled.mkdir()
            run_once(
                scripts[args.variants[0]],
                mock.base_url,
                ["--token", TOKEN, "--output", str(prefilled)],
            )

        def script_args(out):
            if args.scenario == "incremental":
                return [
                    "--username",
                    "bench",
                    "--password",
                    "bench",
                    "--output",
                    str(prefilled),
                ]
            return ["--token", TOKEN, "--output", str(out)]

        for i in range(args.warmup + args.runs):
            # ordre alterné à chaque run pour répartir la dérive thermique
            order = args.variants if i % 2 == 0 else list(reversed(args.variants))
            for v in order:
                out = work / f"out-{v.replace('/', '_')}"
                shutil.rmtree(out, ignore_errors=True)
                out.mkdir()
                metrics = run_once(scripts[v], mock.base_url, script_args(out))
                if args.scenario == "full":
                    digests.setdefault(v, set()).add(dir_digest(out))
                if i >= args.warmup:
                    results[v].append(metrics)
                print(f"run {i} {v}: {metrics['wall_s']:.2f}s", file=sys.stderr)

    report = {
        "scenario": args.scenario,
        "runs": args.runs,
        "env": {
            "python": platform.python_version(),
            "kernel": platform.release(),
            "cpu": platform.processor() or platform.machine(),
            "commit": subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT
            )
            .decode()
            .strip(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "variants": {},
    }
    for v, runs in results.items():
        report["variants"][v] = {k: summarize([r[k] for r in runs]) for k in runs[0]}
        if v in digests:
            report["variants"][v]["outputs"] = sorted(
                f"{h[:16]} ({n} fichiers)" for h, n in digests[v]
            )

    if len(args.variants) == 2:
        base, cand = (results[v] for v in args.variants)
        report["delta_vs_" + args.variants[0]] = {
            k: paired_delta(base, cand, k) for k in base[0]
        }

    if args.scenario == "full":
        all_digests = set().union(*digests.values())
        report["outputs_identical"] = len(all_digests) == 1

    shutil.rmtree(work, ignore_errors=True)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json:
        pathlib.Path(args.json).write_text(text + "\n")


if __name__ == "__main__":
    main()
