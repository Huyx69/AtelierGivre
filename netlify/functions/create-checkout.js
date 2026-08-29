// ════════════════════════════════════════════════════════════════════════
//  Atelier Givre — création d'une session de paiement Stripe (Netlify Function)
//  Endpoint : POST /.netlify/functions/create-checkout
//
//  Le navigateur envoie UNIQUEMENT les références du panier (clé + quantité).
//  Les PRIX sont recalculés ici, côté serveur, à partir du catalogue ci-dessous :
//  jamais à partir des montants envoyés par le client (sécurité anti-fraude).
//
//  Règle de paiement :
//    • Livraison à domicile ('home')  → paiement de la TOTALITÉ (sous-total + livraison)
//    • Click & collect     ('collect')→ ACOMPTE de 30 % (solde réglé au retrait)
//
//  Variable d'environnement requise (à configurer dans Netlify, JAMAIS dans le code) :
//    STRIPE_SECRET_KEY   → ta clé secrète Stripe (sk_test_... puis sk_live_...)
// ════════════════════════════════════════════════════════════════════════

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// ── Catalogue de confiance : clé de ligne panier → prix unitaire en euros ──
//   La clé suit le format du site : "id@option" ou "id@variante@option".
//   ⚠️ Si tu changes un prix sur le site, mets-le à jour ICI aussi.
const PRICES = {
  // Tartes & entremets
  'trois-citrons@4/6 personnes': 26,
  'trois-citrons@8/10 personnes': 44,
  'peche-verveine@4/6 personnes': 24,
  'peche-verveine@8/10 personnes': 42,
  'choco-cacahuete@4/6 personnes': 24,
  'choco-cacahuete@8/10 personnes': 42,
  'vanille-pistache@4/6 personnes': 26,
  'vanille-pistache@8/10 personnes': 44,
  'manguier@4 personnes': 24,
  'manguier@8 personnes': 42,
  'flan-pecan@4 personnes': 22,
  'flan-pecan@8 personnes': 40,
  // Cakes
  'cake-citron-framboise@Cake 25 cm': 22,
  'cake-vanille-pavot@Cake 25 cm': 22,
  'cake-citron-nature@Cake 25 cm': 12,
  'cake-vanille-pavot-nature@Cake 25 cm': 14,
  // Cannelés (avec variantes) — + repli sans variante
  'cannele@Sans alcool@À l\'unité': 2.40,
  'cannele@Sans alcool@Lot de 3': 6.80,
  'cannele@Sans alcool@Lot de 6': 13.30,
  'cannele@Au rhum@À l\'unité': 2.60,
  'cannele@Au rhum@Lot de 3': 7.40,
  'cannele@Au rhum@Lot de 6': 14.40,
  'cannele@À l\'unité': 2.40,
  'cannele@Lot de 3': 6.80,
  'cannele@Lot de 6': 13.30,
  // Petits gâteaux
  'cookie-pistache@À l\'unité': 4.20,
  'cookie-pistache@Lot de 2': 8,
  'cookie-pistache@Lot de 4': 15.50,
  'cookie-pecan@À l\'unité': 4.20,
  'cookie-pecan@Lot de 2': 8,
  'cookie-pecan@Lot de 4': 15.50,
  'financiers@À l\'unité': 2.40,
  'financiers@Lot de 2': 4.60,
  'financiers@Lot de 4': 9.20,
  'financiers@Lot de 6': 14,
  'madeleines@À l\'unité': 2,
  'madeleines@Lot de 3': 5.50,
  'madeleines@Lot de 6': 10.50,
};

// ── Number Cake : mêmes constantes que le site ──
const NC_PRICE_PER_PERSON = 3.5;
const NC_SUPP_DECOR = 2.5;
const NC_SUPP_FRUITSEC = 1.5;

const DEPOSIT_RATE = 0.30;          // acompte click & collect
const FREE_SHIPPING_FROM = 60;      // livraison offerte à partir de 60 €
const MAX_KM = 20;                  // rayon de livraison
const cents = (eur) => Math.round(eur * 100);

