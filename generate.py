"""Generate 365 daily 10x10 kana crosswords from vocab.txt -> puzzles.js"""
import json, random, sys

N = 10
DAYS = 365
ATTEMPTS = 24
POOL = 420
SMALL = str.maketrans("ぁぃぅぇぉっゃゅょゎ", "あいうえおつやゆよわ")


def to_grid(kana):
    out = []
    for ch in kana:
        o = ord(ch)
        if 0x30A1 <= o <= 0x30F6:  # katakana -> hiragana
            ch = chr(o - 0x60)
        out.append(ch)
    return "".join(out).translate(SMALL)


def load_vocab(path):
    vocab, pos = [], ""
    for line in open(path, encoding="utf8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            pos = line[1:]
            continue
        kana, written, meaning = line.split("|")
        g = to_grid(kana)
        vocab.append({"k": kana, "w": written, "m": meaning, "p": pos, "g": g})
    return vocab


def build(rng, pool, vocab):
    grid = [[None] * N for _ in range(N)]
    used = [[[False, False] for _ in range(N)] for _ in range(N)]
    placed, used_strings = [], set()

    def fits(g, r, c, d):
        dr, dc = (0, 1) if d == 0 else (1, 0)
        L = len(g)
        er, ec = r + dr * (L - 1), c + dc * (L - 1)
        if r < 0 or c < 0 or er >= N or ec >= N:
            return -1
        br, bc = r - dr, c - dc
        if 0 <= br and 0 <= bc and grid[br][bc]:
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
        if cross == L:
            return -1
        return cross

    def place(vi, r, c, d):
        g = vocab[vi]["g"]
        dr, dc = (0, 1) if d == 0 else (1, 0)
        for i, ch in enumerate(g):
            grid[r + dr * i][c + dc * i] = ch
            used[r + dr * i][c + dc * i][d] = True
        placed.append((vi, r, c, d))
        used_strings.add(g)

    index = {}
    for vi in pool:
        for p, ch in enumerate(vocab[vi]["g"]):
            index.setdefault(ch, []).append((vi, p))

    starters = [vi for vi in pool if 5 <= len(vocab[vi]["g"]) <= 8]
    vi = rng.choice(starters)
    L = len(vocab[vi]["g"])
    d = rng.randint(0, 1)
    a, b = rng.randint(2, 7), rng.randint(0, N - L)
    place(vi, a, b, 0) if d == 0 else place(vi, b, a, 1)

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
                    for vi, p in index.get(ch, ()):
                        g = vocab[vi]["g"]
                        if g in used_strings:
                            continue
                        sr, sc = (r, c - p) if d == 0 else (r - p, c)
                        x = fits(g, sr, sc, d)
                        if x > 0:
                            cands.append((x * 3 + len(g) * 0.6 + rng.random() * 2, vi, sr, sc, d))
        if not cands:
            break
        cands.sort(reverse=True)
        _, vi, r, c, d = cands[rng.randint(0, min(2, len(cands) - 1))]
        place(vi, r, c, d)

    filled = sum(1 for r in range(N) for c in range(N) if grid[r][c])
    crossings = sum(1 for r in range(N) for c in range(N) if used[r][c][0] and used[r][c][1])
    rows = sum(1 for r in range(N) if any(grid[r]))
    cols = sum(1 for c in range(N) if any(grid[r][c] for r in range(N)))
    score = filled + crossings * 1.5 - (N - rows) * 8 - (N - cols) * 8
    return score, grid, placed


def main():
    vocab = load_vocab("vocab.txt")
    usable = [i for i, v in enumerate(vocab) if 2 <= len(v["g"]) <= N]
    last_used = {}
    puzzles = []
    for day in range(DAYS):
        rng = random.Random(20261013 + day * 7919)
        order = sorted(usable, key=lambda i: (last_used.get(i, -999), rng.random()))
        pool = [i for i in order if day - last_used.get(i, -999) > 10][:POOL]
        best = None
        for _ in range(ATTEMPTS):
            res = build(rng, pool, vocab)
            if best is None or res[0] > best[0]:
                best = res
        score, grid, placed = best
        for vi, *_ in placed:
            last_used[vi] = day
        puzzles.append({
            "g": "".join(grid[r][c] or "#" for r in range(N) for c in range(N)),
            "w": [list(p) for p in placed],
        })
        filled = sum(ch != "#" for ch in puzzles[-1]["g"])
        print(f"day {day:3d}: words={len(placed):2d} filled={filled} score={score:.0f}", file=sys.stderr)

    clues = {}
    for line in open("clues.txt", encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#"):
            k, w, c = line.split("|")
            clues[(k, w)] = c
    missing = [v["k"] + "|" + v["w"] for v in vocab if (v["k"], v["w"]) not in clues]
    if missing:
        sys.exit("clues.txt 缺少提示：" + "、".join(missing))
    out_vocab = [[v["k"], v["w"], v["m"], v["p"], clues[(v["k"], v["w"])]] for v in vocab]
    with open("puzzles.js", "w", encoding="utf8") as f:
        f.write("const START_DATE='2026-10-13';\n")
        f.write("const VOCAB=" + json.dumps(out_vocab, ensure_ascii=False, separators=(",", ":")) + ";\n")
        f.write("const PUZZLES=" + json.dumps(puzzles, ensure_ascii=False, separators=(",", ":")) + ";\n")


main()
