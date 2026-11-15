# カットとカットセット

[PDFを読む](cuts-and-cutsets.pdf)

原稿は `cuts-and-cutsets.typ`、図と生成処理は `figures/` にあります。

リポジトリ直下から、TypstでPDFを生成します。

```sh
typst compile cuts-and-cutsets/cuts-and-cutsets.typ cuts-and-cutsets/cuts-and-cutsets.pdf
```

図を変更した場合は、Python 3とTypstで図を再生成してからコンパイルします。

```sh
python3 cuts-and-cutsets/figures/graphs.py
```
