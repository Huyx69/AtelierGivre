-- ════════════════════════════════════════════════════════════════════════
--  Atelier Givre — verrou d'accès admin (à coller dans Supabase → SQL Editor)
--  Restreint les écritures (produits + photos) aux SEULS emails autorisés.
--  ⚠️ Ajoute ici l'email Google de ton pote quand tu l'as, puis relance ce script.
-- ════════════════════════════════════════════════════════════════════════

-- Produits : lecture publique (déjà en place), écriture réservée aux emails autorisés
drop policy if exists "products_admin_write" on public.products;
create policy "products_admin_write"
  on public.products for all
  to authenticated
  using ( (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com'
    -- , 'email-de-ton-pote@gmail.com'
  ) )
  with check ( (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com'
    -- , 'email-de-ton-pote@gmail.com'
  ) );

-- Photos : upload / suppression réservés aux emails autorisés
drop policy if exists "images_admin_write" on storage.objects;
create policy "images_admin_write"
  on storage.objects for all
  to authenticated
  using ( bucket_id = 'product-images' and (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com'
    -- , 'email-de-ton-pote@gmail.com'
  ) )
  with check ( bucket_id = 'product-images' and (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com'
    -- , 'email-de-ton-pote@gmail.com'
  ) );
