# 毎日クロスワード

每日一題的 10×10 日文假名填字遊戲，單字範圍 JLPT N5–N4，共 365 天題目。

網站：https://leochou39.github.io/kana-crossword/

## 檔案

| 檔案 | 用途 |
| --- | --- |
| `vocab.txt` | 單字表（讀音｜寫法｜中文意思，依詞性分區） |
| `clues.txt` | 每個單字的情境提示 |
| `generate.py` | 出題程式，讀取上面兩個檔案，產生 `puzzles.js` |
| `index.html` | 網頁本體 |
| `build_site.sh` | 把網頁打包到 `docs/`，GitHub Pages 從這裡發佈 |

## 修改單字或提示後

```sh
python3 generate.py
./build_site.sh
```

然後把變更 commit 並 push，網站幾分鐘內就會更新。

第 1 期是 2026-10-13，題目依玩家當地日期每天輪換，365 天後從頭開始。遊玩紀錄只存在玩家自己的瀏覽器裡。
