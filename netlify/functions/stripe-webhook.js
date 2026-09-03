// ════════════════════════════════════════════════════════════════════════
//  Atelier Givre — notification de commande par email (Netlify Function)
//  Endpoint : POST /.netlify/functions/stripe-webhook
//
//  Stripe appelle cette fonction après CHAQUE paiement réussi
//  (événement « checkout.session.completed »). On envoie alors le détail
//  de la commande par email à l'atelier, via FormSubmit (déjà activé).
//
//  Variables d'environnement requises dans Netlify :
//    STRIPE_SECRET_KEY      → déjà configurée
//    STRIPE_WEBHOOK_SECRET  → fournie par Stripe à la création du webhook (whsec_…)
// ════════════════════════════════════════════════════════════════════════

const Stripe = require('stripe');

const NOTIFY_EMAIL = 'ateliergivre.contact@gmail.com';

exports.handler = async (event) => {
  const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
  const sig = event.headers['stripe-signature'];
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const raw = event.isBase64Encoded ? Buffer.from(event.body, 'base64').toString('utf8') : event.body;

  let stripeEvent;
  try {
    stripeEvent = stripe.webhooks.constructEvent(raw, sig, secret);
  } catch (err) {
    return { statusCode: 400, body: 'Signature webhook invalide : ' + (err && err.message ? err.message : '') };
  }

  if (stripeEvent.type === 'checkout.session.completed') {
    const s = stripeEvent.data.object;
    const m = s.metadata || {};
    const cust = s.customer_details || {};
    const shipAddr = (s.shipping_details && s.shipping_details.address)
      || (s.shipping && s.shipping.address) || null;
    const shipStr = shipAddr
      ? [shipAddr.line1, shipAddr.line2, shipAddr.postal_code, shipAddr.city].filter(Boolean).join(', ')
      : '';
    const home = m.fulfillment === 'home';

    const rows = [
      'NOUVELLE COMMANDE',
      '',
      'Client   : ' + (cust.name || '—'),
      'Email    : ' + (cust.email || '—'),
      'Téléphone: ' + (cust.phone || '—'),
      '',
      'Mode           : ' + (home ? 'Livraison à domicile' : 'Click & collect'),
      'Date souhaitée : ' + (m.date_souhaitee || '—'),
      home ? ('Adresse        : ' + (m.adresse_livraison || shipStr || '—')) : null,
      home ? ('Distance       : ' + (m.distance_km || '—') + ' km') : null,
      '',
      'Articles : ' + (m.articles || '—'),
      '',
      'Sous-total       : ' + (m.sous_total || '—'),
      'Livraison        : ' + (m.livraison || '—'),
      'TOTAL COMMANDE   : ' + (m.total_commande || '—'),
      'Payé maintenant  : ' + (m.paye_maintenant || '—'),
      !home ? ('Solde au retrait : ' + (m.solde_au_retrait || '—')) : null,
    ].filter((x) => x !== null);

    const body = new URLSearchParams({
      _subject: 'Nouvelle commande — Atelier Givre' + (m.date_souhaitee ? (' (pour le ' + m.date_souhaitee + ')') : ''),
      _template: 'box',
      email: cust.email || NOTIFY_EMAIL, // « répondre à » = le client
      Commande: rows.join('\n'),
    });

    try {
      await fetch('https://formsubmit.co/ajax/' + NOTIFY_EMAIL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' },
        body: body.toString(),
      });
    } catch (e) {
      // On n'échoue jamais le webhook pour un email : Stripe le renverrait en boucle.
    }
  }

  return { statusCode: 200, body: JSON.stringify({ received: true }) };
};
