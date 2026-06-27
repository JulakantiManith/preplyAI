# DNS Configuration Guide

This document describes the DNS records required to deploy the AI Interview & Presentation Coach with a custom domain.

## Overview

The application uses a split-domain architecture:

| Service    | Subdomain Example            | Purpose                          |
| ---------- | ---------------------------- | -------------------------------- |
| Frontend   | `interviewcoach.yourdomain.com` | Main user-facing application     |
| Backend    | `api.interviewcoach.yourdomain.com` | API server                       |
| Auth       | Same as frontend domain      | Supabase auth callback handling  |

## Required DNS Records

### Frontend (A or CNAME)

Point your root application domain to your hosting provider.

| Type  | Name                            | Value                                | TTL  |
| ----- | ------------------------------- | ------------------------------------ | ---- |
| CNAME | `interviewcoach.yourdomain.com` | `your-app.vercel.app` (or hosting provider) | 300  |

If your hosting provider requires an A record (e.g., a VPS or dedicated server):

| Type | Name                            | Value           | TTL  |
| ---- | ------------------------------- | --------------- | ---- |
| A    | `interviewcoach.yourdomain.com` | `<server-ip>`   | 300  |

### Backend API (A or CNAME)

Point the API subdomain to your backend hosting provider.

| Type  | Name                                | Value                                    | TTL  |
| ----- | ----------------------------------- | ---------------------------------------- | ---- |
| CNAME | `api.interviewcoach.yourdomain.com` | `your-api.onrender.com` (or hosting provider) | 300  |

If using an A record:

| Type | Name                                | Value           | TTL  |
| ---- | ----------------------------------- | --------------- | ---- |
| A    | `api.interviewcoach.yourdomain.com` | `<server-ip>`   | 300  |

### Auth Callback Domain

Auth callbacks (email verification, password reset) are handled by the **frontend** domain. No separate DNS record is needed — Supabase redirects users back to paths on the frontend domain (e.g., `/auth/callback`).

## Environment Variable Mapping

Once DNS is configured, update your environment variables:

```env
# Backend .env
APP_DOMAIN=interviewcoach.yourdomain.com
FRONTEND_URL=https://interviewcoach.yourdomain.com
BACKEND_URL=https://api.interviewcoach.yourdomain.com
ALLOWED_ORIGINS=https://interviewcoach.yourdomain.com

# Frontend .env
VITE_APP_DOMAIN=interviewcoach.yourdomain.com
VITE_API_URL=https://api.interviewcoach.yourdomain.com/api/v1
```

## SSL/TLS Certificates

- Most modern hosting providers (Vercel, Render, Railway, Netlify) provision TLS certificates automatically when you add a custom domain.
- If self-hosting, use [Let's Encrypt](https://letsencrypt.org/) with certbot or a reverse proxy like Caddy that handles certificates automatically.
- Ensure both the frontend and backend subdomains have valid HTTPS certificates before going live.

## Verification

After configuring DNS records, verify propagation:

```bash
# Check frontend domain
dig interviewcoach.yourdomain.com

# Check backend domain
dig api.interviewcoach.yourdomain.com

# Verify HTTPS is working
curl -I https://interviewcoach.yourdomain.com
curl -I https://api.interviewcoach.yourdomain.com/api/v1/health
```

DNS propagation can take up to 48 hours, though most changes take effect within minutes to a few hours.
