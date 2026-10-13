"""Backtracking search that tries to fit EVERY chosen word into an N x N grid -> puzzle.js

用法：python3 fit_all.py 13   （可以加上秒數上限：python3 fit_all.py 13 120）
"""
import json, random, sys, time

from generate import MUST, load

N = int(sys.argv[1]) if len(sys.argv) > 1 else 13
LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 90


def solve(words, rng, deadline):
    grid = [[None] * N for _ in range(N)]
    used = [[[False, False] for _ in range(N)] for _ in range(N)]
    placed = []

    def fits(g, r, c, d):
        dr, dc = (0, 1) if d == 0 else (1, 0)
        L = len(g)
        er, ec = r + dr * (L - 1), c + dc * (L - 1)
        if r < 0 or c < 0 or er >= N or ec >= N:
            return -1
        br, bc = r - dr, c - dc
        if br >= 0 and bc >= 0 and grid[br][bc]:
            return -1
        ar, ac = er + dr, ec + dc
        if ar < N and ac < N and grid[ar][ac]:
            return -1
        cross = 0
        for i, ch in enumerate(g):
            rr, cc = r + dr * i, c + dc * i
            cell = grid[rr][cc]
            if cell:
                if cell != ch or used[rr][cc][d]:
                    return -1
                cross += 1
            else:
                for pr, pc in ((rr + dc, cc + dr), (rr - dc, cc - dr)):
                    if 0 <= pr < N and 0 <= pc < N and grid[pr][pc]:
                        return -1
        return -1 if cross == L else cross

    def put(g, r, c, d, on):
        dr, dc = (0, 1) if d == 0 else (1, 0)
        changed = []
        for i, ch in enumerate(g):
            rr, cc = r + dr * i, c + dc * i
            if on:
                if grid[rr][cc] is None:
                    changed.append((rr, cc))
                grid[rr][cc] = ch
                used[rr][cc][d] = True
        return changed

    def options(g):
        opts = []
        for r in range(N):
            for c in range(N):
                for d in (0, 1):
                    x = fits(g, r, c, d)
                    if x > 0:
                        opts.append((x + rng.random(), r, c, d))
        opts.sort(reverse=True)
        return opts[:6]

    remaining = sorted(range(len(words)), key=lambda i: -len(words[i]["a"]))

    def dfs(rest):
        if time.time() > deadline:
            return False
        if not rest:
            return True
        # 先放「可以放的位置最少」的字，比較不會卡住
        best = None
        for i in rest:
            o = options(words[i]["a"])
            if not o:
                return False
            if best is None or len(o) < len(best[1]):
                best = (i, o)
        i, opts = best
        g = words[i]["a"]
        for _, r, c, d in opts:
            changed = put(g, r, c, d, True)
            placed.append((i, r, c, d))
            if dfs([j for j in rest if j != i]):
                return True
            placed.pop()
            dr, dc = (0, 1) if d == 0 else (1, 0)
            for k in range(len(g)):
                used[r + dr * k][c + dc * k][d] = False
            for rr, cc in changed:
                grid[rr][cc] = None
        return False

    first = remaining[0]
    g = words[first]["a"]
    d = rng.randint(0, 1)
    off = rng.randint(0, N - len(g))
    mid = rng.randint(N // 2 - 2, N // 2 + 1)
    r, c = (mid, off) if d == 0 else (off, mid)
    put(g, r, c, d, True)
    placed.append((first, r, c, d))
    ok = dfs(remaining[1:])
    return ok, grid, placed


def main():
    words = [w for w in load("words.txt") if w["a"] in MUST]
    deadline_total = time.time() + LIMIT
    tries = 0
    while time.time() < deadline_total:
        tries += 1
        rng = random.Random(tries)
        ok, grid, placed = solve(words, rng, min(deadline_total, time.time() + 8))
        if ok:
            out = {"n": N, "g": "".join(grid[r][c] or "#" for r in range(N) for c in range(N)),
                   "w": [{"a": words[i]["a"], "clue": words[i]["clue"], "info": words[i]["info"], "cat": words[i]["cat"],
                          "r": r, "c": c, "d": d} for i, r, c, d in placed]}
            with open("puzzle.js", "w", encoding="utf8") as f:
                f.write("const PUZZLE=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
            print(f"N={N}: all {len(words)} words fit (try {tries})")
            for r in range(N):
                print(" ".join(grid[r][c] or "." for c in range(N)))
            return
    print(f"N={N}: could not fit all {len(words)} words in {LIMIT:.0f}s ({tries} tries)")
    sys.exit(1)


main()
