"""Regenerate the graph illustrations with: python3 cuts-and-cutsets/figures/graphs.py"""
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
NODES = {'s': (65, 125), 'a': (180, 62), 'b': (180, 188),
         'c': (360, 62), 'd': (360, 188), 't': (475, 125)}
EDGES = [('s','a'), ('s','b'), ('a','c'), ('b','c'),
         ('b','d'), ('c','a'), ('c','t'), ('d','t')]
S = {'s','a','b'}
KEPT = {('s','b'), ('b','c'), ('c','a'), ('d','t')}
BLUE, ORANGE, INK, GRAY = '#175CD3', '#A34B00', '#30343B', '#7A8088'
RED = '#B42318'

def deletion_mark(x, y, color=ORANGE):
    """Clear the underlying line and leave visible whitespace around every cross."""
    path = f'M{x-4},{y-4} l8,8 M{x-4},{y+4} l8,-8'
    return (
        f'<circle cx="{x}" cy="{y}" r="8" fill="white"/>'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.8"/>'
    )

def removed_edge(path, x, y, color=ORANGE, *, cross_color=None):
    """Share thin dashed edges and deletion marks across diagrams and legends."""
    return (
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="5 5"/>'
        + deletion_mark(x, y, color if cross_color is None else cross_color)
    )

def reachable(edges):
    seen = {'s'}
    while True:
        new = seen | {v for u,v in edges if u in seen}
        if new == seen:
            return seen
        seen = new

REACH = reachable(KEPT)
assert REACH == {'s','a','b','c'}
BOUNDARY = {(u,v) for u,v in EDGES if u in S and v not in S}
assert BOUNDARY == {('a','c'), ('b','c'), ('b','d')}
assert 't' not in reachable(set(EDGES) - BOUNDARY)

LABELS = {
    'S': 'S', 'T': 'T', 'T = V \\ S': 'T = V backslash S',
    'S → T': 'S arrow.r T', 'δ⁺(S)': 'delta^+(S)', "E′": "E'", "E \\ E′": "E backslash E'",
    **{name: name for name in NODES},
    "Reach-cut": '"Reach"_(s)(E backslash delta^+(S))',
    "F": "F", "R": "R", "outside-R": "V backslash R",
    "boundary-R": "delta^+(R)",
    "e1": "e_1", "e2": "e_2",
    "both": "F = {e_1, e_2}",
    "first": "delta^+({s}) = {e_1}",
    "second": "delta^+({s,a}) = {e_2}",
    "Reach": '"Reach"_(s)(E\')',
}

def math_labels():
    labels = {}
    with tempfile.TemporaryDirectory(prefix='typst-graph-labels-') as directory:
        directory = Path(directory)
        for i, (label, expression) in enumerate(LABELS.items()):
            source = directory / f'label-{i}.typ'
            target = directory / f'label-{i}.svg'
            source.write_text(
                '#set page(width: auto, height: auto, margin: 4pt, fill: none)\n'
                '#set text(font: ("Hiragino Sans", "Libertinus Serif"), size: 17pt)\n'
                + ('$ ' + expression + ' $' if label in {'a', 'b', 'c', 'd'} else '$ bold(' + expression + ') $')
            )
            subprocess.run(['typst', 'compile', '--format', 'svg', str(source), str(target)], check=True)
            root = ET.fromstring(target.read_text())
            width = float(root.attrib['width'].removesuffix('pt'))
            height = float(root.attrib['height'].removesuffix('pt'))
            # Each SVG has its own glyph definitions. Give every label unique IDs.
            contents = ''.join(ET.tostring(child, encoding='unicode') for child in root)
            for old in re.findall(r'\bid="([^"]+)"', contents):
                contents = contents.replace(f'"{old}"', f'"label{i}-{old}"')
                contents = contents.replace(f'"#{old}"', f'"#label{i}-{old}"')
                contents = contents.replace(f'url(#{old})', f'url(#label{i}-{old})')
            labels[label] = (width, height, contents)
    return labels

MATH_LABELS = math_labels()

