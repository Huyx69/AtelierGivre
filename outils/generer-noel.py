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
     cartes, houx et étoiles, boule à neige, étoiles pendues ;
  4. « La carte de Noël » : une grande section juste après l'accueil, avec les
     gâteaux de la catégorie Noël (lien « Noël » dans le menu) ;
  5. styles (outils/noel/noel.css) et animations (outils/noel/noel.js).

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
    '#3C4A57': '#36443C', '#FBFCFD': '#FFFDF9', '#6B7B89': '#6B7369',
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
    'SAPIN': sapin(), 'ETOILE': etoile_svg(),
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
     '\n    <span class="xm-etoiles" aria-hidden="true"></span><span class="xm-neige-haut" aria-hidden="true"></span>', 'apres'),
]
NOEUDS = ["Lire l'histoire", 'Composer mon Number Cake']

TEXTES = [
    ('Pâtisserie artisanale à Belley · fait main', 'Pâtisserie artisanale à Belley · Noël fait main'),
    ('<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n', '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<meta name="theme-color" content="#173A2E">\n'),
    ('La passion du fait maison, au cœur de chaque bouchée.', 'Des douceurs de fêtes, faites main pour vos tables de Noël.'),
    ("    const cats = this.CATEGORIES.filter((c) => this.PRODUCTS.some((p) => p.cat === c));",
     "    // Édition Noël : les gâteaux de Noël ont leur propre section (« La carte de Noël »), pas d'onglet ici.\n"
     "    const cats = this.CATEGORIES.filter((c) => c !== 'Noël' && this.PRODUCTS.some((p) => p.cat === c));"),
    ("    const catEmpty = visibleProducts.length === 0;\n",
     "    const catEmpty = visibleProducts.length === 0;\n"
     "    // Édition Noël : la carte de Noël (catégorie « Noël » de l'admin).\n"
     "    const noelProducts = this.PRODUCTS.filter((p) => p.cat === 'Noël').map((p) => ({\n"
     "      id: p.id, name: p.name, desc: p.desc, img: p.img,\n"
     "      priceLabel: this.priceFromLabel(p),\n"
     "      delayShort: p.delayShort || '72 h à l’avance',\n"
     "      onOpen: () => this.openProduct(p),\n"
     "    }));\n"),
    ("      catEmpty,\n", "      catEmpty,\n      noelProducts,\n      noelHas: noelProducts.length > 0,\n      noelEmpty: noelProducts.length === 0,\n"),
    ('backdrop-filter:blur(6px);transition:background .3s ease,border-color .3s ease;" style-hover="background:rgba(255,255,255,.16);border-color:#fff;">Découvrir mes créations</a>',
     'backdrop-filter:blur(6px);transition:background .3s ease,border-color .3s ease;" style-hover="background:rgba(255,255,255,.16);border-color:#fff;">Découvrir la carte de Noël</a>'),
]
# Le bouton « Découvrir… » de l'accueil mène à la carte de Noël.
LIEN_ACCUEIL = ('<a href="#creations" style="display:inline-flex;align-items:center;gap:10px;color:#fff;', '<a href="#noel" style="display:inline-flex;align-items:center;gap:10px;color:#fff;')
# Lien « Noël » dans le menu (ordinateur et téléphone), avant « Mes créations ».
MENU = [
    ('        <a href="#creations" style="font-size:13.5px;',
     '        <a href="#noel" style="font-size:13.5px;letter-spacing:.4px;color:#A8232D;font-weight:500;text-decoration:none;padding-bottom:2px;border-bottom:1px solid transparent;transition:border-color .25s ease;" style-hover="border-bottom:1px solid #A8232D;">Noël</a>\n'),
    ('      <a onClick="{{ closeMenu }}" href="#creations"',
     '      <a onClick="{{ closeMenu }}" href="#noel" style="padding:15px 24px;font-size:15px;letter-spacing:.3px;color:#A8232D;font-weight:500;text-decoration:none;border-bottom:1px solid #F2F2F2;">Noël</a>\n'),
]

