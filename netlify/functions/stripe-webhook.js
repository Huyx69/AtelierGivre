// ════════════════════════════════════════════════════════════════════════
//  Atelier Givre — notification de commande par email (Netlify Function)
//  Endpoint : POST /.netlify/functions/stripe-webhook
//
//  Stripe appelle cette fonction après CHAQUE paiement réussi
//  (événement « checkout.session.completed »). On envoie alors le détail
//  de la commande par email à l'atelier, via Resend (service d'email).
//
//  Variables d'environnement requises dans Netlify :
//    STRIPE_SECRET_KEY      → déjà configurée
//    STRIPE_WEBHOOK_SECRET  → secret du webhook Stripe (whsec_…)
//    RESEND_API_KEY         → clé API Resend (re_…)
// ════════════════════════════════════════════════════════════════════════

const Stripe = require('stripe');

const NOTIFY_EMAIL = 'ateliergivre.contact@gmail.com';
// Expéditeur : l'adresse de test Resend fonctionne sans vérifier de domaine,
// tant que le destinataire est l'email du compte Resend (ateliergivre.contact@gmail.com).
// Plus tard, après avoir vérifié le domaine ateliergivre.fr dans Resend,
// tu pourras mettre par ex. 'Atelier Givre <commandes@ateliergivre.fr>'.
const FROM = 'Atelier Givre <onboarding@resend.dev>';

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

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

    // Paires libellé / valeur (dans l'ordre d'affichage)
    const pairs = [
      ['Client', cust.name || '—'],
      ['Email', cust.email || '—'],
      ['Téléphone', cust.phone || '—'],
      ['Mode', home ? 'Livraison à domicile' : 'Click & collect'],
      ['Date souhaitée', m.date_souhaitee || '—'],
      home ? ['Adresse', m.adresse_livraison || shipStr || '—'] : null,
      home ? ['Distance', (m.distance_km || '—') + ' km'] : null,
      ['Articles', m.articles || '—'],
      ['Sous-total', m.sous_total || '—'],
      ['Livraison', m.livraison || '—'],
      ['TOTAL commande', m.total_commande || '—'],
      ['Payé maintenant', m.paye_maintenant || '—'],
      !home ? ['Solde au retrait', m.solde_au_retrait || '—'] : null,
    ].filter(Boolean);

    const text = 'NOUVELLE COMMANDE — Atelier Givre\n\n'
      + pairs.map(([k, v]) => k + ' : ' + v).join('\n');

    const rowsHtml = pairs.map(([k, v]) => {
      const strong = /TOTAL/.test(k);
      return '<tr>'
        + '<td style="padding:8px 14px;border-bottom:1px solid #EEE;color:#8a98a5;font-size:13px;white-space:nowrap;vertical-align:top;">' + esc(k) + '</td>'
        + '<td style="padding:8px 14px;border-bottom:1px solid #EEE;color:#1A2C3D;font-size:14px;' + (strong ? 'font-weight:700;' : '') + '">' + esc(v) + '</td>'
        + '</tr>';
    }).join('');

    const html = '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;">'
      + '<h2 style="color:#1A2C3D;border-bottom:2px solid #C9A84C;padding-bottom:8px;">Nouvelle commande</h2>'
      + '<table style="width:100%;border-collapse:collapse;">' + rowsHtml + '</table>'
      + '<p style="color:#8a98a5;font-size:12px;margin-top:18px;">Atelier Givre · notification automatique de commande</p>'
      + '</div>';

    if (!process.env.RESEND_API_KEY) {
      return { statusCode: 200, body: JSON.stringify({ received: true, email: 'RESEND_API_KEY manquant' }) };
    }
    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + process.env.RESEND_API_KEY,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: FROM,
          to: [NOTIFY_EMAIL],
          reply_to: cust.email || undefined,
          subject: 'Nouvelle commande — Atelier Givre' + (m.date_souhaitee ? (' (pour le ' + m.date_souhaitee + ')') : ''),
          text,
          html,
        }),
      });
    } catch (e) {
      // On n'échoue pas le webhook pour un email (sinon Stripe le renvoie en boucle).
    }
  }

  return { statusCode: 200, body: JSON.stringify({ received: true }) };
};
