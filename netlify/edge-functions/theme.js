// Atelier Givre — page d'accueil servie directement dans le thème actif.
//
// Le thème (normal, halloween, noel) est choisi dans l'admin et enregistré dans
// Supabase (table site_settings). Cette fonction, exécutée par Netlify avant la
// page, renvoie tout de suite le bon fichier (site-noel.html…) à l'adresse « / » :
// Google, les robots des IA et les aperçus de liens lisent ainsi le vrai contenu,
// sans attendre le JavaScript. En cas de souci, on laisse passer : index.html
// choisit alors le thème dans le navigateur, comme avant.
//
// Elle redirige aussi l'ancienne adresse ateliergivre.netlify.app vers ateliergivre.fr.

const SUPABASE_URL = 'https://viuojsmxtvgxmajmpzge.supabase.co';
const SUPABASE_KEY = 'sb_publishable_sLOg6MB-rq1858Xw0kp9pw_eQou1lQl';
const THEMES = { normal: '/site-normal.html', halloween: '/site-halloween.html', noel: '/site-noel.html' };
const DEFAUT = 'noel'; // même thème par défaut que index.html
const DUREE_MEMO = 60 * 1000; // on redemande le thème à Supabase au plus une fois par minute

let memo = { theme: null, depuis: 0 };

async function themeActif() {
  if (memo.theme && Date.now() - memo.depuis < DUREE_MEMO) return memo.theme;
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/site_settings?key=eq.theme&select=value`, {
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` },
      signal: AbortSignal.timeout(1500),
    });
    const lignes = r.ok ? await r.json() : [];
    const t = lignes && lignes[0] && lignes[0].value;
    memo = { theme: THEMES[t] ? t : DEFAUT, depuis: Date.now() };
  } catch (e) {
    memo = { theme: memo.theme || DEFAUT, depuis: Date.now() - DUREE_MEMO / 2 };
  }
  return memo.theme;
}

export default async (request, context) => {
  const url = new URL(request.url);
  if (url.hostname === 'ateliergivre.netlify.app') {
    return Response.redirect(`https://ateliergivre.fr/${url.search}`, 301);
  }
  // Aperçu d'un thème (/?theme=noel) : c'est index.html qui s'en occupe.
  if (url.searchParams.has('theme')) return;
  try {
    return context.rewrite(THEMES[await themeActif()]);
  } catch (e) {
    return; // index.html prend le relais
  }
};

export const config = { path: '/' };
