# Bugfix Requirements Document

## Introduction

When a user attempts to register and Supabase returns an email rate limit error (error code `over_email_send_rate_limit`), the application displays the raw Supabase error message or a generic "Registration failed. Please try again." message. This is confusing and unhelpful to users who don't understand what went wrong or what action to take. The fix should display a clear, user-friendly message explaining they need to wait before trying again.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user attempts to register and Supabase returns an error with code `over_email_send_rate_limit` THEN the system displays the raw Supabase error message (e.g., "Email rate limit exceeded") or a generic "Registration failed. Please try again." message

1.2 WHEN a user attempts to register and Supabase returns an error with code `over_email_send_rate_limit` THEN the system loses the error code information because `registerUser` throws a plain `Error` object without preserving the `code` property

### Expected Behavior (Correct)

2.1 WHEN a user attempts to register and Supabase returns an error with code `over_email_send_rate_limit` THEN the system SHALL display a user-friendly message: "Too many attempts. Please wait a few minutes before trying again."

2.2 WHEN a user attempts to register and Supabase returns an error with code `over_email_send_rate_limit` THEN the system SHALL preserve the Supabase error code in the thrown error object (using the `AuthError` interface with a `code` property, consistent with the existing `loginUser` pattern)

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user attempts to register and Supabase returns an error that is NOT a rate limit error (e.g., "User already registered", invalid credentials) THEN the system SHALL CONTINUE TO display the Supabase error message or the generic fallback message as it does today

3.2 WHEN a user attempts to register with valid data and Supabase succeeds THEN the system SHALL CONTINUE TO navigate the user to the login page with a verification prompt message

3.3 WHEN a user attempts to log in and Supabase returns an `email_not_confirmed` error THEN the system SHALL CONTINUE TO display the email verification prompt message in the LoginForm
