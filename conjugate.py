"""動詞變化：從單字表的動詞自動產生辭書形、ます形、ない形、て形、た形、可能形、意向形的題目。"""

# 不出變化題的動詞（敬語、片語、ある 等不規則或不適合的）
SKIP = {
    "ある", "いらっしゃる", "めしあがる", "ごらんになる", "もうす", "まいる", "いたす", "おっしゃる",
    "くださる", "いただく", "さしあげる", "はいけんする", "うかがう", "きをつける", "やくにたつ", "きがつく",
}
# 看起來像る動詞、其實是五段動詞的字（用「讀音|寫法」分辨同音字）
GODAN_RU = {"かえる|帰る", "はいる|入る", "はしる|走る", "しる|知る", "きる|切る", "すべる|滑る", "へる|減る"}
# 非意志動詞：不出可能形、意向形
NONVOL = {
    "わかる", "できる", "みえる", "きこえる", "ふる", "さく", "こまる", "こわれる", "われる", "おちる", "ぬれる",
    "かわく", "ひえる", "こむ", "すく", "たりる", "のこる", "きまる", "ふえる", "へる", "あがる", "さがる",
    "はじまる", "おわる", "とまる", "しまる", "あく", "きえる", "ひかる", "みつかる", "なおる", "うまれる",
    "しぬ", "かわる", "すぎる", "にあう", "なる", "つかれる", "よごれる", "まにあう", "なれる", "ふく", "いる",
    "くれる", "しる", "わすれる", "まける", "ふとる",
}

ROWS = {  # 五段動詞詞尾 → (あ段, い段, え段, お段)
    "う": "わいえお", "く": "かきけこ", "ぐ": "がぎげご", "す": "さしせそ", "つ": "たちてと",
    "ぬ": "なにねの", "ぶ": "ばびべぼ", "む": "まみめも", "る": "らりれろ",
}
TE = {"う": "って", "つ": "って", "る": "って", "む": "んで", "ぶ": "んで", "ぬ": "んで", "く": "いて", "ぐ": "いで", "す": "して"}
I_ROW = set("いきぎしじちぢにひびぴみりゐ")
E_ROW = set("えけげせぜてでねへべぺめれゑ")

# 形：(題目用名稱, 卡片上的意思後綴, 文法說明, 級數)
FORMS = [
    ("辭書形", "（原形）", "辭書形（原形）", "N5"),
    ("ます形", "（禮貌形）", "ます形（禮貌說法）", "N5"),
    ("ない形", "（否定）", "ない形（不…）", "N5"),
    ("て形", "（て形）", "て形（連接動作、請求、進行）", "N5"),
    ("た形", "（過去）", "た形（…了；過去）", "N5"),
    ("可能形", "（能…）", "可能形（能…；會…）", "N4"),
    ("意向形", "（…吧）", "意向形（…吧；打算…）", "N4"),
]


def verb_group(kana, written):
    if kana == "する" or kana.endswith("する"):
        return "suru"
    if kana == "くる":
        return "kuru"
    if kana.endswith("る") and len(kana) >= 2 and (kana[-2] in I_ROW or kana[-2] in E_ROW) \
            and f"{kana}|{written}" not in GODAN_RU:
        return "ichidan"
    return "godan"


def inflect(word, group, form, base_kana):
    """把 word（讀音或寫法）變成指定形。word 的詞尾假名必須和讀音一致。"""
    if group == "suru":
        stem = word[:-2]
        return stem + {"辭書形": "する", "ます形": "します", "ない形": "しない", "て形": "して",
                       "た形": "した", "可能形": "できる", "意向形": "しよう"}[form]
    if group == "kuru":
        if word == "来る":
            return {"辭書形": "来る", "ます形": "来ます", "ない形": "来ない", "て形": "来て",
                    "た形": "来た", "可能形": "来られる", "意向形": "来よう"}[form]
        return {"辭書形": "くる", "ます形": "きます", "ない形": "こない", "て形": "きて",
                "た形": "きた", "可能形": "こられる", "意向形": "こよう"}[form]
    if group == "ichidan":
        stem = word[:-1]
        return stem + {"辭書形": "る", "ます形": "ます", "ない形": "ない", "て形": "て",
                       "た形": "た", "可能形": "られる", "意向形": "よう"}[form]
    stem, end = word[:-1], word[-1]
    a, i, e, o = ROWS[end]
    if form == "辭書形":
        return word
    if form == "ます形":
        return stem + i + "ます"
    if form == "ない形":
        return stem + a + "ない"
    te = "って" if base_kana == "いく" else TE[end]
    if form == "て形":
        return stem + te
    if form == "た形":
        return stem + te[:-1] + ("だ" if te.endswith("で") else "た")
    if form == "可能形":
        return stem + e + "る"
    if form == "意向形":
        return stem + o + "う"
    raise ValueError(form)


def conjugations(vocab):
    """vocab: list of dict(k, w, m, p, lv)。回傳變化題的 list（不含原本的單字）。"""
    out = []
    for v in vocab:
        if v["p"] != "動詞" or v["k"] in SKIP:
            continue
        group = verb_group(v["k"], v["w"])
        base_label = v["w"]
        masu_label = inflect(v["w"], group, "ます形", v["k"])
        for form, suffix, gram, lv in FORMS:
            if form in ("可能形", "意向形") and v["k"] in NONVOL:
                continue
            kana = inflect(v["k"], group, form, v["k"])
            written = inflect(v["w"], group, form, v["k"])
            clue = f"「{masu_label}」的辭書形" if form == "辭書形" else f"「{base_label}」的{form}"
            out.append({
                "k": kana, "w": written, "m": f"{v['m']}・{form}", "p": "動詞變化", "lv": lv,
                "clue": clue, "form_gram": gram, "base": (v["k"], v["w"]), "form": form,
            })
    return out


if __name__ == "__main__":
    tests = [("たべる", "食べる"), ("いく", "行く"), ("かえる", "帰る"), ("かえる", "変える"), ("のむ", "飲む"),
             ("まつ", "待つ"), ("およぐ", "泳ぐ"), ("はなす", "話す"), ("かう", "買う"), ("くる", "来る"),
             ("する", "する"), ("しぬ", "死ぬ"), ("きる", "切る"), ("きる", "着る"), ("ひっこす", "引っ越す")]
    for k, w in tests:
        g = verb_group(k, w)
        print(k, w, g, " ".join(f"{inflect(k, g, f, k)}/{inflect(w, g, f, k)}" for f, *_ in FORMS))
