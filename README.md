# 毎日クロスワード

每日一題的 10×10 日文假名填字遊戲，單字範圍 JLPT N5–N4，共 365 天題目。

網站：https://leochou39.github.io/kana-crossword/

## 檔案

| 檔案 | 用途 |
| --- | --- |
| `vocab.txt` | 單字表（讀音｜寫法｜中文意思｜級數，依詞性分區；沒寫級數的是 N5） |
| `clues.txt` | 每個單字的情境提示 |
| `examples.txt` | 每個單字的例句、中文翻譯與文法點（完成後顯示） |
| `grammar.txt` | 文法標籤的中文說明 |
| `examples_ruby.txt` | 例句的假名標注（由 `make_furigana.py` 產生） |
| `furigana_fix.txt` | 自動標注讀錯時的修正表 |
| `pairs.txt` | 自動詞／他動詞對照 |
| `generate.py` | 出題程式，讀取上面的檔案，產生 `puzzles.js` |
| `conjugate.py` | 動詞變化題（辭書形、ます形、ない形、て形、た形、可能形、意向形）的變化規則 |
| `index.html` | 網頁本體 |
| `assets/` | 連結預覽圖與網站圖示 |
| `build_site.sh` | 把網頁打包到 `docs/`，GitHub Pages 從這裡發佈 |

## 修改例句後

先重新產生假名標注（需要 SudachiPy，見 `make_furigana.py` 開頭說明），讀錯的詞寫進 `furigana_fix.txt`。

## 修改單字或提示後

```sh
python3 generate.py
./build_site.sh
```

然後把變更 commit 並 push，網站幾分鐘內就會更新。

重新出題時，今天以前已上線的題目會保持不變。新單字請加在 vocab.txt 最後面，避免影響既有題目的編號。

這個版本全部屬於「第一學期」：2026-10-13 是試玩，隔天起為第一課、第二課……，題目依玩家當地日期每天輪換，365 天後從頭開始。遊玩紀錄只存在玩家自己的瀏覽器裡。

## 英文版（AbbVie）

`abbvie/` 是一次性的英文填字遊戲（AbbVie 產品與臨床試驗用語）。改 `abbvie/words.txt` 後執行 `python3 abbvie/generate.py`（在 abbvie 資料夾內）和 `abbvie/build.sh`，網址是 https://leochou39.github.io/kana-crossword/abbvie/
