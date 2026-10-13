#!/bin/sh
# 把 index.html（頁面內容）包成完整網頁，輸出到 docs/ 給 GitHub Pages 使用
cd "$(dirname "$0")"
SITE="https://leochou39.github.io/kana-crossword/"
DESC="每天一題 10×10 日文假名填字遊戲，用生活情境提示複習 JLPT N5–N4 單字，完成後附例句與文法。"
mkdir -p docs
{
  printf '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="%s">\n' "$DESC"
  printf '<meta name="theme-color" content="#2E7A4C">\n'
  printf '<meta property="og:type" content="website">\n'
  printf '<meta property="og:site_name" content="毎日クロスワード">\n'
  printf '<meta property="og:title" content="毎日クロスワード｜N5–N4 日文假名填字">\n'
  printf '<meta property="og:description" content="%s">\n' "$DESC"
  printf '<meta property="og:url" content="%s">\n' "$SITE"
  printf '<meta property="og:image" content="%sog.png">\n' "$SITE"
  printf '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
  printf '<meta name="twitter:card" content="summary_large_image">\n'
  printf '<link rel="icon" type="image/png" href="apple-touch-icon.png">\n'
  printf '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
  printf '</head>\n<body>\n'
  cat index.html
  printf '\n</body>\n</html>\n'
} > docs/index.html
cp puzzles.js docs/puzzles.js
cp assets/og.png assets/apple-touch-icon.png docs/
