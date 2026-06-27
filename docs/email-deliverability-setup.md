# Email Deliverability Setup Guide

This guide documents the DNS records required for email deliverability (SPF, DKIM, DMARC) and provides step-by-step configuration for popular email providers.

## Overview

Email deliverability depends on three DNS-based authentication mechanisms:

| Mechanism | Purpose | Record Type |
|-----------|---------|-------------|
| **SPF** | Declares which servers may send on your behalf | TXT |
| **DKIM** | Cryptographically signs outgoing messages | TXT or CNAME |
| **DMARC** | Instructs receivers how to handle unauthenticated mail | TXT |

All three should be configured to maximize inbox placement and prevent spoofing.

---

## 1. SPF (Sender Policy Framework)

SPF tells receiving mail servers which IP addresses and services are authorized to send email for your domain.

### Record Format

```
Type:  TXT
Host:  @ (or your domain root)
Value: v=spf1 include:{smtp_provider_spf} ~all
```

### Provider-Specific SPF Includes

| Provider | SPF Include |
|----------|-------------|
| SendGrid | `include:sendgrid.net` |
| AWS SES | `include:amazonses.com` |
| Resend | `include:resend.dev` |
| Mailgun | `include:mailgun.org` |

### Example (Resend)

```
v=spf1 include:resend.dev ~all
```

### Notes

- Use `~all` (softfail) during initial setup for safe rollout; switch to `-all` (hardfail) once verified.
- If using multiple providers, combine them: `v=spf1 include:resend.dev include:_spf.google.com ~all`
- SPF has a 10-DNS-lookup limit. Use `include:` sparingly or consider SPF flattening tools.

---

## 2. DKIM (DomainKeys Identified Mail)

DKIM adds a cryptographic signature to outgoing messages, proving they haven't been tampered with in transit.

### Record Format

Each provider generates a unique DKIM key pair. You add the public key as a DNS record.

```
Type:  TXT or CNAME (provider-dependent)
Host:  {selector}._domainkey.{yourdomain}
Value: (provider-specific public key or CNAME target)
```

### Provider-Specific DKIM Setup

#### SendGrid

SendGrid uses CNAME records for automatic key rotation:

```
Type:  CNAME
Host:  s1._domainkey.yourdomain.com
Value: s1.domainkey.u{account_id}.wl{whitelabel_id}.sendgrid.net

Type:  CNAME
Host:  s2._domainkey.yourdomain.com
Value: s2.domainkey.u{account_id}.wl{whitelabel_id}.sendgrid.net
```

SendGrid rotates keys automatically when CNAME records are used.

#### AWS SES

SES provides three CNAME records for DKIM:

```
Type:  CNAME
Host:  {token1}._domainkey.yourdomain.com
Value: {token1}.dkim.amazonses.com

Type:  CNAME
Host:  {token2}._domainkey.yourdomain.com
Value: {token2}.dkim.amazonses.com

Type:  CNAME
Host:  {token3}._domainkey.yourdomain.com
Value: {token3}.dkim.amazonses.com
```

SES handles key rotation automatically via these CNAME records.

#### Resend

Resend uses a single CNAME record:

```
Type:  CNAME
Host:  resend._domainkey.yourdomain.com
Value: (provided in Resend dashboard under Domains → DNS Records)
```

Resend manages key rotation on their infrastructure.

#### Mailgun

Mailgun provides a TXT record:

```
Type:  TXT
Host:  smtp._domainkey.yourdomain.com
Value: (provided in Mailgun dashboard under Sending → Domains → DNS Records)
```

For automatic rotation, use their CNAME-based approach if available.

### Notes

- DKIM selectors are provider-specific. Always copy exact values from your provider's dashboard.
- Key rotation is handled by the provider when using CNAME records (recommended).
- TXT-based keys require manual rotation (check provider documentation for rotation schedule).

---

## 3. DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC tells receiving servers what to do when SPF or DKIM checks fail, and where to send aggregate reports.

### Recommended Record

