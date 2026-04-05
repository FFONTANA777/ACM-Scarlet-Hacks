-- Reset
drop table if exists user_checkpoint_stats cascade;
drop table if exists checkins cascade;
drop table if exists profiles cascade;

-- Extends Supabase's built-in auth.users
create table profiles (
  id            uuid references auth.users(id) on delete cascade primary key,
  username      text unique not null,
  pet_name      text default 'Buddy',
  created_at    timestamptz default now()
);

-- Raw check-in log
create table checkins (
  id            uuid default gen_random_uuid() primary key,
  user_id       uuid references profiles(id) on delete cascade,
  checkpoint    text check (checkpoint in ('wake','gym','breakfast','lunch','dinner','sleep')),
  checked_in_at timestamptz default now(),
  hour_float    float,
  day_of_week   int,
  is_weekend    boolean,
  created_at    timestamptz default now()
);

-- Welford running stats per user per checkpoint
create table user_checkpoint_stats (
  id            uuid default gen_random_uuid() primary key,
  user_id       uuid references profiles(id) on delete cascade,
  checkpoint    text check (checkpoint in ('wake','gym','breakfast','lunch','dinner','sleep')),
  day_type      text check (day_type in ('weekday','weekend')),
  mean          float default null,
  variance      float default 0,
  std            float default null,
  n             int   default 0,
  needy_at      float default null,
  updated_at    timestamptz default now(),

  unique(user_id, checkpoint, day_type)
);

-- Indexes
create index on checkins(user_id, checkpoint);
create index on user_checkpoint_stats(user_id, checkpoint, day_type);