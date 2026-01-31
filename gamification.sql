-- Create table for user statistics (streaks, totals)
create table public.user_stats (
  user_id uuid references auth.users not null primary key,
  current_streak int default 0,
  longest_streak int default 0,
  total_sessions int default 0,
  last_session_at timestamptz
);

-- Enable RLS
alter table public.user_stats enable row level security;

-- Policies for user_stats
create policy "Users can view their own stats" on public.user_stats
  for select using (auth.uid() = user_id);

create policy "Users can update their own stats" on public.user_stats
  for update using (auth.uid() = user_id);

create policy "Users can insert their own stats" on public.user_stats
  for insert with check (auth.uid() = user_id);

-- Create table for achievements/badges
create table public.achievements (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  badge_type text not null,
  awarded_at timestamptz default now(),
  unique(user_id, badge_type)
);

-- Enable RLS
alter table public.achievements enable row level security;

-- Policies for achievements
create policy "Users can view their own achievements" on public.achievements
  for select using (auth.uid() = user_id);

create policy "System can insert achievements" on public.achievements
  for insert with check (true); -- Ideally restricted to service role, but for MVP we allow authenticated insert via backend
