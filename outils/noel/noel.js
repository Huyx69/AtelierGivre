
// ════════════════ ÉDITION NOËL — animations ════════════════
// Ajouté par outils/generer-noel.py. Neige qui tombe (coupable avec le bouton ❄),
// guirlande en chenillard, boules qui tournent et scintillent, boule à neige à secouer.
// Le site est dessiné par React : on écoute les clics sur le document plutôt que
// sur les éléments, qui peuvent être recréés.
(function () {
  'use strict';
  var reduit = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var MEMO = 'ag-neige';

  // ── Neige ──
  var canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:50;';
  var ctx = canvas.getContext('2d');
  var flocons = [];
  var actif = !reduit;
  try { var m = localStorage.getItem(MEMO); if (m === '0') actif = false; else if (m === '1') actif = true; } catch (e) {}
  var l = 0; var h = 0; var dpr = 1;
  function dimensionner() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    l = window.innerWidth; h = window.innerHeight;
    canvas.width = l * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = l < 700 ? 16 : 32; // neige légère
    while (flocons.length < n) flocons.push(nouveau(true));
    flocons.length = n;
  }
  function nouveau(partout) {
    var r = 0.8 + Math.random() * 1.9;
    return { x: Math.random() * l, y: partout ? Math.random() * h : -10, r: r, v: 0.35 + r * 0.22, o: Math.random() * 6.28, a: 0.5 + Math.random() * 0.45 };
  }
  var dernier = 0; var boucle = null;
  function dessiner(t) {
    boucle = requestAnimationFrame(dessiner);
    var dt = Math.min(50, t - (dernier || t)); dernier = t;
    ctx.clearRect(0, 0, l, h);
    for (var i = 0; i < flocons.length; i++) {
      var f = flocons[i];
      f.o += dt * 0.0012;
      f.y += f.v * dt * 0.06;
      f.x += Math.sin(f.o) * 0.35;
      if (f.y > h + 8) { flocons[i] = nouveau(false); continue; }
      ctx.beginPath(); ctx.arc(f.x, f.y, f.r + 0.6, 0, 6.283);
      ctx.fillStyle = 'rgba(120,140,132,' + (f.a * 0.22) + ')'; ctx.fill(); // léger contour : visible aussi sur fond clair
      ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, 6.283);
      ctx.fillStyle = 'rgba(255,255,255,' + f.a + ')'; ctx.fill();
    }
  }
  function demarrer() { if (boucle || !actif || document.hidden) return; dernier = 0; canvas.style.display = ''; boucle = requestAnimationFrame(dessiner); }
  function arreter() { if (boucle) cancelAnimationFrame(boucle); boucle = null; }

  var bouton = document.createElement('button');
  bouton.className = 'xm-bouton-neige';
  bouton.type = 'button';
  bouton.textContent = '❄';
  function majBouton() {
    bouton.setAttribute('aria-pressed', actif ? 'true' : 'false');
    bouton.setAttribute('aria-label', actif ? 'Arrêter la neige' : 'Faire tomber la neige');
    bouton.title = actif ? 'Arrêter la neige' : 'Faire tomber la neige';
  }
  bouton.addEventListener('click', function () {
    actif = !actif;
    try { localStorage.setItem(MEMO, actif ? '1' : '0'); } catch (e) {}
    majBouton();
    if (actif) demarrer(); else { arreter(); ctx.clearRect(0, 0, l, h); canvas.style.display = 'none'; }
  });

  function installer() {
    document.body.appendChild(canvas);
    document.body.appendChild(bouton);
    majBouton();
    dimensionner();
    if (!actif) canvas.style.display = 'none';
    demarrer();
  }
  window.addEventListener('resize', dimensionner);
  document.addEventListener('visibilitychange', function () { if (document.hidden) arreter(); else demarrer(); });
  if (document.body) installer(); else document.addEventListener('DOMContentLoaded', installer);

  // ── Étincelles autour d'un point ──
  function etincelles(x, y, n) {
    if (reduit || !document.body.animate) return;
    for (var i = 0; i < n; i++) {
      var e = document.createElement('span');
      e.className = 'xm-etincelle';
      e.style.left = (x - 3) + 'px'; e.style.top = (y - 3) + 'px';
      document.body.appendChild(e);
      var a = (i / n) * 6.283 + Math.random() * 0.4; var d = 26 + Math.random() * 34;
      e.animate([{ transform: 'translate(0,0) scale(1)', opacity: 1 }, { transform: 'translate(' + Math.cos(a) * d + 'px,' + Math.sin(a) * d + 'px) scale(.2)', opacity: 0 }],
        { duration: 650 + Math.random() * 300, easing: 'cubic-bezier(.2,.7,.3,1)' }).onfinish = (function (el) { return function () { el.remove(); }; })(e);
    }
  }

  document.addEventListener('click', function (ev) {
    if (reduit) return;
    // Guirlande : chenillard.
    var g = ev.target.closest && ev.target.closest('.xm-guirlande');
    if (g) {
      g.querySelectorAll('i').forEach(function (b, i) {
        b.animate([{ filter: 'brightness(1)' }, { filter: 'brightness(2.4) saturate(1.4)' }, { filter: 'brightness(1)' }], { duration: 420, delay: i * 45 });
      });
      return;
    }
    // Boule : un tour sur elle-même et des étincelles.
    var b = ev.target.closest && ev.target.closest('.xm-boule');
    if (b) {
      // « add » : le tour s'ajoute au balancement en cours au lieu de le remplacer (pas de saut).
      b.animate([{ transform: 'rotate(0deg)' }, { transform: 'rotate(-22deg)' }, { transform: 'rotate(16deg)' }, { transform: 'rotate(-8deg)' }, { transform: 'rotate(0deg)' }], { duration: 1100, easing: 'ease-out', composite: 'add' });
      etincelles(ev.clientX, ev.clientY, 12);
      return;
    }
    // Boule à neige : on la secoue, la neige tourbillonne.
    var s = ev.target.closest && ev.target.closest('.xm-globe-boule');
    if (s) {
      s.animate([{ transform: 'rotate(0)' }, { transform: 'rotate(-10deg)' }, { transform: 'rotate(9deg)' }, { transform: 'rotate(-6deg)' }, { transform: 'rotate(3deg)' }, { transform: 'rotate(0)' }], { duration: 700, easing: 'ease-in-out' });
      s.querySelectorAll('.xm-globe-verre i').forEach(function (f) {
        var dx = (Math.random() - 0.5) * 80; var dy = -40 - Math.random() * 60;
        f.animate([{ transform: 'translate(0,' + (40 + Math.random() * 60) + 'px)' }, { transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'translate(' + (-dx / 2) + 'px,120px)' }],
          { duration: 2600 + Math.random() * 1600, easing: 'cubic-bezier(.25,.6,.35,1)' });
      });
    }
  });
})();
