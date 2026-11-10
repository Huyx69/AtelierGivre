#!/usr/bin/env python3
"""
Atelier Givre — fabrique l'édition Noël du site (site-noel.html) à partir du
site normal (site-normal.html).

  python3 outils/generer-noel.py

Ce que fait le script :
  1. couleurs : bleu nuit → vert sapin, gris bleutés → crèmes chauds,
     boutons principaux → rouge Noël (l'or reste l'accent) ;
  2. quelques textes de saison (accroche de l'accueil) et l'onglet « Noël »
     ouvert par défaut quand il contient des gâteaux ;
  3. décors : guirlande lumineuse, boules suspendues, neige au sol et sur les
     cartes, houx et étoiles, boule à neige, étoiles pendues, traîneau ;
  4. styles (outils/noel/noel.css) et animations (outils/noel/noel.js).

Si le site normal change (textes, logique, prix…), relancer le script suffit
pour mettre l'édition Noël à jour.
"""
import math
import random
import re
from pathlib import Path
from urllib.parse import quote

RACINE = Path(__file__).resolve().parent.parent
ICI = Path(__file__).resolve().parent / 'noel'
random.seed(25)

ROUGE = '#A8232D'
SAPIN = '#173A2E'
CREME = '#FBF6EE'

# ── 1. Couleurs ─────────────────────────────────────────────────────────────
PALETTE = {
    '#1A2C3D': SAPIN, '#101C27': '#0F2A20', '#566571': '#56625B', '#8A98A5': '#8D968E',
    '#F5F7FA': CREME, '#E8E8E8': '#ECE3D3', '#F2F2F2': '#F3ECE0', '#EEE': '#EFE7DA',
    '#DBE4EC': '#E6DCCB', '#E3EAF2': '#EFE6D6', '#EAF0F6': '#F4EDE1', '#E2EAF2': '#EEE4D3',
    '#F0F0F0': '#F1EADF', '#C8D8E8': '#DCCFBA', '#A7B6C5': '#B5AE9F', '#9FB0C0': '#ADA595',
    '#EEF3F8': '#F6F0E6', '#E8EFF6': '#F3ECE1', '#DFE8F1': '#ECE2D2', '#DCE3EA': '#E6DDCF',
    '#D5DFE9': '#E2D6C4', '#CFD8E1': '#DDD2C1', '#C4D0DC': '#D6C9B5', '#B3BFC9': '#C2BBAD',
    '#93A2B0': '#A39D90', '#8FA1B3': '#A0998B', '#7D8E9D': '#8B887E', '#728290': '#7E7D73',
    '#3C4A57': '#36443C', '#FBFCFD': '#FFFDF9',
}
RGBA = {
    'rgba(26,44,61,': 'rgba(23,58,46,', 'rgba(16,28,39,': 'rgba(13,34,26,', 'rgba(13,22,31,': 'rgba(10,26,20,',
}
# Boutons principaux et éléments actifs : rouge Noël.
CIBLES = [
    ('background:#C9A84C;color:#fff;border:1px solid #C9A84C', f'background:{ROUGE};color:#fff;border:1px solid {ROUGE}'),
    ('background:#C9A84C;color:#fff', f'background:{ROUGE};color:#fff'),
    ("active ? '1px solid #C9A84C'", f"active ? '1px solid {ROUGE}'"),
    ("active ? '#C9A84C'", f"active ? '{ROUGE}'"),
    ("canCheckout ? '#C9A84C'", f"canCheckout ? '{ROUGE}'"),
    ("s.cgvAccepted ? '#C9A84C'", f"s.cgvAccepted ? '{ROUGE}'"),
    ('rgba(201,168,76,.5)', 'rgba(168,35,45,.45)'),
]

# ── 3. Dessins SVG ──────────────────────────────────────────────────────────
def url(svg):
    # Dimensions explicites (celles du viewBox) : sans elles, certains navigateurs
    # ignorent background-size et dessinent l'image à sa taille d'origine.
    m = re.search(r"viewBox='0 0 ([\d.]+) ([\d.]+)'", svg)
    if m and ' width=' not in svg[:120]:
        svg = svg.replace('<svg ', f"<svg width='{m.group(1)}' height='{m.group(2)}' ", 1)
    return 'url("data:image/svg+xml,' + quote(svg, safe=" =:/'") + '")'

def collines(base, amplitude, pas, graine):
    rnd = random.Random(graine)
    pts = [(x, base - rnd.uniform(0, amplitude)) for x in range(0, 1441, pas)]
    d = f'M0 {pts[0][1]:.0f}'
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cx = (x0 + x1) / 2
        d += f' C{cx:.0f} {y0:.0f} {cx:.0f} {y1:.0f} {x1} {y1:.0f}'
    return d + ' L1440 100 L0 100Z'

