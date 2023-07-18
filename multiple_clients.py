import argparse
import subprocess
import multiprocessing


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--participants", type=int, default=5)
    return parser.parse_args()


def worker(x: None):
    result = subprocess.call("python3 client.py", shell=True)
    return result


def main():
    n: int = parse().participants

    print(f"Initializating {n} participants")
    with multiprocessing.Pool(n) as p:
        p.map(worker, [None] * n)


if __name__ == "__main__":
    main()
