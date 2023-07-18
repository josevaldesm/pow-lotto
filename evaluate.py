import json
import time
import subprocess

from tqdm import tqdm

def worker(n: int):
    result = subprocess.call("python3 multiple_clients.py --participants={n}", shell=True)
    return result

def main():
    max_k = 20
    players = [1, 5, 10, 16]
    iterations = [{ "k": k, "n": n } for k in range(1, max_k + 1) for n in players]
    results = []
    for kw in (pbar := tqdm(iterations)):
        k = kw["k"]
        n = kw["n"]
        pbar.set_description(f"Simulating lottery with k={k} and n={n}")
        p = subprocess.Popen(f"python3 main.py --difficulty={k} --max-rounds=10 --evaluate", shell=True, stdout=subprocess.PIPE)
        time.sleep(3) # Wait until server is setted
        subprocess.call(f"python3 multiple_clients.py --participants={n}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out, _ = p.communicate()
        text = json.loads("\n".join(out.decode().split("\n")[4:]))
        results.append({"k": k, "n": n, "data": text})
        with open("results.json", "w") as f:
            json.dump(results, f, indent=4)
if __name__ == "__main__":
    main()