def neige_sol(couleur, opacite, graine, base):
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 100' preserveAspectRatio='none'>"
               f"<path d='{collines(base, 34, 180, graine)}' fill='{couleur}' fill-opacity='{opacite}'/></svg>")

def neige_bord(haut=True, couleur='#FFFFFF'):
    # Bande de neige ondulée avec quelques gouttes, de largeur 400, épaisseur ~20.
    rnd = random.Random(7 if haut else 11)
    d = 'M0 0 H400 V9'
    x = 400
    while x > 0:
        w = rnd.uniform(14, 30); x2 = max(0, x - w); creux = rnd.uniform(9, 15)
        if rnd.random() < 0.18:
            m = (x + x2) / 2
            d += f' C{x - w * .2:.1f} {creux:.1f} {m + 3:.1f} {creux + 2:.1f} {m + 2:.1f} {creux + 6:.1f} A2.6 2.6 0 0 1 {m - 3:.1f} {creux + 6:.1f} C{m - 3:.1f} {creux + 2:.1f} {x2 + w * .2:.1f} {creux:.1f} {x2:.1f} 9'
        else:
            d += f' Q{(x + x2) / 2:.1f} {creux:.1f} {x2:.1f} 9'
        x = x2
    d += ' Z'
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 20' preserveAspectRatio='none'><path d='{d}' fill='{couleur}'/></svg>")

def etoiles(n, graine):
    rnd = random.Random(graine)
    couches = []
    for _ in range(n):
        x, y, r = rnd.uniform(2, 98), rnd.uniform(3, 97), rnd.choice([1, 1, 1.5, 2])
        couches.append(f'radial-gradient({r}px {r}px at {x:.1f}% {y:.1f}%,#fff 50%,transparent 51%)')
    return ','.join(couches)

def etoile_svg(couleur='#D9B65A', clair='#F6E3A4'):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; r = 48 if i % 2 == 0 else 20
        pts.append(f'{50 + r * math.cos(a):.1f},{50 + r * math.sin(a):.1f}')
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
               f"<stop offset='0' stop-color='{clair}'/><stop offset='1' stop-color='{couleur}'/></linearGradient></defs>"
               f"<polygon points='{' '.join(pts)}' fill='url(#g)' stroke='#A9863A' stroke-width='1.5' stroke-linejoin='round'/></svg>")

def houx():
    # Branche de sapin, trois feuilles de houx et des baies rouges.
    rnd = random.Random(3)
    aiguilles = []
    for i in range(46):
        t = i / 45; x = 12 + t * 150; y = 170 - t * 120 + math.sin(t * 3) * 6
        for s in (-1, 1):
            a = (-1.0 + s * 0.9) + rnd.uniform(-.15, .15); L = 18 + rnd.uniform(-3, 5) - t * 4
            aiguilles.append(f'M{x:.1f} {y:.1f} l{L * math.cos(a):.1f} {L * math.sin(a) * s:.1f}')
    feuille = 'M0 0 C8 -6 14 -2 20 -8 C22 -3 28 -2 32 -6 C33 0 38 3 44 2 C40 8 41 13 44 18 C37 17 33 20 30 24 C26 19 20 20 14 22 C14 16 8 12 0 0Z'
    feuilles = ''.join(f"<path d='{feuille}' transform='translate({x} {y}) rotate({r}) scale(1.35)' fill='{c}' stroke='#0B2A1C' stroke-width='1.2'/>"
                       for x, y, r, c in [(96, 104, -20, '#1F6B44'), (100, 108, 60, '#2A7F52'), (92, 112, 150, '#1B5E3C')])
    baies = ''.join(f"<circle cx='{x}' cy='{y}' r='8' fill='#C62B32' stroke='#7C1119' stroke-width='1.2'/><circle cx='{x - 2.5}' cy='{y - 2.5}' r='2.2' fill='#fff' fill-opacity='.7'/>"
                    for x, y in [(98, 102), (110, 100), (104, 112)])
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'>"
               f"<path d='M10 172 Q90 120 168 48' fill='none' stroke='#5A3B22' stroke-width='4' stroke-linecap='round'/>"
               f"<path d='{' '.join(aiguilles)}' fill='none' stroke='#2E6B4A' stroke-width='2.4' stroke-linecap='round'/>"
               f"<path d='{' '.join(aiguilles[::3])}' fill='none' stroke='#4C8F66' stroke-width='1.4' stroke-linecap='round'/>"
               f"{feuilles}{baies}</svg>")

