-- Enable UUID generation
create extension if not exists "uuid-ossp";

-- User profiles (extends Supabase's built-in auth)
create table public.profiles (
  id            uuid references auth.users(id) primary key,
  display_name  text,
  campus        text,
  created_at    timestamp with time zone default now()
);

-- Outfits (one row per uploaded photo)
create table public.outfits (
  id          uuid default uuid_generate_v4() primary key,
  user_id     uuid references public.profiles(id) not null,
  image_url   text not null,
  created_at  timestamp with time zone default now()
);

-- Analyses (AI output for one outfit)
create table public.analyses (
  id           uuid default uuid_generate_v4() primary key,
  outfit_id    uuid references public.outfits(id) not null,
  pieces_json  jsonb,
  vibes_json   jsonb,
  created_at   timestamp with time zone default now()
);

-- Suggestions (advice after user picks a vibe)
create table public.suggestions (
  id             uuid default uuid_generate_v4() primary key,
  analysis_id    uuid references public.analyses(id) not null,
  selected_vibe  text not null,
  advice_text    text,
  keep_json      jsonb,
  swap_json      jsonb,
  add_json       jsonb,
  tags_json      jsonb,
  created_at     timestamp with time zone default now()
);


-- Turn on RLS for all tables
alter table public.profiles    enable row level security;
alter table public.outfits     enable row level security;
alter table public.analyses    enable row level security;
alter table public.suggestions enable row level security;

-- Profiles: users can only read/write their own
create policy "users can read own profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "users can insert own profile"
  on public.profiles for insert
  with check (auth.uid() = id);

-- Outfits: users can only see their own
create policy "users can read own outfits"
  on public.outfits for select
  using (auth.uid() = user_id);

create policy "users can insert own outfits"
  on public.outfits for insert
  with check (auth.uid() = user_id);

-- Analyses and suggestions: readable if you own the outfit
create policy "users can read own analyses"
  on public.analyses for select
  using (
    exists (
      select 1 from public.outfits
      where outfits.id = analyses.outfit_id
      and outfits.user_id = auth.uid()
    )
  );

create policy "users can read own suggestions"
  on public.suggestions for select
  using (
    exists (
      select 1 from public.analyses
      join public.outfits on outfits.id = analyses.outfit_id
      where analyses.id = suggestions.analysis_id
      and outfits.user_id = auth.uid()
    )
  );  



-- Authenticated users can upload to their own folder
create policy "auth users can upload outfits"
  on storage.objects for insert
  with check (
    bucket_id = 'outfits'
    and auth.role() = 'authenticated'
  );

-- Anyone can read photos (Gemini needs this)
create policy "public can read outfits"
  on storage.objects for select
  using (bucket_id = 'outfits');  