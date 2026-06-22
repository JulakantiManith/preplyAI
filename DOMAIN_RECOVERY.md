# Domain Recovery Procedure

This document describes how to recover full application functionality when a custom domain expires, DNS becomes misconfigured, or you need to switch between domain configurations. **No source code changes, database schema changes, or infrastructure recreation are required.**

---

## Prerequisites

You need access to:
- **Vercel Dashboard** (Frontend deployment)
- **Render Dashboard** (Backend deployment)
- **Supabase Dashboard** (Authentication configuration)

The original Vercel (`*.vercel.app`) and Render (`*.onrender.com`) platform URLs **always continue working**, even while a custom domain is configured. They serve as your emergency fallback.

---

## Recovery Steps

### Step 1: Update Environment Variables

Update the following variables in each service to point to the desired URLs.

#### Vercel (Frontend)

Go to: **Vercel Dashboard → Project → Settings → Environment Variables**

| Variable | Custom Domain Value | Recovery (Platform URL) Value |
|----------|-------------------|-------------------------------|
| `VITE_APP_DOMAIN` | `myapp.com` | *(leave empty or remove)* |
| `VITE_API_URL` | `https://api.myapp.com` | `https://your-app.onrender.com` |

#### Render (Backend)

Go to: **Render Dashboard → Service → Environment**

| Variable | Custom Domain Value | Recovery (Platform URL) Value |
|----------|-------------------|-------------------------------|
| `APP_DOMAIN` | `myapp.com` | *(leave empty or remove)* |
| `FRONTEND_URL` | `https://myapp.com` | `https://your-app.vercel.app` |
| `BACKEND_URL` | `https://api.myapp.com` | `https://your-app.onrender.com` |
| `ALLOWED_ORIGINS` | `https://myapp.com,https://your-app.vercel.app` | `https://your-app.vercel.app` |

> **Note:** SMTP variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_SENDER_EMAIL`, `SMTP_SENDER_NAME`) are independent of the domain and do not need to change during recovery.

---

### Step 2: Update Supabase Auth Redirect URLs

Go to: **Supabase Dashboard → Authentication → URL Configuration**

1. **Site URL**: Set to your active frontend URL (e.g., `https://your-app.vercel.app`)
2. **Redirect URLs**: Add/update the following entries to include your active frontend URL:
   - `https://your-app.vercel.app/**`
   - `https://your-app.vercel.app/auth/callback`
   - `https://your-app.vercel.app/auth/reset-password`

