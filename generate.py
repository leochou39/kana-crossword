"""Generate 365 daily 10x10 kana crosswords from vocab.txt -> puzzles.js"""
import datetime, json, os, re, random, sys

N = 10
DAYS = 365
ATTEMPTS = 24
POOL = 420
START = datetime.date(2026, 10, 13)
MAX_TWO = 3          # 每題最多幾個兩字短單字
COOLDOWN = {"N4": 8, "N5": 20}  # 同一個字隔幾天才能再出現（N4 較常出現）
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
        parts = line.split("|")
        kana, written, meaning = parts[:3]
        level = parts[3] if len(parts) > 3 else "N5"
        g = to_grid(kana)
        vocab.append({"k": kana, "w": written, "m": meaning, "p": pos, "g": g, "lv": level})
    return vocab


def build(rng, pool, vocab):
    grid = [[None] * N for _ in range(N)]
    used = [[[False, False] for _ in range(N)] for _ in range(N)]
    placed, used_strings, twos = [], set(), [0]

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
        if len(g) == 2:
            twos[0] += 1

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
                        if g in used_strings or (len(g) == 2 and twos[0] >= MAX_TWO):
                            continue
                        sr, sc = (r, c - p) if d == 0 else (r - p, c)
                        x = fits(g, sr, sc, d)
                        if x > 0:
                            bonus = (1.5 if vocab[vi]["lv"] == "N4" else 0) - (2.5 if len(g) == 2 else 0)
                            cands.append((x * 3 + len(g) * 0.8 + bonus + rng.random() * 2, vi, sr, sc, d))
        if not cands:
            break
        cands.sort(reverse=True)
        _, vi, r, c, d = cands[rng.randint(0, min(2, len(cands) - 1))]
        place(vi, r, c, d)

    filled = sum(1 for r in range(N) for c in range(N) if grid[r][c])
    crossings = sum(1 for r in range(N) for c in range(N) if used[r][c][0] and used[r][c][1])
    rows = sum(1 for r in range(N) if any(grid[r]))
    cols = sum(1 for c in range(N) if any(grid[r][c] for r in range(N)))
    n4 = sum(1 for vi, *_ in placed if vocab[vi]["lv"] == "N4")
    score = filled + crossings * 1.5 - (N - rows) * 8 - (N - cols) * 8 + n4 * 1.2 - twos[0] * 2
    return score, grid, placed


def main():
    vocab = load_vocab("vocab.txt")
    usable = [i for i, v in enumerate(vocab) if 2 <= len(v["g"]) <= N]
    last_used = {}
    puzzles = []
    # 已經上線（今天以前）的題目保持不變，避免玩家的進度對不上
    frozen = []
    if os.path.exists("puzzles.js"):
        old = open("puzzles.js", encoding="utf8").read()
        frozen = json.loads(re.search(r"const PUZZLES=(.*?);\n", old).group(1))
    keep = min(len(frozen), max(0, (datetime.date.today() - START).days + 1))
    for day in range(DAYS):
        if day < keep:
            puzzles.append(frozen[day])
            for vi, *_ in frozen[day]["w"]:
                last_used[vi] = day
            print(f"day {day:3d}: kept (already published)", file=sys.stderr)
            continue
        rng = random.Random(20261013 + day * 7919)
        order = sorted(usable, key=lambda i: (last_used.get(i, -999), rng.random()))
        pool = [i for i in order if day - last_used.get(i, -999) > COOLDOWN[vocab[i]["lv"]]][:POOL]
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
        n4 = sum(1 for vi, *_ in placed if vocab[vi]["lv"] == "N4")
        two = sum(1 for vi, *_ in placed if len(vocab[vi]["g"]) == 2)
        print(f"day {day:3d}: words={len(placed):2d} filled={filled} n4={n4} two={two} score={score:.0f}", file=sys.stderr)

    clues = {}
    for line in open("clues.txt", encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#"):
            k, w, c = line.split("|")
            clues[(k, w)] = c
    missing = [v["k"] + "|" + v["w"] for v in vocab if (v["k"], v["w"]) not in clues]
    if missing:
        sys.exit("clues.txt 缺少提示：" + "、".join(missing))
    examples = {}
    for line in open("examples.txt", encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#"):
            k, w, s, t, gr = line.split("|")
            examples[(k, w)] = [s, t, gr]
    missing = [v["k"] + "|" + v["w"] for v in vocab if (v["k"], v["w"]) not in examples]
    if missing:
        sys.exit("examples.txt 缺少例句：" + "、".join(missing))
    grammar = {}
    for line in open("grammar.txt", encoding="utf8"):
        line = line.strip()
        if line and not line.startswith("#"):
            k, disp = line.split("|")
            grammar[k] = disp
    missing = sorted({part for ex in examples.values() for part in ex[2].split("／") if part not in grammar})
    if missing:
        sys.exit("grammar.txt 缺少文法說明：" + "、".join(missing))
    for ex in examples.values():
        ex[2] = "／".join(grammar[part] for part in ex[2].split("／"))
    # [讀音, 寫法, 意思, 詞性, 提示, 級數, 例句, 例句翻譯, 文法]
    out_vocab = [[v["k"], v["w"], v["m"], v["p"], clues[(v["k"], v["w"])], v["lv"]] + examples[(v["k"], v["w"])] for v in vocab]
    with open("puzzles.js", "w", encoding="utf8") as f:
        f.write("const START_DATE='2026-10-13';\n")
        f.write("const VOCAB=" + json.dumps(out_vocab, ensure_ascii=False, separators=(",", ":")) + ";\n")
        f.write("const PUZZLES=" + json.dumps(puzzles, ensure_ascii=False, separators=(",", ":")) + ";\n")


main()
