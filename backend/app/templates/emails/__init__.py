"""Branded HTML email templates for Supabase Auth authentication flows.

These templates are designed to be configured in the Supabase Dashboard
under Authentication → Email Templates. They use Supabase's template
variables ({{ .ConfirmationURL }}, {{ .Token }}, {{ .SiteURL }}, {{ .Email }})
which are automatically injected at send time.

Templates:
- verification_email.html: Email address verification after signup
- password_reset_email.html: Password recovery/reset flow
- magic_link_email.html: Passwordless magic link login
- otp_email.html: One-time password verification code

All templates feature:
- Responsive table-based layouts for email client compatibility
- Dark/light mode support via @media (prefers-color-scheme: dark)
- Inline CSS for maximum rendering consistency
- Branded header with app identity
- Security notices and expiration warnings
- Fallback text links for accessibility
- Footer with site link and contact info
"""
