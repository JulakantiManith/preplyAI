import { describe, it, expect, vi, beforeEach } from "vitest";
import fc from "fast-check";
import { registerUser } from "./authService";

/**
 * **Validates: Requirements 3.1, 3.2, 3.3**
 *
 * Preservation Property Tests:
 * These tests confirm baseline behavior on UNFIXED code that must remain unchanged
 * after the bug fix is applied. They verify:
 * - Non-rate-limit errors throw with the correct .message
 * - Successful registrations return correct AuthResponse
 */

// Mock supabase module
vi.mock("@/shared/lib/supabase", () => ({
  supabase: {
    auth: {
      signUp: vi.fn(),
    },
  },
  getEmailVerificationUrl: () => "http://localhost:5173/auth/verify-email",
}));

import { supabase } from "@/shared/lib/supabase";

const mockedSignUp = vi.mocked(supabase.auth.signUp);

// Generator for valid registration data
const validRegistrationData = fc.record({
  fullName: fc.string({ minLength: 1, maxLength: 100 }).filter((s) => s.trim().length > 0),
  email: fc.emailAddress(),
  password: fc
    .string({ minLength: 8, maxLength: 128 })
    .filter((p) => /[A-Z]/.test(p) && /[a-z]/.test(p) && /\d/.test(p)),
});

// Generator for non-rate-limit error codes
const nonRateLimitErrorCode = fc.oneof(
  fc.constant("user_already_exists"),
  fc.constant("invalid_credentials"),
  fc.constant("weak_password"),
  fc.constant(undefined),
  fc.string({ minLength: 1, maxLength: 50 }).filter(
    (s) => s !== "over_email_send_rate_limit"
  )
);

// Generator for error messages
const errorMessage = fc.string({ minLength: 1, maxLength: 200 }).filter((s) => s.trim().length > 0);

describe("registerUser - Preservation: Non-Rate-Limit Errors", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should throw an error whose .message matches the Supabase error message for all non-rate-limit error codes", async () => {
    await fc.assert(
      fc.asyncProperty(
        validRegistrationData,
        nonRateLimitErrorCode,
        errorMessage,
        async (data, errorCode, message) => {
          // Mock supabase to return a non-rate-limit error
          mockedSignUp.mockResolvedValue({
            data: { user: null, session: null },
            error: {
              code: errorCode,
              message: message,
              name: "AuthApiError",
              status: 400,
            },
          } as any);

          try {
            await registerUser(data);
            expect.fail("registerUser should have thrown an error");
          } catch (error: any) {
            // Preservation: the thrown error's message must match the Supabase error message
            expect(error.message).toBe(message);
          }
        }
      ),
      { numRuns: 50 }
    );
  });
});

describe("registerUser - Preservation: Successful Registration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return AuthResponse with correct accessToken, tokenType, and user fields for successful registrations", async () => {
    await fc.assert(
      fc.asyncProperty(
        validRegistrationData,
        fc.uuid(),
        fc.string({ minLength: 10, maxLength: 200 }),
        async (data, userId, accessToken) => {
          // Mock supabase to return a successful response
          mockedSignUp.mockResolvedValue({
            data: {
              user: {
                id: userId,
                email: data.email,
                user_metadata: { full_name: data.fullName },
              },
              session: {
                access_token: accessToken,
              },
            },
            error: null,
          } as any);

          const result = await registerUser(data);

          // Preservation: successful registration returns correct AuthResponse
          expect(result.accessToken).toBe(accessToken);
          expect(result.tokenType).toBe("bearer");
          expect(result.user.id).toBe(userId);
          expect(result.user.email).toBe(data.email);
          expect(result.user.fullName).toBe(data.fullName);
        }
      ),
      { numRuns: 50 }
    );
  });
});
