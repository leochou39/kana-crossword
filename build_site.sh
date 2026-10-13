#!/bin/sh
# 把 index.html（頁面內容）包成完整網頁，輸出到 docs/ 給 GitHub Pages 使用
cd "$(dirname "$0")"
mkdir -p docs
{ printf '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'; cat index.html; printf '\n</body>\n</html>\n'; } > docs/index.html
cp puzzles.js docs/puzzles.js
