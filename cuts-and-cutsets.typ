#import "@preview/ctheorems:2.0.0": *
#show: thm-rules.with(qed-symbol: $square$)

#set page(paper: "a4", margin: (x: 28mm, y: 26mm), numbering: "1")
#set text(font: ("Hiragino Sans", "Libertinus Serif"), size: 10.5pt, lang: "ja")
#show regex("[0-9]+"): set text(font: "Arial")
#set par(leading: 0.85em, spacing: 1.35em)
#set heading(numbering: "1.")
#show heading.where(level: 1): it => block(
  width: 100%,
  inset: (bottom: 9pt),
  stroke: (bottom: 0.8pt + rgb("606060")),
  below: 1.2em,
)[#it]
#show heading.where(level: 2): it => block(
  width: 100%,
  inset: (bottom: 6pt),
  stroke: (bottom: 0.4pt + rgb("B0B0B0")),
  above: 1.4em,
  below: 0.9em,
)[#it]

#let blue = rgb("175CD3")
#let intuition(body) = block(
  inset: (left: 12pt, top: 7pt, bottom: 9pt),
  stroke: (left: 2pt + blue),
  text(fill: blue)[#body],
)

// 環境全体を囲み、番号と参照は ctheorems に任せる。
#let framed = thm.with(
  base: none,
  numbering: "1",
  fmt: thm-fmt-block.with(
    body-fmt: body => body,
    separator: [#linebreak()],
  ),
  breakable: false,
  stroke: 0.6pt + rgb("9CA3AF"),
  inset: (x: 14pt, y: 11pt),
  above: 12pt,
  below: 12pt,
)
#let definition = framed.with(supplement: "定義", counter: "definition")
#let theorem = framed.with(supplement: "定理", counter: "theorem")
#let lemma = framed.with(supplement: "補題", counter: "lemma")
#let remark = framed.with(supplement: "注意", counter: "remark")
#let proof-env = proof.with(
  supplement: "証明",
  title-fmt: strong,
  separator: [．],
  above: 7pt,
  below: 7pt,
)

#let proof(body) = {
  v(10pt)
  proof-env(body)
}

= カットとカットセット

本節では、drken の記事#footnote[
  drken「燃やす埋める問題（最小カット問題）の考え方を総整理！ 前編」第1章、特に1-2・1-3節（Qiita）。
  #link("https://qiita.com/drken/items/52aafd8c073b37749539")[#underline(stroke: 0.35pt + rgb("606060"), offset: 2pt)[#text(font: "Menlo", size: 0.9em)[https://qiita.com/drken/items/52aafd8c073b37749539]]]
]を手掛かりに、カットと辺の削除の関係を整理します。次の2つは、似ていますが同じではありません。

- 頂点の分け方から決まるカットセット
- 取り除くと到達できなくなる辺の集まり

この違いを、数学屋にとって分かりやすい形で整理します。

以下では、頂点集合 $V$ と辺集合 $E$ からなる有向グラフ $G = (V, E)$ を考え、異なる頂点 $s, t in V$ を固定します。

== 頂点と辺による切断の表現

カットとカットセットが、それぞれ何を表すのかを明確にします。

#definition[
頂点集合 $S subset.eq V$ が*カット*（cut）であるとは、
$ s in S, quad t in.not S $
が成立することをいいます。

#intuition[カットは、すべての頂点を $s$ のいる側と $t$ のいる側に分けることに対応します。#linebreak()
2つの側をつなぐ辺のところでグラフを切り分ける、と捉えると「カット」という名前をイメージしやすいです。]
] <def-cut>

$S$ に含まれない頂点の集まり $V backslash S$ を $T$ と書き、両側を組にして $(S, T)$ と表す流儀もあります。本節では、$s$ 側の頂点集合 $S$ でカットを表します。

#definition[
辺集合 $E' subset.eq E$ に対し、$s$ からの*到達可能集合*（reachable set）を
$ "Reach"_(s)(E') := {v in V | s arrow.squiggly v " in " (V, E')} $
と定めます#footnote[$"Reach"_(s)$ は標準的な記号ではなく、このノート内でのみ用いる記法です。]。ただし、$s arrow.squiggly v " in " (V, E')$ は、辺集合 $E'$ の辺だけを使う有向パスで $s$ から $v$ へ到達できることを表します。長さ $0$ のパスも認めます。

