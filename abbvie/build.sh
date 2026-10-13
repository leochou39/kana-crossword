#!/bin/sh
# 把 index.html 包成完整網頁，輸出到 ../docs/abbvie/（網址：https://leochou39.github.io/kana-crossword/abbvie/）
cd "$(dirname "$0")"
OUT=../docs/abbvie
mkdir -p "$OUT"
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="An unofficial crossword about AbbVie products and clinical-trial terms.">\n'
  printf '<meta name="theme-color" content="#3F3DB8">\n'
  printf '<meta property="og:title" content="AbbVie Crossword">\n'
  printf '<meta property="og:description" content="Products, pipeline &amp; clinical-trial terms in one 12x12 crossword.">\n'
  printf '</head>\n<body>\n'
  sed "s|src=\"puzzle.js\"|src=\"puzzle.js?v=$(md5 -q puzzle.js | cut -c1-8)\"|" index.html
  printf '\n</body>\n</html>\n'
} > "$OUT/index.html"
cp puzzle.js "$OUT/puzzle.js"
