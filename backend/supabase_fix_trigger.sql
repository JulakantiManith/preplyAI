-- ============================================================================
-- FIX: "Database error saving new user" during registration
-- ============================================================================
-- Root Cause: The handle_new_user() trigger fires on auth.users INSERT but
-- fails because:
-- 1. The function's search_path doesn't include 'extensions' schema where
--    uuid_generate_v4() lives in Supabase
-- 2. The function may not have proper permissions to insert into public.profiles
--
-- Run these queries in Supabase SQL Editor to diagnose and fix.
-- ============================================================================

-- ============================================================================
-- STEP 1: DIAGNOSTIC QUERIES (run these first to confirm the issue)
-- ============================================================================

-- Check if uuid-ossp extension exists and which schema it's in
SELECT extname, extnamespace::regnamespace as schema
FROM pg_extension
WHERE extname = 'uuid-ossp';

-- Check all triggers on auth.users
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'auth'
  AND event_object_table = 'users';

-- Check the handle_new_user function definition
SELECT proname, prosrc, proconfig
FROM pg_proc
WHERE proname = 'handle_new_user';

-- Check profiles table structure
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'profiles'
ORDER BY ordinal_position;

-- Check if there are any failed auth attempts in logs
SELECT id, email, created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 5;

-- ============================================================================
-- STEP 2: THE FIX — Drop and recreate the trigger function
-- ============================================================================

-- Drop the existing trigger first
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Drop the existing function
DROP FUNCTION IF EXISTS handle_new_user();

-- Recreate with explicit schema references and proper search_path
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
BEGIN
  INSERT INTO public.profiles (id, user_id, created_at, updated_at)
  VALUES (
    gen_random_uuid(),
    NEW.id,
    now(),
    now()
  )
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$;

-- Recreate the trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- STEP 3: VERIFY THE FIX
-- ============================================================================

-- Test that the function exists with correct config
SELECT proname, prosrc, proconfig
FROM pg_proc
WHERE proname = 'handle_new_user';

-- Verify trigger is attached
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'auth'
  AND event_object_table = 'users'
  AND trigger_name = 'on_auth_user_created';

-- ============================================================================
-- ALTERNATIVE FIX (if gen_random_uuid is also not found):
-- Use the extensions schema explicitly
-- ============================================================================

-- If the above still fails, try this version instead:
-- 
-- CREATE OR REPLACE FUNCTION public.handle_new_user()
-- RETURNS TRIGGER
-- LANGUAGE plpgsql
-- SECURITY DEFINER
-- SET search_path = public
-- AS $$
-- BEGIN
--   INSERT INTO public.profiles (id, user_id, created_at, updated_at)
--   VALUES (
--     extensions.uuid_generate_v4(),
--     NEW.id,
--     now(),
--     now()
--   )
--   ON CONFLICT (user_id) DO NOTHING;
--   RETURN NEW;
-- END;
-- $$;

-- ============================================================================
-- NUCLEAR OPTION: If you want to remove the trigger entirely and create
-- profiles on first API access instead (simpler, no trigger dependency):
-- ============================================================================

-- DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
-- DROP FUNCTION IF EXISTS handle_new_user();
--
-- Then handle profile creation in the backend profile_service.py:
-- When GET /profile returns no profile, create one on the fly.