#intuition[残っている道だけを使って、$s$ からどこまで行けるかを表します。矢印の逆向きには進めません。]
] <def-reach>

#definition[
頂点集合 $S subset.eq V$ に対し、$S$ の*出辺境界*（outgoing edge boundary）を
$ delta^+(S) := {(u,v) in E | u in S, v in.not S} $
と定めます。

#intuition[$S$ を一つの区域と見ると、その内側から外側へ境目を越える道に当たります。入ってくる向きの道は数えません。]
] <def-boundary>

#definition[
辺集合 $F subset.eq E$ が*カットセット*（cutset）であるとは、あるカット $S$ について
$ F = delta^+(S) $
と表せることをいいます。

#intuition[2つのグループの間にある、$s$ 側から $t$ 側への通り道をひとまとめにしたものです。]
] <def-cutset>

== カットセットの削除と到達不能性

頂点集合を分けることと、辺を取り除いて到達できなくすることの関係を確かめます。

#theorem[
辺集合 $F subset.eq E$ について、次の2つは同値です。

- $F$ を取り除くと、$s$ から $t$ へ到達できなくなります。
- あるカット $S$ のカットセットが $F$ に含まれます。すなわち、$delta^+(S) subset.eq F$ が成立します。
] <thm-cutset>

この同値性を示すため、まずカットセットを取り除いたときの性質を確認し、次に到達を妨げる辺集合からカットセットを見つけます。

#lemma[
頂点集合 $S$ がカットならば、そのカットセット $delta^+(S)$ を取り除くと、$s$ から $t$ へ到達できなくなります。すなわち、
$ t in.not "Reach"_(s)(E backslash delta^+(S)) $
が成立します。

#proof[
$s$ から $t$ への任意の有向パスは、$S$ 内から始まり $S$ 外で終わるため、少なくとも一度 $S$ から外へ出ます。その際に通る辺は $delta^+(S)$ に属します。したがって、それらの辺をすべて除くと $s$ から $t$ へのパスは存在しません。
]
] <lem-boundary>

#remark[
辺集合 $F subset.eq E$ を取り除くと $s$ から $t$ へ到達できなくなっても、$F$ 自体がカットセットであるとは限りません。つまり、@thm-cutset の包含関係は、必ずしも等号になるわけではありません。

例えば、頂点 $s, a, t$ と辺 $e_1 = (s,a)$、$e_2 = (a,t)$ からなるグラフで、$F = {e_1, e_2}$ とします。$F$ を取り除くと $s$ から $t$ へ到達できなくなりますが、カットは $S = {s}$ と $S = {s,a}$ の2つだけで、それぞれ
$ delta^+({s}) = {e_1}, quad delta^+({s,a}) = {e_2} $
となります。したがって $F = delta^+(S)$ となるカットはなく、$F$ はカットセットではありません。

] <rem-extra-edges>

#lemma[
辺集合 $F subset.eq E$ を取り除くと $s$ から $t$ へ到達できなくなるとし、
$ R := "Reach"_(s)(E backslash F) $
とおきます。このとき $R$ はカットであり、
$ delta^+(R) subset.eq F $
が成立します。

#intuition[辺をあちこち取り除いて $s$ から $t$ へ行けなくした場合も、取り除いた辺を見直すと、あるカットセットが丸ごと含まれています。]

#proof[
長さ $0$ のパスを認めるので $s in R$ です。また、仮定より $t in.not R$ です。よって $R$ はカットです。

任意の辺 $(u,v) in delta^+(R)$ をとります。もし $(u,v) in.not F$ なら、$u in R$ であることと辺 $(u,v) in E backslash F$ から $v in R$ が従います。しかしこれは $v in.not R$ に矛盾します。ゆえに $delta^+(R) subset.eq F$ が成り立ちます。
]

#intuition[残った道で $s$ から行ける場所と、行けない場所に分けてみます。行ける側から境目を越える道が残っていれば、その先にも行けるはずです。だから、そのような道はすべて取り除かれていたと分かります。]
] <lem-reach>

最後に、2つの補題を使って @thm-cutset を示します。

#v(10pt)
#proof-env(supplement: [@thm-cutset の証明])[
順方向は @lem-reach によります。逆方向は @lem-boundary と、カットセットに加えて他の辺を削除しても $s$ から $t$ へのパスが生じないことによります。
]