exports.handler = async (event) => {
  const origin = event.headers.origin || (event.headers.host ? 'https://' + event.headers.host : '');
  const headers = { 'Content-Type': 'application/json' };

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }
  if (!process.env.STRIPE_SECRET_KEY) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Stripe non configuré (STRIPE_SECRET_KEY manquant).' }) };
  }

  let payload;
  try { payload = JSON.parse(event.body || '{}'); }
  catch (e) { return { statusCode: 400, headers, body: JSON.stringify({ error: 'Corps invalide' }) }; }

  const items = Array.isArray(payload.items) ? payload.items : [];
  const delivery = payload.delivery === 'home' ? 'home' : 'collect';
  if (!items.length) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Panier vide' }) };
  }

  // ── Reconstruction du panier avec des prix DE CONFIANCE ──
  const lines = [];
  let subtotalCents = 0;
  for (const it of items) {
    const qty = Math.max(1, Math.min(99, parseInt(it.qty, 10) || 0));
    let unit; // euros
    let label;

    if (it.id === 'number-cake') {
      const m = it.meta || {};
      const persons = Math.max(1, parseInt(m.persons, 10) || 0);
      const decors = Math.max(0, parseInt(m.decors, 10) || 0);
      const fruitsSecs = Math.max(0, parseInt(m.fruitsSecs, 10) || 0);
      unit = persons * NC_PRICE_PER_PERSON + decors * NC_SUPP_DECOR + fruitsSecs * NC_SUPP_FRUITSEC;
      label = (it.name || 'Number Cake sur-mesure') + ' (' + persons + ' personnes)';
    } else {
      unit = PRICES[it.key];
      if (unit == null) {
        return { statusCode: 400, headers, body: JSON.stringify({ error: 'Article inconnu : ' + it.key }) };
      }
      // Libellé lisible (cosmétique) ; le prix vient toujours de PRICES, jamais du client.
      label = (it.name || it.key) + (it.opt ? ' — ' + it.opt : '');
    }

    subtotalCents += cents(unit) * qty;
    lines.push({ label, unitCents: cents(unit), qty });
  }

  // ── Frais de livraison (recalculés côté serveur) ──
  let deliveryFeeCents = 0;
  if (delivery === 'home' && subtotalCents < cents(FREE_SHIPPING_FROM)) {
    let km = parseFloat(String(payload.deliveryKm).replace(',', '.'));
    if (!isFinite(km) || km <= 0) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Distance de livraison manquante' }) };
    }
    km = Math.min(km, MAX_KM);
    deliveryFeeCents = cents(km); // 1 €/km
  }

  const totalCents = subtotalCents + deliveryFeeCents;
  const amountDueCents = delivery === 'collect'
    ? Math.round(subtotalCents * DEPOSIT_RATE)   // acompte 30 % (livraison gratuite en collect)
    : totalCents;                                // paiement intégral

  if (amountDueCents < 50) { // minimum Stripe : 0,50 €
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Montant trop faible pour le paiement en ligne.' }) };
  }

  // ── Construction des lignes Stripe ──
  const euros = (c) => (c / 100).toFixed(2).replace('.', ',') + ' €';
  const summary = lines.map((l) => l.qty + '× ' + l.label).join(' | ').slice(0, 480);
  let line_items;

  if (delivery === 'collect') {
    // Un seul poste : l'acompte. Le détail figure dans la description + metadata.
    line_items = [{
      price_data: {
        currency: 'eur',
        unit_amount: amountDueCents,
        product_data: {
          name: 'Acompte 30 % — Commande Atelier Givre (Click & collect)',
          description: ('Total commande ' + euros(totalCents) + ' · solde de ' + euros(totalCents - amountDueCents) + ' à régler au retrait. ' + summary).slice(0, 500),
        },
      },
      quantity: 1,
    }];
  } else {
    // Livraison : chaque article + frais de livraison, paiement intégral.
    line_items = lines.map((l) => ({
      price_data: { currency: 'eur', unit_amount: l.unitCents, product_data: { name: l.label.slice(0, 250) } },
      quantity: l.qty,
    }));
    if (deliveryFeeCents > 0) {
      line_items.push({
        price_data: { currency: 'eur', unit_amount: deliveryFeeCents, product_data: { name: 'Livraison à domicile' } },
        quantity: 1,
      });
    }
  }

  const metadata = {
    fulfillment: delivery,
    sous_total: euros(subtotalCents),
    livraison: euros(deliveryFeeCents),
    total_commande: euros(totalCents),
    paye_maintenant: euros(amountDueCents),
    solde_au_retrait: delivery === 'collect' ? euros(totalCents - amountDueCents) : '0,00 €',
    articles: summary,
  };

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      locale: 'fr',
      line_items,
      metadata,
      payment_intent_data: { metadata },
      phone_number_collection: { enabled: true },
      billing_address_collection: 'auto',
      ...(delivery === 'home' ? { shipping_address_collection: { allowed_countries: ['FR'] } } : {}),
      success_url: origin + '/?paid=1&session_id={CHECKOUT_SESSION_ID}',
      cancel_url: origin + '/?canceled=1',
    });
    return { statusCode: 200, headers, body: JSON.stringify({ url: session.url }) };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Stripe : ' + (err && err.message ? err.message : 'erreur') }) };
  }
};
