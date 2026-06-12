# Email Rate Limit Error Handling Bugfix Design

## Overview

When Supabase returns an `over_email_send_rate_limit` error during registration, the application currently displays the raw error message or a generic fallback because `registerUser` throws a plain `Error` without preserving the error code. The fix will preserve the error code using the existing `AuthError` interface (already used in `loginUser`) and add a code-specific check in `RegisterForm` to display a user-friendly message: "Too many attempts. Please wait a few minutes before trying again."

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug — when `registerUser` encounters an `over_email_send_rate_limit` error code from Supabase and the code is lost because a plain `Error` is thrown
- **Property (P)**: The desired behavior — rate-limited registration attempts display "Too many attempts. Please wait a few minutes before trying again."
- **Preservation**: Existing error handling for non-rate-limit registration errors, successful registrations, and login `email_not_confirmed` handling must remain unchanged
- **registerUser**: The function in `frontend/src/features/auth/services/authService.ts` that calls `supabase.auth.signUp` and handles errors
- **AuthError**: The interface in `authService.ts` extending `Error` with an optional `code` property, currently used only by `loginUser`
- **RegisterForm**: The component in `frontend/src/features/auth/components/RegisterForm.tsx` that calls `registerUser` via `useAuth` and renders error messages

## Bug Details

### Bug Condition

The bug manifests when a user triggers Supabase's email send rate limit during registration. The `registerUser` function throws a plain `Error(error.message)` which discards the `error.code` property. Without the code, `RegisterForm` cannot distinguish rate-limit errors from other failures and falls back to displaying the raw Supabase message.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type { registrationAttempt: RegisterFormData, supabaseResponse: SupabaseAuthError }
  OUTPUT: boolean
  
  RETURN input.supabaseResponse.error IS NOT NULL
         AND input.supabaseResponse.error.code == "over_email_send_rate_limit"
