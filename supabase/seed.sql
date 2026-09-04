-- ════════════════════════════════════════════════════════════════════════
--  Atelier Givre — remplissage du catalogue (à coller dans Supabase → SQL Editor)
--  Insère les produits actuels. Réexécutable sans risque (on conflict do nothing).
-- ════════════════════════════════════════════════════════════════════════

-- Colonne pour le libellé de variante (ex. « Préparation » pour les cannelés)
alter table public.products add column if not exists variant_label text default '';

insert into public.products
  (id, category, name, description, composition, allergenes, options, variants, variant_label, images, active, promo_percent, sort_order)
values

('trois-citrons', $$Tartes & entremets$$, $$Tarte aux Trois Citrons$$,
 $$Trois citrons, trois nuances : la fraîcheur du citron jaune, le parfum du citron vert et l'intensité du yuzu.$$,
 ARRAY[$$Pâte sucrée$$,$$Crème d'amande au citron vert$$,$$Crémeux citron jaune$$,$$Gel citron yuzu$$,$$Ganache montée citron jaune et vert$$,$$Zestes de citron vert et jaune$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (amande)$$],
 $j$[{"label":"4/6 personnes","price":26},{"label":"8/10 personnes","price":44}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/trois-citrons-1.jpg$$,$$images/trois-citrons-2.jpg$$,$$images/trois-citrons-3.jpg$$],
 true, 0, 10),

('choco-cacahuete', $$Tartes & entremets$$, $$Tarte Chocolat, Caramel & Cacahuète$$,
 $$L'intensité du chocolat, la douceur du caramel et le caractère de la cacahuète dans une tarte résolument gourmande.$$,
 ARRAY[$$Pâte sucrée amande$$,$$Croustillant cacahuète$$,$$Caramel vanille$$,$$Crémeux chocolat au lait$$,$$Ganache montée chocolat noir$$,$$Cacahuètes$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (amande)$$,$$Arachides$$,$$Soja$$],
 $j$[{"label":"4/6 personnes","price":24},{"label":"8/10 personnes","price":42}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/choco-cacahuete-1.jpg$$,$$images/choco-cacahuete-2.jpg$$,$$images/choco-cacahuete-3.jpg$$],
 true, 0, 20),

('vanille-pistache', $$Tartes & entremets$$, $$Tarte Vanille & Pistache$$,
 $$La douceur de la vanille rencontre l'intensité de la pistache, entre crémeux, croustillant et praliné.$$,
 ARRAY[$$Pâte sucrée amande$$,$$Croustillant pistache$$,$$Crémeux vanille & chocolat blanc$$,$$Praliné pistache maison$$,$$Ganache montée vanille$$,$$Pistaches caramélisées$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (pistache, amande)$$,$$Soja$$],
 $j$[{"label":"4/6 personnes","price":26},{"label":"8/10 personnes","price":44}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/vanille-pistache-1.jpg$$,$$images/vanille-pistache-2.jpg$$,$$images/vanille-pistache-3.jpg$$],
 true, 0, 30),

('manguier', $$Tartes & entremets$$, $$Le Manguier$$,
 $$La fraîcheur de la mangue associée à la douceur de la vanille, pour un entremets frais, léger et fruité.$$,
 ARRAY[$$Biscuit madeleine vanille$$,$$Compotée de mangue$$,$$Brunoise de mangue$$,$$Ganache montée vanille$$,$$Mangue fraîche$$,$$Glaçage neutre$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$],
 $j$[{"label":"4 personnes","price":24},{"label":"8 personnes","price":42}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/manguier-1.jpg$$,$$images/manguier-2.jpg$$,$$images/manguier-3.jpg$$],
 true, 0, 40),

('flan-pecan', $$Tartes & entremets$$, $$Flan Vanille & Pécan$$,
 $$La douceur de la vanille et la gourmandise de la noix de pécan réunies dans un flan fondant et généreux.$$,
 ARRAY[$$Pâte sucrée$$,$$Praliné pécan maison$$,$$Appareil à flan vanille$$,$$Ganache montée vanille$$,$$Noix de pécan$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (pécan)$$],
 $j$[{"label":"4 personnes","price":22},{"label":"8 personnes","price":40}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/flan-pecan-1.jpg$$,$$images/flan-pecan-2.jpg$$,$$images/flan-pecan-3.jpg$$],
 true, 0, 50),

('cake-citron-framboise', $$Cakes$$, $$Cake Citron & Framboise$$,
 $$La fraîcheur du citron associée à l'acidité de la framboise dans un cake moelleux, fruité et gourmand.$$,
 ARRAY[$$Cake moelleux citron$$,$$Crémeux framboise$$,$$Glaçage rocher$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (amande)$$,$$Soja$$],
 $j$[{"label":"Cake 25 cm","price":22}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cake-citron-framboise-1.jpg$$,$$images/cake-citron-framboise-2.jpg$$,$$images/cake-citron-framboise-3.jpg$$],
 true, 0, 60),

('cake-vanille-pavot', $$Cakes$$, $$Cake Vanille & Pavot$$,
 $$La douceur de la vanille associée au caractère délicat du pavot dans un cake tendre et parfumé.$$,
 ARRAY[$$Cake moelleux vanille pavot$$,$$Crémeux vanille$$,$$Glaçage rocher vanille pavot$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (amande)$$,$$Soja$$],
 $j$[{"label":"Cake 25 cm","price":22}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cake-vanille-pavot-1.jpg$$,$$images/cake-vanille-pavot-2.jpg$$,$$images/cake-vanille-pavot-3.jpg$$],
 true, 0, 70),

('cake-citron-nature', $$Cakes$$, $$Cake Citron (nature)$$,
 $$La fraîcheur du citron dans un cake simple, généreux et délicieusement moelleux.$$,
 ARRAY[$$Cake moelleux citron$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$],
 $j$[{"label":"Cake 25 cm","price":12}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cake-citron-framboise-1.jpg$$],
 true, 0, 80),

('cake-vanille-pavot-nature', $$Cakes$$, $$Cake Vanille-Pavot (nature)$$,
 $$La vanille et le pavot réunis dans un cake moelleux, délicat et naturellement parfumé.$$,
 ARRAY[$$Cake moelleux vanille pavot$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$],
 $j$[{"label":"Cake 25 cm","price":14}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cake-vanille-pavot-1.jpg$$],
 true, 0, 90),

('cannele', $$Petits gâteaux$$, $$Cannelés Bordelais$$,
 $$Une coque intensément caramélisée, un cœur tendre et le parfum de la vanille relevé par les notes du rhum.$$,
 ARRAY[$$Cannelé$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$],
 $j$[{"label":"À l'unité","price":2.40},{"label":"Lot de 3","price":6.80},{"label":"Lot de 6","price":13.30}]$j$::jsonb,
 $j$[{"label":"Sans alcool","options":[{"label":"À l'unité","price":2.40},{"label":"Lot de 3","price":6.80},{"label":"Lot de 6","price":13.30}],"composition":["Cannelé"],"allergenes":["Gluten (blé)","Œufs","Lait"]},{"label":"Au rhum","options":[{"label":"À l'unité","price":2.60},{"label":"Lot de 3","price":7.40},{"label":"Lot de 6","price":14.40}],"composition":["Cannelé"],"allergenes":["Gluten (blé)","Œufs","Lait","Alcool (rhum)"]}]$j$::jsonb,
 $$Préparation$$,
 ARRAY[$$images/cannele-1.jpg$$,$$images/cannele-2.jpg$$,$$images/cannele-3.jpg$$],
 true, 0, 100),

('cookie-pistache', $$Petits gâteaux$$, $$Cookie Deux Chocolats & Pistache$$,
 $$Deux chocolats, un cœur coulant à la pistache. Servi encore tiède, il est à son meilleur.$$,
 ARRAY[$$Farine de blé$$,$$Beurre$$,$$Sucre$$,$$Œufs$$,$$Chocolat noir & au lait$$,$$Pistache$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (pistaches)$$,$$Soja$$],
 $j$[{"label":"À l'unité","price":4.20},{"label":"Lot de 2","price":8},{"label":"Lot de 4","price":15.50}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cookie-1.jpg$$,$$images/cookie-3.jpg$$],
 true, 0, 110),

('cookie-pecan', $$Petits gâteaux$$, $$Cookie Deux Chocolats & Pécan$$,
 $$Deux chocolats et un cœur coulant à la pécan, pour une note plus torréfiée.$$,
 ARRAY[$$Farine de blé$$,$$Beurre$$,$$Sucre$$,$$Œufs$$,$$Chocolat noir & au lait$$,$$Noix de pécan$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (pécan)$$,$$Soja$$],
 $j$[{"label":"À l'unité","price":4.20},{"label":"Lot de 2","price":8},{"label":"Lot de 4","price":15.50}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/cookie-2.jpg$$,$$images/cookie-3.jpg$$],
 true, 0, 120),

('financiers', $$Petits gâteaux$$, $$Financiers Pistache / Noisette$$,
 $$Un financier fondant et généreux où la pistache et la noisette révèlent toute leur intensité.$$,
 ARRAY[$$Financier pistache ou noisette$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$,$$Fruits à coque (amande, pistache, noisette)$$],
 $j$[{"label":"À l'unité","price":2.40},{"label":"Lot de 2","price":4.60},{"label":"Lot de 4","price":9.20},{"label":"Lot de 6","price":14}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/financier-1.jpg$$,$$images/financier-2.jpg$$,$$images/financier-3.jpg$$],
 true, 0, 130),

('madeleines', $$Petits gâteaux$$, $$Madeleines Citron & Vanille$$,
 $$Une madeleine tendre et moelleuse, délicatement parfumée à la vanille ou au citron.$$,
 ARRAY[$$Madeleine moelleuse$$],
 ARRAY[$$Gluten (blé)$$,$$Œufs$$,$$Lait$$],
 $j$[{"label":"À l'unité","price":2},{"label":"Lot de 3","price":5.50},{"label":"Lot de 6","price":10.50}]$j$::jsonb,
 $j$[]$j$::jsonb, $$$$,
 ARRAY[$$images/financier-1.jpg$$],
 true, 0, 140)

on conflict (id) do nothing;
