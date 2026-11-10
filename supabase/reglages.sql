-- ════════════════════════════════════════════════════════════════════════
--  Atelier Givre — réglages du site (à coller dans Supabase → SQL Editor)
--  Crée la table des réglages, avec le thème actif du site (normal,
--  halloween, noel), choisi dans l'admin.
--  Lecture publique (le site doit savoir quel thème afficher),
--  écriture réservée aux emails autorisés (les mêmes que dans security.sql).
-- ════════════════════════════════════════════════════════════════════════

create table if not exists public.site_settings (
  key        text primary key,          -- ex. 'theme'
  value      text not null,             -- ex. 'noel'
  updated_at timestamptz default now()
);

alter table public.site_settings enable row level security;

drop policy if exists "settings_public_read" on public.site_settings;
create policy "settings_public_read"
  on public.site_settings for select
  using (true);

drop policy if exists "settings_admin_write" on public.site_settings;
create policy "settings_admin_write"
  on public.site_settings for all
  to authenticated
  using ( (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com',
    'givresebastien@gmail.com'
  ) )
  with check ( (auth.jwt() ->> 'email') in (
    'ateliergivre.contact@gmail.com',
    'tiago270106@gmail.com',
    'givresebastien@gmail.com'
  ) );

-- Thème au démarrage : Noël (on le change ensuite dans l'admin).
insert into public.site_settings (key, value) values ('theme', 'noel')
on conflict (key) do nothing;