END FUNCTION
```

### Examples

- **Example 1**: User registers with `test@example.com`, Supabase returns `{ code: "over_email_send_rate_limit", message: "Email rate limit exceeded" }`. **Expected**: "Too many attempts. Please wait a few minutes before trying again." **Actual**: "Email rate limit exceeded" (raw message displayed)
- **Example 2**: User rapidly re-submits registration form 5 times in a row. **Expected**: friendly rate-limit message on subsequent attempts. **Actual**: raw/confusing Supabase error text
- **Example 3**: User registers with valid data, Supabase succeeds. **Expected**: navigate to login with verification message. **Actual**: works correctly (not a bug condition)
- **Edge case**: User gets a different error (e.g., "User already registered" with no rate-limit code). **Expected**: the Supabase message is displayed as-is. **Actual**: works correctly (not a bug condition)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Non-rate-limit registration errors (e.g., "User already registered") must continue to display the Supabase error message or the generic fallback as they do today
- Successful registration must continue to navigate the user to `/login` with the verification prompt message
- Login flow's `email_not_confirmed` error handling in `LoginForm` must remain unchanged
- The `loginUser` function's error handling pattern (already using `AuthError` with code) must remain unchanged
- All other auth service functions (`logoutUser`, `forgotPassword`, `resetPassword`) must remain unchanged

**Scope:**
All inputs that do NOT involve a Supabase `over_email_send_rate_limit` error code during registration should be completely unaffected by this fix. This includes:
- Successful registrations
- Registration failures with other error codes
- All login attempts (successful and failed)
- Password reset flows
- Logout operations

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Error Code Discarded in `registerUser`**: On line 35 of `authService.ts`, the error handler throws `new Error(error.message)` — a plain `Error` object. The Supabase error's `.code` property is logged to console but not preserved in the thrown error. Compare with `loginUser` (line 66-67) which correctly creates an `AuthError` and attaches `authError.code = error.code`.

2. **No Code-Specific Handling in `RegisterForm`**: The `onSubmit` catch block in `RegisterForm.tsx` only checks `error instanceof Error` and displays `error.message`. There is no check for `error.code === "over_email_send_rate_limit"` to display a user-friendly message. Compare with `LoginForm` which checks `err.code === "email_not_confirmed"` for specialized messaging.

## Correctness Properties

Property 1: Bug Condition - Rate Limit Error Shows User-Friendly Message

_For any_ registration attempt where Supabase returns an error with code `over_email_send_rate_limit`, the fixed `registerUser` function SHALL throw an `AuthError` preserving the code, and `RegisterForm` SHALL display "Too many attempts. Please wait a few minutes before trying again." instead of the raw error message.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Non-Rate-Limit Errors and Other Flows Unchanged

_For any_ registration attempt where Supabase returns an error that is NOT `over_email_send_rate_limit`, or where registration succeeds, or for any login/logout/password-reset operation, the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing error messages, navigation, and functionality.

**Validates: Requirements 3.1, 3.2, 3.3**

## Fix Implementation

### Changes Required

**File**: `frontend/src/features/auth/services/authService.ts`

**Function**: `registerUser`

**Specific Changes**:
1. **Preserve error code**: Replace `throw new Error(error.message || "Registration failed. Please try again.")` with the `AuthError` pattern already used in `loginUser`:
   ```typescript
   const authError: AuthError = new Error(error.message || "Registration failed. Please try again.");
   authError.code = error.code;
   throw authError;
   ```

---

**File**: `frontend/src/features/auth/components/RegisterForm.tsx`

**Function**: `onSubmit` (catch block)

**Specific Changes**:
2. **Add rate-limit code check**: Before displaying the raw error message, check if the error has `code === "over_email_send_rate_limit"` and display the user-friendly message:
   ```typescript
   } catch (error) {
     const err = error as { code?: string; message?: string };
     if (err.code === "over_email_send_rate_limit") {
       setFormError("Too many attempts. Please wait a few minutes before trying again.");
     } else if (error instanceof Error) {
       setFormError(error.message);
     } else {
       setFormError("Registration failed. Please try again.");
     }
   }
   ```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Mock `supabase.auth.signUp` to return an error with `code: "over_email_send_rate_limit"`. Call `registerUser` and inspect the thrown error object. Render `RegisterForm` and trigger a registration that hits the rate limit. Observe the displayed message. Run these tests on the UNFIXED code to observe failures.

**Test Cases**:
1. **Service Layer Test**: Call `registerUser` when Supabase returns `{ code: "over_email_send_rate_limit", message: "Email rate limit exceeded" }` — assert the thrown error has a `.code` property (will fail on unfixed code)
2. **Component Display Test**: Render `RegisterForm`, simulate rate-limit error from service — assert the displayed message is "Too many attempts. Please wait a few minutes before trying again." (will fail on unfixed code)
3. **Error Code Preservation Test**: Verify the thrown error is an instance that carries both `.message` and `.code` (will fail on unfixed code because plain `Error` has no `.code`)

**Expected Counterexamples**:
- The thrown error from `registerUser` lacks a `.code` property
- `RegisterForm` displays raw "Email rate limit exceeded" instead of the user-friendly message
- Root cause confirmed: plain `Error` discards the code

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := registerUser_fixed(input)
  ASSERT result.thrownError.code == "over_email_send_rate_limit"
  ASSERT displayedMessage == "Too many attempts. Please wait a few minutes before trying again."
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT registerUser_original(input) = registerUser_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (various error codes, messages, success scenarios)
- It catches edge cases that manual unit tests might miss (e.g., `undefined` code, empty message)
- It provides strong guarantees that behavior is unchanged for all non-rate-limit errors

**Test Plan**: Observe behavior on UNFIXED code first for non-rate-limit errors and successful registrations, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Non-Rate-Limit Error Preservation**: Verify errors like "User already registered" (code: `user_already_exists`) still display the Supabase message as-is
2. **Successful Registration Preservation**: Verify successful signups still return `AuthResponse` and navigation works
3. **Login email_not_confirmed Preservation**: Verify LoginForm still handles `email_not_confirmed` code correctly
4. **Generic Error Preservation**: Verify errors without an `instanceof Error` check still show "Registration failed. Please try again."

### Unit Tests

- Test `registerUser` throws `AuthError` with code preserved for rate-limit errors
- Test `registerUser` throws `AuthError` with code preserved for other Supabase errors
- Test `RegisterForm` displays user-friendly message when error code is `over_email_send_rate_limit`
- Test `RegisterForm` displays raw error message for non-rate-limit errors
- Test `RegisterForm` displays generic fallback for non-Error exceptions

### Property-Based Tests

- Generate random Supabase error codes (from a realistic set) and verify that only `over_email_send_rate_limit` triggers the user-friendly message, while all other codes display the error's message
- Generate random registration inputs with successful Supabase responses and verify `AuthResponse` is returned unchanged
- Generate various error shapes (with/without code, with/without message) and verify error handling remains consistent

### Integration Tests

- Test full registration flow with rate-limit error end-to-end (mock at Supabase boundary)
- Test full registration flow with success end-to-end (verify navigation to /login)
- Test that LoginForm's email_not_confirmed handling is unaffected after the fix
