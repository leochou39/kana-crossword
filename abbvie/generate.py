"""Build one 12x12 English crossword from words.txt -> puzzle.js"""
import json, random, sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
ATTEMPTS = 20000
MAX_ABBR = 6
MUST = {"ABBVIE", "PIPELINE", "HUMIRA", "SKYRIZI", "RINVOQ", "IMBRUVICA", "VENCLEXTA", "QULIPTA", "LINZESS",
        "PLACEBO", "ENROLLMENT", "AUDIT", "VISIT", "FDA", "TNF", "ADC",
        "PROTOCOL", "CONSENT", "ENDPOINT", "BOTOX", "ALLERGAN"}  # 使用者指定的字
ONLY_MUST = True  # 只用指定的字出題
TOPK = 5


def load(path):
    out = []
    for line in open(path, encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#"):
            a, clue, info, cat = line.split("|")
            if len(a) <= N:
                out.append({"a": a, "clue": clue, "info": info, "cat": cat})
    return out


def build(rng, words):
    grid = [[None] * N for _ in range(N)]
    used = [[[False, False] for _ in range(N)] for _ in range(N)]
    placed, abbr = [], [0]
    names = set()

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

    def place(i, r, c, d):
        g = words[i]["a"]
        dr, dc = (0, 1) if d == 0 else (1, 0)
        for k, ch in enumerate(g):
            grid[r + dr * k][c + dc * k] = ch
            used[r + dr * k][c + dc * k][d] = True
        placed.append((i, r, c, d))
        names.add(g)
        if len(g) == 3:
            abbr[0] += 1

    first = rng.choice([i for i, w in enumerate(words) if len(w["a"]) >= 6])
    L = len(words[first]["a"])
    if rng.random() < .5:
        place(first, rng.randint(3, 8), rng.randint(0, N - L), 0)
    else:
        place(first, rng.randint(0, N - L), rng.randint(3, 8), 1)

    index = {}
    for i, w in enumerate(words):
        for p, ch in enumerate(w["a"]):
            index.setdefault(ch, []).append((i, p))
    while True:
        cands = []
        for r in range(N):
            for c in range(N):
                ch = grid[r][c]
                if not ch:
                    continue
                for d in (0, 1):
                    if used[r][c][d]:
                        continue
                    for i, p in index.get(ch, ()):
                        g = words[i]["a"]
                        if g in names or (len(g) == 3 and abbr[0] >= MAX_ABBR):
                            continue
                        sr, sc = (r, c - p) if d == 0 else (r - p, c)
                        x = fits(g, sr, sc, d)
                        if x > 0:
                            bonus = (1.5 if words[i]["cat"] in ("product", "company") else 0) + (3 if g in MUST else 0)
                            cands.append((x * 3 + len(g) * 0.7 + bonus + rng.random() * 2, i, sr, sc, d))
        if not cands:
            break
        cands.sort(reverse=True)
        _, i, r, c, d = cands[rng.randint(0, min(TOPK, len(cands) - 1))]
        place(i, r, c, d)

    filled = sum(1 for r in range(N) for c in range(N) if grid[r][c])
    crossings = sum(1 for r in range(N) for c in range(N) if used[r][c][0] and used[r][c][1])
    rows = sum(1 for r in range(N) if any(grid[r]))
    cols = sum(1 for c in range(N) if any(grid[r][c] for r in range(N)))
    cats = {words[i]["cat"] for i, *_ in placed}
    prod = sum(1 for i, *_ in placed if words[i]["cat"] == "product")
    trial = sum(1 for i, *_ in placed if words[i]["cat"] == "trial")
    score = filled + crossings * 1.5 - (N - rows) * 8 - (N - cols) * 8 + min(prod, 8) * 3 + min(trial, 8) * 2 \
        + (5 if "ABBVIE" in names else 0) + len(cats) * 2 + len(MUST & names) * 30 + len(placed) * 2
    return score, grid, placed


def main():
    words = load("words.txt")
    if ONLY_MUST:
        words = [w for w in words if w["a"] in MUST]
        missing = MUST - {w["a"] for w in words}
        if missing:
            sys.exit("words.txt 裡找不到：" + "、".join(sorted(missing)))
    rng = random.Random(20261013)
    best = None
    for _ in range(ATTEMPTS):
        res = build(rng, words)
        if best is None or res[0] > best[0]:
            best = res
    score, grid, placed = best
    out = {
        "n": N,
        "g": "".join(grid[r][c] or "#" for r in range(N) for c in range(N)),
        "w": [{"a": words[i]["a"], "clue": words[i]["clue"], "info": words[i]["info"], "cat": words[i]["cat"],
               "r": r, "c": c, "d": d} for i, r, c, d in placed],
    }
    with open("puzzle.js", "w", encoding="utf8") as f:
        f.write("const PUZZLE=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    filled = sum(ch != "#" for ch in out["g"])
    print(f"score={score:.0f} words={len(placed)} filled={filled}/{N*N}", file=sys.stderr)
    for r in range(N):
        print(" ".join(grid[r][c] or "." for c in range(N)), file=sys.stderr)
    print(", ".join(w["a"] for w in out["w"]), file=sys.stderr)


if __name__ == "__main__":
    main()