def noeud(couleur, bord):
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 40'>"
               f"<path d='M30 18 C20 2 4 2 6 14 C7 24 22 22 30 18Z M30 18 C40 2 56 2 54 14 C53 24 38 22 30 18Z' fill='{couleur}' stroke='{bord}' stroke-width='2'/>"
               f"<path d='M28 20 L18 38 L24 36 L27 40 L30 22Z M32 20 L42 38 L36 36 L33 40 L30 22Z' fill='{couleur}' stroke='{bord}' stroke-width='2'/>"
               f"<circle cx='30' cy='19' r='5' fill='{couleur}' stroke='{bord}' stroke-width='2'/></svg>")

def sapin():
    etages = ''.join(f"<path d='M50 {y} L{50 - w} {y + 26} L{50 + w} {y + 26}Z' fill='{c}'/>" for y, w, c in [(8, 16, '#2E7A52'), (24, 24, '#256B47'), (42, 32, '#1D5A3B')])
    boules = ''.join(f"<circle cx='{x}' cy='{y}' r='3' fill='{c}'/>" for x, y, c in [(44, 30, '#E5483F'), (58, 46, '#F6C65B'), (38, 58, '#F6C65B'), (62, 62, '#E5483F'), (50, 40, '#D6ECFF')])
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>{etages}<rect x='46' y='68' width='8' height='12' fill='#6B4428'/>"
               f"<polygon points='50,0 52.5,6 59,6 54,10 56,16 50,12.5 44,16 46,10 41,6 47.5,6' fill='#F6D27A'/>{boules}</svg>")

def traineau():
    renne = ("<path d='M0 22 C4 14 14 12 22 14 L30 6 L32 0 M30 6 L36 2 M30 6 L26 0 M22 14 C26 16 28 20 26 24 "
             "L30 34 M18 24 L20 34 M8 22 L4 34 M12 22 L12 34 M0 22 L-6 20' fill='none' stroke='#E6C878' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/>"
             "<ellipse cx='12' cy='19' rx='13' ry='6' fill='#E6C878'/>")
    rennes = ''.join(f"<g transform='translate({x} {y})'>{renne}</g>" for x, y in [(10, 14), (52, 10), (94, 6)])
    return url(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 64'>{rennes}"
               f"<path d='M118 22 L150 30 M64 20 L118 22' stroke='#E6C878' stroke-width='1.4'/>"
               f"<path d='M150 24 C152 40 166 46 196 44 C214 43 220 36 222 26 L206 28 C200 34 188 34 178 30 L176 18 Z' fill='#E6C878'/>"
               f"<path d='M146 50 C170 54 210 54 232 46' fill='none' stroke='#E6C878' stroke-width='3' stroke-linecap='round'/>"
               f"<rect x='182' y='8' width='18' height='14' rx='2' fill='#E6C878'/><path d='M182 15 H200 M191 8 V22' stroke='#173A2E' stroke-width='2'/></svg>")

FIL = url("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 24' preserveAspectRatio='none'>"
          "<path d='M0 3 Q50 17 100 3' fill='none' stroke='#2D4A3C' stroke-width='1.5' vector-effect='non-scaling-stroke'/></svg>")

DESSINS = {
    'FIL': FIL,
    'NEIGE_SOL': neige_sol(CREME, 1, 1, 96),
    'NEIGE_SOL_FOND': neige_sol('#FFFFFF', .55, 2, 70),
    'NEIGE_CARTE': neige_bord(True),
    'NEIGE_HAUT': neige_bord(False, CREME),  # prolonge la section crème du dessus
    'ETOILES_A': etoiles(38, 4), 'ETOILES_B': etoiles(34, 9),
    'HOUX': houx(), 'NOEUD': noeud('#F3E2B0', '#C9A84C'), 'NOEUD_GRAND': noeud(ROUGE, '#7C1119'),
    'SAPIN': sapin(), 'ETOILE': etoile_svg(), 'TRAINEAU': traineau(),
}

def decor_globe():
    flocons = ''.join(f'<i style="--x:{random.uniform(6, 94):.0f}%;--s:{random.choice([3, 3, 4, 5])}px;--d:{random.uniform(5, 9):.1f}s;--t:-{random.uniform(0, 9):.1f}s;"></i>' for _ in range(16))
    return ('\n        <div class="xm-globe" aria-hidden="true">'
            '<div class="xm-globe-boule" title="Secouez-moi !"><div class="xm-globe-verre"><span class="xm-globe-sapin"></span>' + flocons + '</div><div class="xm-globe-socle"></div></div>'
            '<p class="xm-globe-texte">Un projet pour les fêtes&nbsp;?<small>Cliquez sur la boule pour la secouer</small></p></div>')

