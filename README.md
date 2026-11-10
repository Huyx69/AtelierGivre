"# AtelierGivre" 

## Thèmes du site

Le site existe en plusieurs habillages, choisis dans l'admin (`admin.html` → « Thème du site ») :

| Thème | Site | Page « introuvable » |
|---|---|---|
| Normal | `site-normal.html` | `404-normal.html` |
| Halloween | `site-halloween.html` | `404-halloween.html` |
| Noël | `site-noel.html` | `404-noel.html` |

- `index.html` et `404.html` lisent le thème actif dans Supabase (table `site_settings`, clé `theme`) et affichent la bonne version.
- Aperçu d'un thème sans l'activer : `/?theme=noel` (ou `normal`, `halloween`).
- **À faire une fois** : coller `supabase/reglages.sql` dans Supabase → SQL Editor (crée la table des réglages). Sans elle, le site reste en thème normal.
- L'édition Noël est fabriquée à partir du site normal : après une modification de `site-normal.html`, relancer `python3 outils/generer-noel.py`. Les modifications de logique (panier, paiement…) faites dans `site-normal.html` doivent aussi être reportées dans `site-halloween.html`.
- La catégorie « Noël » existe dans l'admin. En thème Noël, ses gâteaux sont présentés dans « La carte de Noël », grande section juste après l'accueil (avec un message « bientôt » tant qu'elle est vide). Dans les autres thèmes, un onglet « Noël » apparaît dans « Mes créations » dès qu'elle contient des gâteaux.
