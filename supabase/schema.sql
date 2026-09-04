-- ════════════════════════════════════════════════════════════════════════
--  Atelier Givre — structure de la base (à coller dans Supabase → SQL Editor)
--  Crée la table des produits + les règles de sécurité + le stockage photos.
-- ════════════════════════════════════════════════════════════════════════

-- 1) Table des produits ----------------------------------------------------
create table if not exists public.products (
  id            text primary key,               -- identifiant court, ex. 'trois-citrons'
  category      text not null,                  -- 'Tartes & entremets', 'Cakes', ...
  name          text not null,
  description   text default '',
  composition   text[]  default '{}',           -- liste des éléments
  allergenes    text[]  default '{}',           -- liste des allergènes
  options       jsonb   default '[]'::jsonb,    -- [{ "label": "4/6 personnes", "price": 26 }]
  variants      jsonb   default '[]'::jsonb,    -- pour les produits à variantes (cannelés…)
  images        text[]  default '{}',           -- URLs des photos (stockage Supabase)
  active        boolean default true,           -- affiché sur le site ?
  promo_percent integer default 0,              -- remise en % (0 = pas de promo)
  sort_order    integer default 0,              -- ordre d'affichage
  updated_at    timestamptz default now()
);

-- 2) Sécurité (Row Level Security) ----------------------------------------
alter table public.products enable row level security;

-- Tout le monde peut LIRE les produits (site public)
drop policy if exists "products_public_read" on public.products;
create policy "products_public_read"
  on public.products for select
  using (true);

-- Seul un utilisateur CONNECTÉ peut créer / modifier / supprimer (dashboard)
drop policy if exists "products_admin_write" on public.products;
create policy "products_admin_write"
  on public.products for all
  to authenticated
  using (true)
  with check (true);

-- 3) Stockage des photos ---------------------------------------------------
insert into storage.buckets (id, name, public)
values ('product-images', 'product-images', true)
on conflict (id) do nothing;

-- Lecture publique des photos
drop policy if exists "images_public_read" on storage.objects;
create policy "images_public_read"
  on storage.objects for select
  using (bucket_id = 'product-images');

-- Upload / modification / suppression réservés aux utilisateurs connectés
drop policy if exists "images_admin_write" on storage.objects;
create policy "images_admin_write"
  on storage.objects for all
  to authenticated
  using (bucket_id = 'product-images')
  with check (bucket_id = 'product-images');
