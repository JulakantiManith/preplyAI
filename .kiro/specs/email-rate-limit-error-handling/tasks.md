# Implementation Plan

## Overview

This task list implements the bugfix for preserving the Supabase `over_email_send_rate_limit` error code in `registerUser` and displaying a user-friendly message in `RegisterForm`. The workflow follows the bug condition methodology: explore the bug with tests first, write preservation tests, then implement the fix and verify.

## Tasks

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Rate Limit Error Code Lost in registerUser
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Setup**: Install Vitest, @testing-library/react, @testing-library/jest-dom, jsdom, and fast-check as dev dependencies. Configure Vitest in vite.config.ts with jsdom environment
  - **Scoped PBT Approach**: Scope the property to the concrete failing case — mock `supabase.auth.signUp` to return `{ data: { user: null, session: null }, error: { code: "over_email_send_rate_limit", message: "Email rate limit exceeded" } }`
  - Test that calling `registerUser` with any valid registration data when Supabase returns the rate-limit error throws an error that has `.code === "over_email_send_rate_limit"` (from Bug Condition in design: `isBugCondition(input)` where `input.supabaseResponse.error.code == "over_email_send_rate_limit"`)
  - Test that `RegisterForm` displays "Too many attempts. Please wait a few minutes before trying again." when the rate-limit error is thrown (from Expected Behavior in design)
  - Run test on UNFIXED code - expect FAILURE (the thrown `Error` has no `.code` property, and RegisterForm shows raw message)
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found (e.g., "registerUser throws plain Error without .code property", "RegisterForm displays raw 'Email rate limit exceeded' instead of user-friendly message")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Rate-Limit Registration Errors and Success Flow Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe: `registerUser` with Supabase error `{ code: "user_already_exists", message: "User already registered" }` throws Error with message "User already registered" on unfixed code
  - Observe: `registerUser` with Supabase error `{ code: undefined, message: "Some other error" }` throws Error with message "Some other error" on unfixed code
  - Observe: `registerUser` with successful Supabase response returns `AuthResponse` with correct user data on unfixed code
  - Observe: `RegisterForm` displays raw error message for non-rate-limit errors on unfixed code
  - Write property-based test with fast-check: for all generated Supabase error codes that are NOT `"over_email_send_rate_limit"` (from set: `"user_already_exists"`, `"invalid_credentials"`, `"weak_password"`, `undefined`, random strings), `registerUser` throws an error whose `.message` matches the Supabase error message (from Preservation Requirements in design)
  - Write property-based test: for all valid registration inputs with successful Supabase response, `registerUser` returns an `AuthResponse` with correct `accessToken`, `tokenType`, and `user` fields (from Preservation Requirements in design)
  - Write test: `RegisterForm` displays the error `.message` directly for non-rate-limit errors (no special handling)
  - Verify all tests pass on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Fix for rate limit error code lost during registration

  - [x] 3.1 Implement the fix in authService.ts
    - In `registerUser`, replace `throw new Error(error.message || "Registration failed. Please try again.")` with the `AuthError` pattern from `loginUser`:
      ```typescript
      const authError: AuthError = new Error(error.message || "Registration failed. Please try again.");
      authError.code = error.code;
      throw authError;
      ```
    - This preserves the Supabase error code in the thrown error object
    - _Bug_Condition: isBugCondition(input) where input.supabaseResponse.error.code == "over_email_send_rate_limit"_
    - _Expected_Behavior: thrown error has .code === "over_email_send_rate_limit" for rate-limit errors_
    - _Preservation: All non-rate-limit errors still throw with same .message as before_
    - _Requirements: 2.2_

  - [x] 3.2 Implement the fix in RegisterForm.tsx
    - In the `onSubmit` catch block, add a check for the rate-limit error code BEFORE the existing `instanceof Error` check:
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
    - This displays a user-friendly message for rate-limited registration attempts
    - _Bug_Condition: isBugCondition(input) where error.code == "over_email_send_rate_limit"_
    - _Expected_Behavior: RegisterForm displays "Too many attempts. Please wait a few minutes before trying again."_
    - _Preservation: Non-rate-limit errors continue to display error.message or generic fallback_
    - _Requirements: 2.1_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Rate Limit Error Shows User-Friendly Message
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior (error.code preserved, user-friendly message displayed)
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Rate-Limit Errors and Success Flow Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions introduced)
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Checkpoint - Ensure all tests pass
  - Run full test suite with `npx vitest --run`
  - Ensure all property-based tests and unit tests pass
  - Verify no TypeScript compilation errors with `npx tsc --noEmit`
  - Ensure all tests pass, ask the user if questions arise

## Task Dependency Graph

```json
{
  "waves": [
    ["1", "2"],
    ["3.1", "3.2"],
    ["3.3", "3.4"],
    ["4"]
  ]
}
```

## Notes

- Tests use Vitest + fast-check for property-based testing and @testing-library/react for component tests
- The test framework must be set up as part of task 1 since no test runner is currently configured
- The `AuthError` interface already exists in `authService.ts` (used by `loginUser`) — no new types needed
- Mock `supabase.auth.signUp` at the module level for service tests; mock `useAuth` hook for component tests
