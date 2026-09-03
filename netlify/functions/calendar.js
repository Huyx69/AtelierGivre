// ════════════════════════════════════════════════════════════════════════
//  Atelier Givre — calendrier abonné des commandes (Netlify Function)
//  Endpoint : GET /.netlify/functions/calendar?key=VOTRE_CLE
//
//  Renvoie un calendrier (format iCalendar) listant toutes les commandes
//  payées, une par date souhaitée. On s'abonne UNE FOIS à ce lien sur
//  l'iPhone (Réglages → Calendrier → Comptes → Ajouter un calendrier
//  avec abonnement), puis chaque nouvelle commande apparaît toute seule.
//
//  Variables d'environnement requises dans Netlify :
//    STRIPE_SECRET_KEY  → déjà configurée
//    CALENDAR_KEY       → une clé secrète au choix (protège l'accès au lien)
// ════════════════════════════════════════════════════════════════════════

const Stripe = require('stripe');

const icsEsc = (t) => String(t == null ? '' : t)
  .replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');

const ymd = (d) => d.getUTCFullYear() + String(d.getUTCMonth() + 1).padStart(2, '0') + String(d.getUTCDate()).padStart(2, '0');

exports.handler = async (event) => {
  const key = (event.queryStringParameters && event.queryStringParameters.key) || '';
  if (!process.env.CALENDAR_KEY || key !== process.env.CALENDAR_KEY) {
    return { statusCode: 401, body: 'Accès refusé.' };
  }
  if (!process.env.STRIPE_SECRET_KEY) {
    return { statusCode: 500, body: 'Stripe non configuré.' };
  }

  const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
  let sessions = [];
  try {
    const res = await stripe.checkout.sessions.list({ limit: 100 });
    sessions = res.data || [];
  } catch (e) {
    return { statusCode: 500, body: 'Erreur Stripe : ' + (e && e.message ? e.message : '') };
  }

  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const events = [];

  for (const s of sessions) {
    if (s.payment_status !== 'paid' && s.status !== 'complete') continue;
    const m = s.metadata || {};
    if (!/^\d{4}-\d{2}-\d{2}$/.test(m.date_iso || '')) continue;

    const start = m.date_iso.replace(/-/g, '');
    const endD = new Date(m.date_iso + 'T00:00:00Z'); endD.setUTCDate(endD.getUTCDate() + 1);
    const end = ymd(endD);

    const cust = s.customer_details || {};
    const home = m.fulfillment === 'home';
    const summary = ('Commande — ' + (m.articles || 'Atelier Givre')).slice(0, 180);
    const location = home ? (m.adresse_livraison || '') : '196 rue du Promenoir, 01300 Belley';
    const desc = [
      'Client : ' + (cust.name || '—'),
      'Téléphone : ' + (cust.phone || '—'),
      'Email : ' + (cust.email || '—'),
      'Mode : ' + (home ? 'Livraison à domicile' : 'Click & collect'),
      home ? ('Adresse : ' + (m.adresse_livraison || '—')) : null,
      'Articles : ' + (m.articles || '—'),
      'Total : ' + (m.total_commande || '—'),
      'Payé : ' + (m.paye_maintenant || '—'),
      !home ? ('Solde au retrait : ' + (m.solde_au_retrait || '—')) : null,
    ].filter(Boolean).join('\n');

    events.push([
      'BEGIN:VEVENT',
      'UID:' + s.id + '@ateliergivre.fr',
      'DTSTAMP:' + stamp,
      'DTSTART;VALUE=DATE:' + start,
      'DTEND;VALUE=DATE:' + end,
      'SUMMARY:' + icsEsc(summary),
      'DESCRIPTION:' + icsEsc(desc),
      'LOCATION:' + icsEsc(location),
      'END:VEVENT',
    ].join('\r\n'));
  }

  const cal = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Atelier Givre//Commandes//FR',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Commandes Atelier Givre',
    'X-WR-TIMEZONE:Europe/Paris',
    ...events,
    'END:VCALENDAR',
  ].join('\r\n');

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/calendar; charset=utf-8',
      'Cache-Control': 'no-cache, max-age=0',
      'Content-Disposition': 'inline; filename="commandes-atelier-givre.ics"',
    },
    body: cal,
  };
};