def section_noel():
    carte = (
        '          <article onClick="{{ p.onOpen }}" class="xm-carte-noel" style="background:#fff;border:1px solid #ECE3D3;border-radius:14px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;animation:ag-cardIn .5s ease both;transition:transform .35s ease,box-shadow .35s ease;" style-hover="transform:translateY(-6px);box-shadow:0 26px 48px -26px rgba(23,58,46,.45);">\n'
        '            <div class="ag-card-img" style="position:relative;height:270px;overflow:hidden;background:linear-gradient(150deg,#FBF6EE 0%,#F4EDE1 55%,#EEE4D3 100%);">\n'
        '              <img src="{{ p.img }}" alt="{{ p.name }}" loading="lazy" decoding="async" style="width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease;" style-hover="transform:scale(1.04);">\n'
        '              <span class="xm-ruban" aria-hidden="true">Noël</span>\n'
        '            </div>\n'
        '            <div style="padding:24px 24px 26px;display:flex;flex-direction:column;flex:1;">\n'
        '              <h3 style="font-family:\'Cormorant Garamond\',serif;font-weight:600;font-size:25px;margin:0 0 8px;color:#173A2E;">{{ p.name }}</h3>\n'
        '              <p style="font-size:14px;line-height:1.65;color:#7E7D73;margin:0 0 16px;flex:1;">{{ p.desc }}</p>\n'
        '              <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">\n'
        '                <span style="font-family:\'Cormorant Garamond\',serif;font-size:26px;font-weight:600;color:#A8232D;">{{ p.priceLabel }}</span>\n'
        '                <span style="background:#A8232D;color:#fff;font-size:12px;letter-spacing:.8px;text-transform:uppercase;padding:11px 20px;border-radius:2px;">Commander</span>\n'
        '              </div>\n'
        '              <p style="font-size:11.5px;letter-spacing:.4px;color:#8D968E;margin:12px 0 0;">{{ p.delayShort }}</p>\n'
        '            </div>\n'
        '          </article>\n')
    return (
        '  <!-- ════════════════ LA CARTE DE NOËL (édition Noël) ════════════════ -->\n'
        '  <section id="noel" class="ag-sec xm-carte" style="scroll-margin-top:80px;padding:92px 28px 110px;">\n'
        '    <span class="xm-houx g" aria-hidden="true"></span><span class="xm-houx d" aria-hidden="true"></span>\n'
        '    <div style="max-width:1180px;margin:0 auto;position:relative;z-index:1;">\n'
        '      <div data-reveal style="opacity:0;transform:translateY(26px);transition:opacity .9s cubic-bezier(.22,.61,.36,1),transform .9s cubic-bezier(.22,.61,.36,1);text-align:center;margin-bottom:46px;">\n'
        '        <div style="display:flex;align-items:center;justify-content:center;gap:12px;color:#C9A84C;margin-bottom:16px;"><span style="height:1px;width:30px;background:#C9A84C;"></span><span style="font-size:12px;letter-spacing:3px;text-transform:uppercase;">Édition de fêtes</span><span style="height:1px;width:30px;background:#C9A84C;"></span></div>\n'
        '        <h2 style="font-family:\'Cormorant Garamond\',serif;font-weight:500;font-size:clamp(44px,6.4vw,82px);line-height:1;margin:0;color:#173A2E;">La carte de <em style="font-style:italic;color:#A8232D;">Noël</em></h2>\n'
        '        <p style="font-size:16px;line-height:1.75;color:#56625B;margin:20px auto 0;max-width:54ch;">Bûches, entremets de fêtes et douceurs à offrir&nbsp;: des créations imaginées pour vos tables de Noël, faites main à l\'atelier. Pensez à commander à l\'avance.</p>\n'
        '      </div>\n'
        '      <sc-if value="{{ noelHas }}" hint-placeholder-val="{{ true }}">\n'
        '        <div class="ag-creations-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:32px;">\n'
        '          <sc-for list="{{ noelProducts }}" as="p" hint-placeholder-count="3">\n' + carte +
        '          </sc-for>\n'
        '        </div>\n'
        '      </sc-if>\n'
        '      <sc-if value="{{ noelEmpty }}" hint-placeholder-val="{{ false }}">\n'
        '        <div class="xm-bientot">\n'
        '          <p style="font-family:\'Cormorant Garamond\',serif;font-size:clamp(28px,3.4vw,38px);color:#173A2E;margin:0 0 10px;">La carte se dévoile très bientôt</p>\n'
        '          <p style="font-size:15px;line-height:1.75;color:#56625B;margin:0 auto 26px;max-width:50ch;">Les gâteaux de Noël arrivent sur le site dans les prochains jours. Une envie particulière pour vos fêtes, un repas de famille, un cadeau&nbsp;? Écrivez-moi, je vous prépare une proposition.</p>\n'
        '          <a href="#devis" style="display:inline-flex;align-items:center;gap:10px;background:#A8232D;color:#fff;text-decoration:none;font-size:13px;letter-spacing:1.3px;text-transform:uppercase;padding:15px 30px;border-radius:2px;"><span class="xm-noeud" aria-hidden="true"></span>Me demander un devis</a>\n'
        '        </div>\n'
        '      </sc-if>\n'
        '    </div>\n'
        '  </section>\n\n')



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
    une(LIEN_ACCUEIL[0]); s = s.replace(*LIEN_ACCUEIL)
    for repere, ajout in MENU:
        une(repere); s = s.replace(repere, ajout + repere)

    # Couleurs.
    for a, b in CIBLES:
        s = s.replace(a, b)
    for a, b in PALETTE.items():
        s = re.sub(re.escape(a) + r'(?![0-9A-Fa-f])', b, s, flags=re.I)
    for a, b in RGBA.items():
        s = s.replace(a, b)

    # La carte de Noël, juste après l'accueil.
    repere = '  <!-- ════════════════ NOS CRÉATIONS'
    une(repere); s = s.replace(repere, section_noel() + repere)

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
