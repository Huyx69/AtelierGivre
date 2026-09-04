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

const Stripe = require('stripe');

// ── Catalogue de confiance : lu depuis Supabase (source unique de vérité) ──
//   La clé de ligne panier suit le format du site : "id@option" ou "id@variante@option".
const SUPABASE_URL = 'https://viuojsmxtvgxmajmpzge.supabase.co';
const SUPABASE_KEY = 'sb_publishable_sLOg6MB-rq1858Xw0kp9pw_eQou1lQl';

// Charge les produits et renvoie une fonction prix(clé) → prix en euros (ou null si inconnu).
async function loadPriceResolver() {
  const r = await fetch(SUPABASE_URL + '/rest/v1/products?select=id,options,variants,active', {
    headers: { apikey: SUPABASE_KEY, Authorization: 'Bearer ' + SUPABASE_KEY },
  });
  if (!r.ok) throw new Error('catalogue indisponible');
  const byId = {};
  (await r.json()).forEach((p) => { byId[p.id] = p; });
  return (key) => {
    const parts = String(key).split('@');
    const p = byId[parts[0]];
    if (!p || p.active === false) return null;
    let opts, optLabel;
    if (parts.length >= 3) {
      const v = (p.variants || []).find((x) => x.label === parts[1]);
      opts = v ? v.options : p.options;
      optLabel = parts.slice(2).join('@');
    } else {
      opts = p.options;
      optLabel = parts.slice(1).join('@');
    }
    const o = (opts || []).find((x) => x.label === optLabel);
    return o ? Number(o.price) : null;
  };
}

// ── Number Cake : mêmes constantes que le site ──
const NC_PRICE_PER_PERSON = 3.5;
// Supplément par garniture (décor ou fruit sec), croissant avec le nombre de parts.
const NC_SUPP_TIERS = [
  { max: 8, price: 2 },
  { max: 12, price: 4 },
  { max: 20, price: 5 },
  { max: 30, price: 6 },
  { max: 40, price: 8 },
  { max: Infinity, price: 10 },
];
const ncSuppPerItem = (persons) => {
  const t = NC_SUPP_TIERS.find((x) => persons <= x.max);
  return t ? t.price : 10;
};

const DEPOSIT_RATE = 0.30;          // acompte click & collect
const FREE_SHIPPING_FROM = 60;      // livraison offerte à partir de 60 € (dans la zone)
const FREE_ZONE_KM = 20;            // zone normale : 1 €/km, offerte dès 60 €
const MAX_KM = 50;                  // limite absolue de livraison
const cents = (eur) => Math.round(eur * 100);

exports.handler = async (event) => {
  const origin = event.headers.origin || (event.headers.host ? 'https://' + event.headers.host : '');
  const headers = { 'Content-Type': 'application/json' };

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }
  if (!process.env.STRIPE_SECRET_KEY) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Stripe non configuré (STRIPE_SECRET_KEY manquant côté Netlify).' }) };
  }
  const stripe = Stripe(process.env.STRIPE_SECRET_KEY);

  let payload;
  try { payload = JSON.parse(event.body || '{}'); }
  catch (e) { return { statusCode: 400, headers, body: JSON.stringify({ error: 'Corps invalide' }) }; }

  const items = Array.isArray(payload.items) ? payload.items : [];
  const delivery = payload.delivery === 'home' ? 'home' : 'collect';
  if (!items.length) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Panier vide' }) };
  }

  // ── Date souhaitée : délai minimum 10 j (number cake) sinon 72 h ──
  const leadDays = items.some((it) => it && it.id === 'number-cake') ? 10 : 3;
  const minDate = new Date(); minDate.setHours(0, 0, 0, 0); minDate.setDate(minDate.getDate() + leadDays);
  const pad = (n) => String(n).padStart(2, '0');
  const minDateStr = minDate.getFullYear() + '-' + pad(minDate.getMonth() + 1) + '-' + pad(minDate.getDate());
  const pickupDate = String(payload.pickupDate || '');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(pickupDate) || pickupDate < minDateStr) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Date de retrait/livraison invalide ou trop proche (délai minimum ' + leadDays + ' jours).' }) };
  }

  // ── Reconstruction du panier avec des prix DE CONFIANCE (lus depuis la base) ──
  let priceOf;
  try {
    priceOf = await loadPriceResolver();
  } catch (e) {
    return { statusCode: 503, headers, body: JSON.stringify({ error: 'Catalogue momentanément indisponible, réessayez.' }) };
  }
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
      // Suppléments : croustillant, gel, compotée + fruits au-delà de 1 frais + 1 sec offerts.
      const suppCount = (m.croustillant ? 1 : 0) + (m.gel ? 1 : 0) + (m.compotee ? 1 : 0)
        + Math.max(0, decors - 1) + Math.max(0, fruitsSecs - 1);
      unit = persons * NC_PRICE_PER_PERSON + suppCount * ncSuppPerItem(persons);
      label = (it.name || 'Number Cake sur-mesure') + ' (' + persons + ' personnes)';
    } else {
      unit = priceOf(it.key);
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
  if (delivery === 'home') {
    const km = parseFloat(String(payload.deliveryKm).replace(',', '.'));
    if (!isFinite(km) || km <= 0) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Distance de livraison manquante' }) };
    }
    if (km > MAX_KM) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Adresse hors zone de livraison (max 50 km).' }) };
    }
    if (km <= FREE_ZONE_KM && subtotalCents >= cents(FREE_SHIPPING_FROM)) {
      deliveryFeeCents = 0; // offerte dans la zone
    } else {
      // 1 €/km + 2 €/km de supplément au-delà de 20 km
      const fee = km * 1 + Math.max(0, km - FREE_ZONE_KM) * 2;
      deliveryFeeCents = cents(fee);
    }
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
    date_souhaitee: pickupDate.split('-').reverse().join('/'),
    date_iso: pickupDate,
    articles: summary,
    ...(delivery === 'home' ? { adresse_livraison: String(payload.address || '').slice(0, 480), distance_km: String(payload.deliveryKm || '') } : {}),
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
