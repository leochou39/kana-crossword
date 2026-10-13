"""替例句加上假名標注，輸出 examples_ruby.txt（格式：讀音|寫法|{漢字|かな}標注後的例句）。

需要 SudachiPy（只有重新產生標注時才需要，網站本身不需要）：
    python3 -m venv venv && venv/bin/pip install sudachipy sudachidict_core
    venv/bin/python make_furigana.py
自動判讀錯的讀音，請寫進 furigana_fix.txt（格式：漢字詞|正確讀音），再重跑一次。
"""
import re
import sys

from sudachipy import dictionary, tokenizer

KANJI = r"[㐀-鿿々〆ヵヶ]"


def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def load_fixes(path="furigana_fix.txt"):
    fixes = {}
    try:
        for line in open(path, encoding="utf8"):
            line = line.strip()
            if line and not line.startswith("#"):
                w, r = line.split("|")
                fixes[w] = r
    except FileNotFoundError:
        pass
    return fixes


def align(surface, reading):
    """把讀音對到漢字部分：通い/かよい → [(通, かよ), (い, None)]"""
    parts = re.findall(rf"{KANJI}+|[^㐀-鿿々〆ヵヶ]+", surface)
    pattern = "".join("(.+?)" if re.match(KANJI, p) else f"({re.escape(kata2hira(p))})" for p in parts)
    m = re.fullmatch(pattern, reading)
    if not m:
        return [(surface, reading)]
    return [(p, g if re.match(KANJI, p) else None) for p, g in zip(parts, m.groups())]


def annotate(sentence, tok, fixes):
    out, pairs = [], []
    morphs = list(tok.tokenize(sentence, tokenizer.Tokenizer.SplitMode.C))
    i = 0
    while i < len(morphs):
        # 先試著把相鄰的詞合起來對照修正表（例如 何曜 + 日 → 何曜日）
        for n in (3, 2, 1):
            surf = "".join(m.surface() for m in morphs[i:i + n])
            if surf in fixes and i + n <= len(morphs):
                reading, used = fixes[surf], n
                break
        else:
            surf, used = morphs[i].surface(), 1
            reading = kata2hira(morphs[i].reading_form())
        if re.search(KANJI, surf):
            pairs.append((surf, reading))
            for p, r in align(surf, reading):
                out.append(f"{{{p}|{r}}}" if r else p)
        else:
            out.append(surf)
        i += used
    return "".join(out), pairs


def main():
    tok = dictionary.Dictionary(dict="core").create()
    fixes = load_fixes()
    lines, seen = [], {}
    for line in open("examples.txt", encoding="utf8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        k, w, s, _t, _g = line.split("|")
        ruby, pairs = annotate(s, tok, fixes)
        lines.append(f"{k}|{w}|{ruby}")
        for p in pairs:
            seen.setdefault(p, s)
    with open("examples_ruby.txt", "w", encoding="utf8") as f:
        f.write("# 例句假名標注（由 make_furigana.py 產生，{漢字|かな}）\n" + "\n".join(lines) + "\n")
    if "--pairs" in sys.argv:
        for (surf, r), s in sorted(seen.items()):
            print(f"{surf}|{r}|{s}")


main()