If recovering from a custom domain, you may remove the custom domain redirect entries or leave them (they won't cause harm).

---

### Step 3: Redeploy Services

1. **Redeploy Backend** on Render:
   - Go to Render Dashboard → Service → Manual Deploy → "Deploy latest commit"
   - Wait for deployment to complete and health check to pass

2. **Redeploy Frontend** on Vercel:
   - Go to Vercel Dashboard → Project → Deployments → Redeploy
   - Or push an empty commit / trigger a redeployment from the dashboard

---

### Step 4: Verify Recovery

1. Open the frontend at the platform URL (`https://your-app.vercel.app`)
2. Confirm the app loads without errors
3. Test login/registration to verify auth redirects work
4. Test an API call to confirm CORS and backend connectivity

---

## Domain Configuration Scenarios

### Scenario A: Custom Domain (All Variables Populated)

All services use your custom domain. This is the standard production configuration.

| Service | Variable | Example Value |
|---------|----------|---------------|
| Vercel | `VITE_APP_DOMAIN` | `myapp.com` |
| Vercel | `VITE_API_URL` | `https://api.myapp.com` |
| Render | `APP_DOMAIN` | `myapp.com` |
| Render | `FRONTEND_URL` | `https://myapp.com` |
| Render | `BACKEND_URL` | `https://api.myapp.com` |
| Render | `ALLOWED_ORIGINS` | `https://myapp.com,https://your-app.vercel.app` |
| Supabase | Site URL | `https://myapp.com` |
| Supabase | Redirect URLs | `https://myapp.com/**` |

### Scenario B: Platform URLs Only (All Domain Variables Empty/Unset)

No custom domain is configured. The app runs entirely on Vercel and Render default URLs. This is the recovery configuration when a domain expires.

| Service | Variable | Value |
|---------|----------|-------|
| Vercel | `VITE_APP_DOMAIN` | *(empty or unset)* |
| Vercel | `VITE_API_URL` | `https://your-app.onrender.com` |
| Render | `APP_DOMAIN` | *(empty or unset)* |
| Render | `FRONTEND_URL` | `https://your-app.vercel.app` |
| Render | `BACKEND_URL` | `https://your-app.onrender.com` |
| Render | `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| Supabase | Site URL | `https://your-app.vercel.app` |
| Supabase | Redirect URLs | `https://your-app.vercel.app/**` |

When `VITE_APP_DOMAIN` is empty, the frontend automatically uses the current browser origin (the Vercel deployment URL) for all redirect URLs and internal links.

When `APP_DOMAIN` is empty, the backend starts in default-URL mode using fallback values.

### Scenario C: Mixed (Frontend Custom Domain, No APP_DOMAIN)

A hybrid configuration where the frontend uses a custom domain but `APP_DOMAIN` is not set. Useful for partial migrations or when only DNS for the frontend is configured.

| Service | Variable | Value |
|---------|----------|-------|
| Vercel | `VITE_APP_DOMAIN` | `myapp.com` |
| Vercel | `VITE_API_URL` | `https://your-app.onrender.com` |
| Render | `APP_DOMAIN` | *(empty or unset)* |
| Render | `FRONTEND_URL` | `https://myapp.com` |
| Render | `BACKEND_URL` | `https://your-app.onrender.com` |
| Render | `ALLOWED_ORIGINS` | `https://myapp.com,https://your-app.vercel.app` |
| Supabase | Site URL | `https://myapp.com` |
| Supabase | Redirect URLs | `https://myapp.com/**,https://your-app.vercel.app/**` |

---

## Important Notes

- **Platform URLs always work.** The original `*.vercel.app` and `*.onrender.com` URLs remain functional at all times, regardless of custom domain configuration. They are your guaranteed recovery path.
- **No code changes needed.** Recovery is purely a configuration operation — environment variables, Supabase settings, and redeployment.
- **No database changes needed.** The database schema is completely independent of domain configuration.
- **No infrastructure recreation needed.** Existing Vercel and Render services continue to function; only their environment variables change.
- **SMTP is domain-independent.** Email configuration (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_SENDER_EMAIL, SMTP_SENDER_NAME) does not depend on APP_DOMAIN and does not need updating during domain recovery.
- **Include platform URLs in ALLOWED_ORIGINS.** Always keep the Vercel deployment URL in ALLOWED_ORIGINS so CORS permits requests from the platform URL even when a custom domain is active. This ensures immediate fallback capability.

---

## Quick Recovery Checklist

Use this checklist when a custom domain expires or DNS fails:

- [ ] Update `VITE_APP_DOMAIN` on Vercel (clear it or set to empty)
- [ ] Update `VITE_API_URL` on Vercel to Render platform URL
- [ ] Update `APP_DOMAIN` on Render (clear it or set to empty)
- [ ] Update `FRONTEND_URL` on Render to Vercel platform URL
- [ ] Update `BACKEND_URL` on Render to Render platform URL
- [ ] Update `ALLOWED_ORIGINS` on Render to include Vercel platform URL
- [ ] Update Supabase Site URL to Vercel platform URL
- [ ] Update Supabase Redirect URLs to include Vercel platform URL patterns
- [ ] Redeploy Backend on Render
- [ ] Redeploy Frontend on Vercel
- [ ] Verify: Frontend loads at platform URL
- [ ] Verify: Login/registration works
- [ ] Verify: API calls succeed (no CORS errors)
