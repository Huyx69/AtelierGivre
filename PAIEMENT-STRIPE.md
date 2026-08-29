# Mise en place du paiement Stripe — Atelier Givre

Le site appelle une petite fonction serverless (Netlify) qui crée la session de
paiement Stripe avec le bon montant :

- **Livraison à domicile** → le client paie **la totalité** (sous-total + livraison).
- **Click & collect** → le client paie **un acompte de 30 %**, le solde est réglé au retrait.

Les prix sont **recalculés côté serveur** (fichier `netlify/functions/create-checkout.js`) :
personne ne peut trafiquer le montant depuis le navigateur.

---

## 1. Créer le compte Stripe (gratuit, sans abonnement)

1. Va sur **https://dashboard.stripe.com/register** et crée le compte de l'Atelier
   (email `ateliergivre.contact@gmail.com`).
2. Renseigne les informations de l'entreprise (auto-entrepreneur, IBAN pour recevoir
   les virements). Tu peux commencer à tester **avant** d'avoir tout validé, en **mode Test**.
3. Récupère la **clé secrète** :
   - Menu **Développeurs → Clés API**.
   - **Mode Test** d'abord : copie la clé `sk_test_...`.
   - Plus tard, en **mode Live** : la clé sera `sk_live_...`.

> ⚠️ Ne colle **jamais** cette clé secrète dans le code, ni dans un message. Elle se
> configure uniquement dans Netlify (étape 3).

---

## 2. Ajouter les fichiers au dépôt

Ces fichiers ont été créés dans le projet — ajoute-les au dépôt GitHub `Huyx69/Atelier-givre` :

```
netlify.toml
package.json
netlify/functions/create-checkout.js
```

(+ la nouvelle version de `index.html` une fois la maquette publiée — voir étape 4.)

---

## 3. Configurer la clé secrète dans Netlify

1. Ouvre ton site sur **https://app.netlify.com** → **Site configuration → Environment variables**.
2. Ajoute une variable :
   - **Key** : `STRIPE_SECRET_KEY`
   - **Value** : ta clé `sk_test_...` (puis `sk_live_...` en production)
3. Enregistre. Netlify installera automatiquement la dépendance `stripe` (grâce au `package.json`).

---

## 4. Publier le site

La logique de paiement est dans la maquette `Atelier Givre v2.dc.html`. **Publie / synchronise**
la maquette pour régénérer `index.html`, puis laisse Netlify redéployer (ou pousse sur `main`).

---

## 5. Tester (mode Test)

1. Sur le site, ajoute un produit au panier.
2. **Click & collect** → le panier affiche « Acompte à payer maintenant (30 %) » + le solde.
   **Livraison** → montant total.
3. Clique sur le bouton de paiement → tu arrives sur la page Stripe.
4. Carte de test Stripe : `4242 4242 4242 4242`, date future, CVC `123`, code postal quelconque.
5. Après paiement → retour sur le site avec l'écran « Commande confirmée ».
6. Vérifie dans **Stripe → Paiements** : montant, et dans les **métadonnées** le détail
   (total, acompte, solde au retrait, articles).

---

## 6. Passer en production (Live)

1. Active le compte Stripe (validation d'identité + IBAN).
2. Remplace la variable Netlify `STRIPE_SECRET_KEY` par la clé `sk_live_...`.
3. Refais un test avec une vraie carte (petit montant) pour confirmer.

---

## Notifications de commande

- Le client reçoit automatiquement un **reçu Stripe** par email.
- Toi, tu vois chaque commande dans le **dashboard Stripe** (avec le détail en métadonnées).
- Pour recevoir un **email récapitulatif** à chaque commande, on pourra ajouter un
  *webhook* Stripe plus tard (dis-le-moi si tu veux).

## Si un prix change sur le site

Mets à jour le **même prix** dans `netlify/functions/create-checkout.js` (objet `PRICES`),
sinon la commande sera refusée (« Article inconnu »).