def svg(mode):
    example = mode in {'satisfies', 'fails'}
    nodes = NODES
    edges = EDGES
    removed = BOUNDARY | {('s','a')} if mode == 'satisfies' else {('a','c'), ('b','c')}
    height = 227 if mode == 'cut' else 261
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="540" height="{height}" viewBox="0 0 540 {height}">',
             f'<rect width="540" height="{height}" fill="white"/>', '<defs>']
    for name,color in [('ink',INK),('accent',ORANGE),('gray',GRAY),('blue',BLUE)]:
        parts.append(f'<marker id="{name}" viewBox="0 0 8 8" refX="4" refY="4" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 Z" fill="{color}"/></marker>')
    parts.append('</defs>')
    def text(x,y,value,size=17,color=INK):
        width,height,contents = MATH_LABELS[value]
        # Typst supplies the same math glyphs as in the manuscript.
        contents = contents.replace('#000000', color).replace('fill="black"', f'fill="{color}"')
        if value in {'s', 't'}:
            contents = f'<g stroke="{color}" stroke-width="0.22" stroke-linejoin="round">{contents}</g>'
        parts.append(f'<svg x="{x-width/2}" y="{y-5-height/2}" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{contents}</svg>')
    if mode in {'cut', 'boundary', 'satisfies', 'lemma1', 'lemma2'}:
        parts.append('<rect x="20" y="10" width="240" height="211" rx="16" fill="#DCE6F3"/>')
        parts.append('<rect x="280" y="10" width="240" height="211" rx="16" fill="#FBF2E8"/>')
        text(45,36,'R' if mode == 'lemma2' else 'S')
        label_width = MATH_LABELS['T = V \\ S'][0]
        s_width = MATH_LABELS['S'][0]
        # Mirror the outer label edges around the graph's vertical center.
        right_label = 'outside-R' if mode == 'lemma2' else 'T = V \\ S'
        label_width = MATH_LABELS[right_label][0]
        text(540 - (45 - s_width / 2) - label_width / 2,36,right_label)
    # Draw edges to node centers; the circles painted afterward mask the ends.
    # This keeps every edge flush with single- and double-ring node outlines.
    for u,v in edges:
        x1,y1=nodes[u]; x2,y2=nodes[v]
        if mode == 'lemma1':
            deleted = (u,v) in BOUNDARY
            color, width, marker = (ORANGE, 1.5, 'accent') if deleted else (INK, 1.5, 'ink')
            dash = 'stroke-dasharray="5 5"' if deleted else ''
        elif mode == 'lemma2':
            deleted = (u,v) in BOUNDARY | {('c','t')}
            boundary = (u,v) in BOUNDARY
            color = ORANGE if boundary else GRAY if deleted else INK
            width = 3.2 if boundary else 1.5
            marker = 'accent' if boundary else 'gray' if deleted else 'ink'
            dash = 'stroke-dasharray="5 5"' if deleted and not boundary else ''
        elif example:
            deleted = (u,v) in removed
            path_to_t = mode == 'fails' and (u,v) in {('s','b'), ('b','d'), ('d','t')}
            color = ORANGE if deleted else BLUE if path_to_t else INK
            width = 2.2 if deleted else 3.2 if path_to_t else 1.5
            marker = 'accent' if deleted else 'blue' if path_to_t else 'ink'
            dash = 'stroke-dasharray="5 5"' if deleted else ''
        elif mode in {'cut', 'boundary'}:
            accent=mode == 'boundary' and (u,v) in BOUNDARY
            color=ORANGE if accent else INK
            width=3.2 if accent else 1.5
            marker='accent' if accent else 'ink'
            dash=''
        else:
            kept=(u,v) in KEPT
            color=INK if kept else GRAY
            width=2.2 if kept else 1.3
            marker='ink' if kept else 'gray'
            dash='' if kept else 'stroke-dasharray="5 5"'
        if (u,v) in {('a','c'), ('c','a')}:
            # Split the quadratic at t=1/2 so marker-mid follows its tangent.
            cx,cy = 270, (29 if (u,v) == ('a','c') else 95)
            q1x,q1y = (x1+cx)/2, (y1+cy)/2
            q2x,q2y = (cx+x2)/2, (cy+y2)/2
            mx,my = (q1x+q2x)/2, (q1y+q2y)/2
            path=f'M{x1},{y1} Q{q1x},{q1y} {mx},{my} Q{q2x},{q2y} {x2},{y2}'
        else:
            path=f'M{x1},{y1} L{(x1+x2)/2},{(y1+y2)/2} L{x2},{y2}'
        deleted = (
            (mode == 'lemma1' and (u,v) in BOUNDARY)
            or (mode == 'lemma2' and (u,v) in BOUNDARY | {('c','t')})
            or (example and (u,v) in removed)
        )
        if deleted:
            cross_x,cross_y = (mx,my) if (u,v) in {('a','c'), ('c','a')} else ((x1+x2)/2,(y1+y2)/2)
            if mode == 'lemma2':
                color = RED if (u,v) in BOUNDARY else GRAY
            parts.append(removed_edge(path, cross_x, cross_y, color,
                                      cross_color=GRAY if mode == 'lemma2' else None))
        else:
            parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" {dash} marker-mid="url(#{marker})"/>')
    for name,(x,y) in nodes.items():
        marked=(mode=='reach' and name in REACH) or (mode in {'lemma1', 'lemma2'} and name in S)
        if marked:
            parts.append(f'<circle cx="{x}" cy="{y}" r="20" fill="white" stroke="{BLUE}" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="14" fill="white" stroke="{BLUE if marked else INK}" stroke-width="1.6"/>')
        text(x,y+5,name,17,BLUE if marked else INK)
    # Keep every symbol-label pair together, with a shared visible gap.
    gap = 5
    if mode == 'lemma1':
        cut_width = MATH_LABELS['δ⁺(S)'][0]
        reach_width = MATH_LABELS['Reach-cut'][0]
        pair_gap = 30
        total = 65+gap+cut_width+pair_gap+20+gap+reach_width
        start = (540-total)/2
        mid = start+32.5
        parts.append(removed_edge(f'M{start} 244 H{start+65}', mid, 244))
        text(start+65+gap+cut_width/2,249,'δ⁺(S)')
        center = start+65+gap+cut_width+pair_gap+10
        parts.append(f'<circle cx="{center}" cy="244" r="10" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
        parts.append(f'<circle cx="{center}" cy="244" r="7" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
        text(center+10+gap+reach_width/2,249,'Reach-cut')
    elif mode == 'lemma2':
        entries = [('F',65), ('boundary-R',35), ('R',20)]
        pair_gap = 25
        total = sum(symbol_width+gap+MATH_LABELS[key][0] for key,symbol_width in entries)+pair_gap*2
        start = (540-total)/2
        for key,symbol_width in entries:
            label_width = MATH_LABELS[key][0]
            if key == 'R':
                center = start+10
                parts.append(f'<circle cx="{center}" cy="244" r="10" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
                parts.append(f'<circle cx="{center}" cy="244" r="7" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
            else:
                if key == 'F':
                    parts.append(removed_edge(f'M{start} 244 H{start+symbol_width}', start+symbol_width/2, 244, GRAY))
                else:
                    parts.append(f'<path d="M{start} 244 H{start+35}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="5 5"/>')
            text(start+symbol_width+gap+label_width/2,249,key)
            start += symbol_width+gap+label_width+pair_gap
    elif example:
        width = MATH_LABELS['F'][0]
        start = (540 - (65 + gap + width)) / 2
        parts.append(removed_edge(f'M{start} 244 H{start+65}', start+32.5, 244))
        text(start+65+gap+width/2,249,'F')
    elif mode=='boundary':
        width = MATH_LABELS['δ⁺(S)'][0]
        start = (540 - (35 + gap + width)) / 2
        parts.append(f'<path d="M{start} 244 H{start+17.5} H{start+35}" stroke="{ORANGE}" stroke-width="3.2" marker-mid="url(#accent)"/>')
        text(start+35+gap+width/2,249,'δ⁺(S)')
    elif mode=='reach':
        e_width = MATH_LABELS['E′'][0]
        reach_width = MATH_LABELS['Reach'][0]
        pair_gap = 42
        total = 35 + gap + e_width + pair_gap + 20 + gap + reach_width
        start = (540-total)/2
        parts.append(f'<path d="M{start} 244 H{start+17.5} H{start+35}" stroke="{INK}" stroke-width="2.2" marker-mid="url(#ink)"/>')
        text(start+35+gap+e_width/2,249,'E′')
        center = start+35+gap+e_width+pair_gap+10
        parts.append(f'<circle cx="{center}" cy="244" r="10" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
        parts.append(f'<circle cx="{center}" cy="244" r="7" fill="white" stroke="{BLUE}" stroke-width="1.2"/>')
        text(center+10+gap+reach_width/2,249,'Reach')
    parts.append('</svg>')
    return '\n'.join(parts)

for mode,name in [('cut','cut.svg'),('reach','reachable-vertices.svg'),('boundary','outgoing-boundary.svg'),('satisfies','theorem-satisfies.svg'),('fails','theorem-fails.svg'),('lemma1','lemma-cut-removal.svg'),('lemma2','lemma-reachable-cut.svg')]:
    (OUT/name).write_text(svg(mode))

# Check both conditions independently on the shared graph.
for removed, expected in [(BOUNDARY | {('s','a')}, True), ({('a','c'), ('b','c')}, False)]:
    blocked = 't' not in reachable(set(EDGES) - removed)
    contains_cutset = False
    middle_vertices = ['a','b','c','d']
    for mask in range(1 << len(middle_vertices)):
        side = {'s'} | {v for i,v in enumerate(middle_vertices) if mask & (1 << i)}
        boundary = {(u,v) for u,v in EDGES if u in side and v not in side}
        contains_cutset |= boundary <= removed
    assert blocked == contains_cutset == expected

def counterexample_svg():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="540" height="136" viewBox="0 0 540 136">', '<rect width="540" height="136" fill="white"/>']
    def label(x,y,key,scale=1):
        w,h,content = MATH_LABELS[key]
        content = content.replace('#000000', INK)
        if key in {'s','t'}:
            content = f'<g stroke="{INK}" stroke-width="0.22">{content}</g>'
        parts.append(f'<svg x="{x-w*scale/2}" y="{y-h*scale/2}" width="{w*scale}" height="{h*scale}" viewBox="0 0 {w} {h}">{content}</svg>')
    for panel,key in enumerate(['both','first','second']):
        x = 180*panel
        if panel:
            split = x + (57 if panel==1 else 123)
            parts.append(f'<rect x="{x+8}" y="20" width="{split-x-16}" height="72" rx="8" fill="#DCE6F3"/>')
            parts.append(f'<rect x="{split+8}" y="20" width="{x+172-split-8}" height="72" rx="8" fill="#FBF2E8"/>')
        for i in range(2):
            start,end = x+23+62*i, x+85+62*i
            mid=(start+end)/2
            accent=panel==0 or i==panel-1
            color=ORANGE if accent else INK
            if panel == 0:
                parts.append(removed_edge(f'M{start} 62 H{end}', mid, 62))
            else:
                parts.append(f'<path d="M{start} 62 H{end}" stroke="{color}" stroke-width="{2.5 if accent else 1.5}"/>')
                parts.append(f'<path d="M{mid-4} 58 L{mid+4} 62 L{mid-4} 66 Z" fill="{color}"/>')
            label(mid,41,'e1' if i==0 else 'e2',0.85)
        for i,name in enumerate(['s','a','t']):
            cx=x+23+62*i
            parts.append(f'<circle cx="{cx}" cy="62" r="11" fill="white" stroke="{INK}" stroke-width="1.4"/>')
            label(cx,62,name,0.9)
        label(x+90,115,key,0.83)
    parts.append('</svg>')
    return '\n'.join(parts)

(OUT/'extra-edges-counterexample.svg').write_text(counterexample_svg())

lemma2_removed = BOUNDARY | {('c','t')}
assert reachable(set(EDGES) - BOUNDARY) == S
assert reachable(set(EDGES) - lemma2_removed) == S
assert BOUNDARY < lemma2_removed
