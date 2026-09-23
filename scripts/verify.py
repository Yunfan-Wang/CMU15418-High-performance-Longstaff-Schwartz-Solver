"""Executable contract checks; optional independent CUDA/CPU comparison."""

import argparse
import json
from pathlib import Path
import subprocess


def output(binary, *args):
    result = subprocess.run(
        [str(binary.resolve()), *args], text=True, capture_output=True, timeout=120
    )
    return result


def check(binary):
    for args in [
        ("--paths", "0"),
        ("--paths", "-1"),
        ("--steps", "0"),
        ("--deg", "8"),
        ("--sigma", "nan"),
        ("--paths", "10000000000"),
        ("--unknown", "1"),
        ("--K",),
    ]:
        assert output(binary, *args).returncode != 0, args
    base = output(binary, "--put", "--paths", "50000", "--steps", "50", "--json")
    assert base.returncode == 0, base.stderr
    put = json.loads(base.stdout)["price"]
    assert 5.5 < put < 6.7, put
    deterministic = output(binary, "--put", "--S0", "80", "--sigma", "0", "--json")
    assert deterministic.returncode == 0, deterministic.stderr
    assert abs(json.loads(deterministic.stdout)["price"] - 20) < 1e-9
    call = output(binary, "--call", "--paths", "50000", "--json")
    assert call.returncode == 0, call.stderr
    assert 9.8 < json.loads(call.stdout)["price"] < 11.1
    tiny = output(binary, "--put", "--paths", "8", "--deg", "7", "--json")
    assert tiny.returncode == 0, tiny.stderr
    assert 0 <= json.loads(tiny.stdout)["price"] <= 100
    repeated = output(
        binary, "--paths", "10000", "--warmup", "1", "--repeat", "2", "--json"
    )
    assert repeated.returncode == 0, repeated.stderr
    assert len(repeated.stdout.splitlines()) == 2
    print(
        f"{binary.name}: input rejection, reference ranges, deterministic limit, singular regression, repeated output passed"
    )
    return put


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", required=True, type=Path)
    parser.add_argument("--cuda", type=Path)
    args = parser.parse_args()
    cpu = check(args.cpu)
    if args.cuda:
        gpu = check(args.cuda)
        assert abs(cpu - gpu) < 0.4, (cpu, gpu)
        print("CPU/CUDA price difference within 0.4 tolerance; RNGs differ.")