```
Type:  TXT
Host:  _dmarc.yourdomain.com
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

### Policy Options

| Policy | Behavior |
|--------|----------|
| `p=none` | Monitor only (receive reports, no enforcement). Use during initial rollout. |
| `p=quarantine` | Move failing messages to spam. Recommended for production. |
| `p=reject` | Reject failing messages outright. Use after confirming legitimate mail passes. |

### Recommended Rollout

1. **Week 1-2:** `p=none` — Collect reports, verify legitimate senders pass SPF/DKIM.
2. **Week 3-4:** `p=quarantine` — Start enforcing without blocking outright.
3. **Week 5+:** `p=reject` — Full enforcement once confident all senders are authenticated.

### Advanced DMARC Options

```
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc-forensics@yourdomain.com; pct=100; adkim=s; aspf=s
```

- `rua` — Aggregate report recipient (daily summaries)
- `ruf` — Forensic report recipient (per-failure details, not all providers support this)
- `pct` — Percentage of messages subject to policy (use 50 for gradual rollout)
- `adkim=s` — Strict DKIM alignment
- `aspf=s` — Strict SPF alignment

---

## Provider-Specific Step-by-Step Guides

### SendGrid

1. **Verify domain** in SendGrid Dashboard → Settings → Sender Authentication → Domain Authentication.
2. **Add SPF:** `v=spf1 include:sendgrid.net ~all`
3. **Add DKIM CNAME records** (provided by SendGrid during domain authentication).
4. **Add DMARC:** `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. **Verify** in SendGrid dashboard — all records should show green checkmarks.

### AWS SES

1. **Verify domain** in AWS Console → SES → Verified Identities → Create Identity.
2. **Add SPF:** `v=spf1 include:amazonses.com ~all`
3. **Add DKIM CNAME records** (3 records provided by SES during domain verification).
4. **Add DMARC:** `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. **Request production access** (SES starts in sandbox mode; submit request to move out).
6. **Verify** — SES dashboard shows "Verified" status for domain.

### Resend

1. **Add domain** in Resend Dashboard → Domains → Add Domain.
2. **Add SPF:** `v=spf1 include:resend.dev ~all`
3. **Add DKIM CNAME record** (provided by Resend during domain setup).
4. **Add DMARC:** `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. **Verify** in Resend dashboard — domain status should change to "Verified".

### Mailgun

1. **Add domain** in Mailgun Dashboard → Sending → Domains → Add New Domain.
2. **Add SPF:** `v=spf1 include:mailgun.org ~all`
3. **Add DKIM TXT record** (provided by Mailgun during domain setup).
4. **Add DMARC:** `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. **Add MX records** if using Mailgun for receiving (optional).
6. **Verify** — Click "Verify DNS Settings" in Mailgun dashboard.

---

## Verification Tools

After configuring DNS records, verify them using these tools:

- [MXToolbox SPF Check](https://mxtoolbox.com/spf.aspx)
- [MXToolbox DKIM Check](https://mxtoolbox.com/dkim.aspx)
- [MXToolbox DMARC Check](https://mxtoolbox.com/dmarc.aspx)
- [Google Admin Toolbox](https://toolbox.googleapps.com/apps/checkmx/)
- [Mail-Tester](https://www.mail-tester.com/) — Send a test email and get a deliverability score

---

## Application Configuration

### Environment Variables

The application includes an optional SMTP health check that verifies connectivity on startup or via a dedicated endpoint.

```bash
# Enable SMTP connectivity verification at startup (default: false)
EMAIL_DELIVERABILITY_CHECK_ENABLED=false
```

### Health Check Endpoint

```
GET /api/v1/health/email
```

Returns SMTP connectivity status without sending an actual email. Verifies that the application can authenticate with the configured SMTP server.

**Response (healthy):**
```json
{
  "status": "healthy",
  "smtp_host": "smtp.resend.com",
  "smtp_port": 465,
  "connection": "authenticated",
  "tls": true
}
```

**Response (unhealthy):**
```json
{
  "status": "unhealthy",
  "smtp_host": "smtp.resend.com",
  "smtp_port": 465,
  "connection": "failed",
  "error": "Connection refused"
}
```

**Response (not configured):**
```json
{
  "status": "disabled",
  "message": "SMTP is not configured"
}
```

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Emails going to spam | Missing or misconfigured SPF/DKIM/DMARC | Verify all 3 records with MXToolbox |
| SPF permerror | Too many DNS lookups (>10) | Consolidate includes or use SPF flattening |
| DKIM signature mismatch | Wrong selector or outdated key | Re-verify DKIM records in provider dashboard |
| DMARC reports show failures | Unauthorized senders or misaligned domains | Check `rua` reports and update SPF/DKIM |
| Health check failing | Incorrect SMTP credentials or firewall blocking | Verify credentials in `.env` and check port access |
