# Supabase Project Settings

This document describes the Supabase dashboard configuration required when deploying with a custom domain.

## Authentication Settings

Navigate to **Authentication → URL Configuration** in your Supabase project dashboard.

### Site URL

Set the Site URL to your production frontend domain:

```
https://interviewcoach.yourdomain.com
```

This is the base URL that Supabase uses to construct email confirmation links and other auth-related URLs.

### Redirect URLs

Add the following redirect URLs so that Supabase allows redirecting users back to your application after auth flows:

| Redirect URL                                              | Purpose                                           |
| --------------------------------------------------------- | ------------------------------------------------- |
| `https://interviewcoach.yourdomain.com/auth/callback`     | OAuth and email verification callback             |
| `https://interviewcoach.yourdomain.com/login`             | Post-logout or session-expired redirect           |
| `https://interviewcoach.yourdomain.com/reset-password`    | Password reset flow landing page                  |
| `https://interviewcoach.yourdomain.com/verify-email`      | Email verification confirmation page              |

For local development, also keep the default localhost entries:

| Redirect URL                              | Purpose               |
| ----------------------------------------- | --------------------- |
| `http://localhost:5173/auth/callback`      | Local dev callback    |
| `http://localhost:5173/login`              | Local dev login       |
| `http://localhost:5173/reset-password`     | Local dev reset       |
| `http://localhost:5173/verify-email`       | Local dev verify      |

### Wildcard Pattern (Optional)

If you use preview/staging deployments (e.g., Vercel preview URLs), you can add a wildcard pattern:

```
https://*-your-project.vercel.app/**
```

## Email Templates

Navigate to **Authentication → Email Templates** in your Supabase dashboard.

Ensure the following templates use the correct redirect URL format:

- **Confirm signup**: Link should redirect to `{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup`
- **Reset password**: Link should redirect to `{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=recovery`
- **Magic link**: Link should redirect to `{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=magiclink`

## Auth Providers (Optional)

If using OAuth providers (Google, GitHub, etc.):

1. Navigate to **Authentication → Providers**
2. For each provider, set the callback URL to:
   ```
   https://<your-supabase-project>.supabase.co/auth/v1/callback
   ```
3. Register this callback URL in the OAuth provider's developer console

## How It Works

The auth redirect flow:

1. User initiates an auth action (sign up, reset password, etc.)
2. Supabase sends an email with a link pointing to the Site URL + auth callback path
3. User clicks the link and is redirected to `https://interviewcoach.yourdomain.com/auth/callback`
4. The frontend handles the callback, establishes the session, and redirects to the appropriate page

The `frontend/src/shared/lib/supabase.ts` module uses `VITE_APP_DOMAIN` to construct these redirect URLs dynamically via `buildAuthRedirectUrl()`.

## Checklist

- [ ] Site URL set to `https://interviewcoach.yourdomain.com`
- [ ] All production redirect URLs added
- [ ] Localhost redirect URLs preserved for local development
- [ ] Email templates verified to use correct redirect paths
- [ ] `VITE_APP_DOMAIN` set in frontend environment
- [ ] `APP_DOMAIN` and `FRONTEND_URL` set in backend environment
- [ ] Test password reset flow end-to-end
- [ ] Test email verification flow end-to-end