DECORS = [
    # (texte repère dans le site normal, ce qu'on insère, 'avant' ou 'apres')
    ('  </header>', '    <div class="xm-guirlande" aria-hidden="true">' + '<i></i>' * 24 + '</div>\n', 'avant'),
    ('<div style="position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(16,28,39,.5) 0%',
     '<div class="xm-boules" aria-hidden="true">'
     '<span class="xm-boule rouge" style="--x:18%;--l:96px;--s:50px;--b:4.6s;"></span>'
     '<span class="xm-boule or" style="--x:52%;--l:150px;--s:40px;--b:5.4s;--bt:-1.2s;"></span>'
     '<span class="xm-boule vert" style="--x:84%;--l:70px;--s:44px;--b:4.2s;--bt:-2.4s;"></span></div>\n    ', 'avant'),
    ('  <!-- ════════════════ NOS CRÉATIONS', '', 'neige-accueil'),
    ('<section id="number-cake" class="ag-sec" style="scroll-margin-top:80px;padding:104px 28px;background:#1A2C3D;color:#fff;overflow:hidden;">',
     '\n    <span class="xm-etoiles" aria-hidden="true"></span><span class="xm-etoiles b" aria-hidden="true"></span>'
     '<span class="xm-houx g" aria-hidden="true"></span><span class="xm-houx d" aria-hidden="true"></span>', 'apres'),
    ('Buffets sucrés &amp; commandes événementielles</div>\n        </div>', decor_globe(), 'apres'),
    ('<section id="galerie" class="ag-sec" style="scroll-margin-top:90px;padding:104px 28px;background:#FFFFFF;">',
     '\n    <div class="xm-pendus" aria-hidden="true">'
     '<span class="xm-pendu" style="--x:4%;--l:70px;--s:30px;"></span><span class="xm-pendu" style="--x:9%;--l:120px;--s:24px;--b:7s;--bt:-2s;"></span>'
     '<span class="xm-pendu" style="--x:91%;--l:96px;--s:28px;--b:6.4s;--bt:-1s;"></span><span class="xm-pendu" style="--x:96%;--l:56px;--s:22px;--b:5.6s;--bt:-3s;"></span></div>', 'apres'),
    ('<footer class="ag-sec" style="background:#1A2C3D;color:#dbe4ec;padding:70px 28px 36px;">',
     '\n    <span class="xm-etoiles" aria-hidden="true"></span><span class="xm-neige-haut" aria-hidden="true"></span><span class="xm-traineau" aria-hidden="true"></span>', 'apres'),
]
NOEUDS = ["Lire l'histoire", 'Composer mon Number Cake']

TEXTES = [
    ('Belley, Ain — fait main', 'Belley, Ain — Noël fait main'),
    ('La passion du fait maison, au cœur de chaque bouchée.', 'Des douceurs de fêtes, faites main pour vos tables de Noël.'),
    ("    activeCat: 'Tartes & entremets',", "    activeCat: 'Noël', // onglet ouvert par défaut (s'il est vide, la première catégorie remplie)"),
]


def generer():
    s = (RACINE / 'site-normal.html').read_text(encoding='utf-8')

    def une(repere):
        if s.count(repere) != 1:
            raise SystemExit(f'Repère introuvable ou ambigu dans site-normal.html : {repere[:70]!r}')

    # Décors (sur le texte d'origine, avant les changements de couleurs).
    for repere, ajout, ou in DECORS:
        une(repere)
        if ou == 'avant':
            s = s.replace(repere, ajout + repere)
        elif ou == 'apres':
            s = s.replace(repere, repere + ajout)
        elif ou == 'neige-accueil':
            # Neige au sol : dernier élément de la section d'accueil.
            i = s.index(repere); j = s.rindex('  </section>', 0, i)
            s = s[:j] + '    <span class="xm-neige-sol" aria-hidden="true"></span>\n' + s[j:]
    for texte in NOEUDS:
        une('>' + texte)
        s = s.replace('>' + texte, '><span class="xm-noeud" aria-hidden="true"></span>' + texte)
    for a, b in TEXTES:
        une(a); s = s.replace(a, b)

    # Couleurs.
    for a, b in CIBLES:
        s = s.replace(a, b)
    for a, b in PALETTE.items():
        s = re.sub(re.escape(a) + r'(?![0-9A-Fa-f])', b, s, flags=re.I)
    for a, b in RGBA.items():
        s = s.replace(a, b)

    # Styles et animations.
    css = (ICI / 'noel.css').read_text(encoding='utf-8')
    for nom, valeur in DESSINS.items():
        css = css.replace(f'@@{nom}@@', valeur)
    reste = re.findall(r'@@\w+@@', css)
    if reste:
        raise SystemExit(f'Dessins manquants : {reste}')
    une('</style>\n')
    s = s.replace('</style>\n', css + '</style>\n')
    js = (ICI / 'noel.js').read_text(encoding='utf-8')
    une('</body>')
    s = s.replace('</body>', '<script>' + js + '</script>\n</body>')

    (RACINE / 'site-noel.html').write_text(s, encoding='utf-8')
    print('site-noel.html :', len(s) // 1024, 'ko')


if __name__ == '__main__':
    generer()
