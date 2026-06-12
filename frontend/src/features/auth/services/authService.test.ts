import { describe, it, expect, vi, beforeEach } from "vitest";
import fc from "fast-check";
import { registerUser } from "./authService";

/**
 * **Validates: Requirements 1.1, 1.2, 2.1, 2.2**
 *
 * Bug Condition Exploration Test:
 * When Supabase returns an error with code "over_email_send_rate_limit",
 * registerUser should throw an error that preserves the .code property.
 *
 * On UNFIXED code, this test is EXPECTED TO FAIL because registerUser
 * throws a plain Error without .code.
 */

// Mock supabase module
vi.mock("@/shared/lib/supabase", () => ({
  supabase: {
    auth: {
      signUp: vi.fn(),
    },
  },
}));

import { supabase } from "@/shared/lib/supabase";

const mockedSignUp = vi.mocked(supabase.auth.signUp);

// Generator for valid registration data
const validRegistrationData = fc.record({
  fullName: fc.string({ minLength: 1, maxLength: 100 }).filter((s) => s.trim().length > 0),
  email: fc.emailAddress(),
  password: fc
    .string({ minLength: 8, maxLength: 128 })
    .filter(
      (p) => /[A-Z]/.test(p) && /[a-z]/.test(p) && /\d/.test(p)
    ),
});

describe("registerUser - Bug Condition: Rate Limit Error Code Lost", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should throw an error with .code === 'over_email_send_rate_limit' when Supabase returns rate-limit error", async () => {
    await fc.assert(
      fc.asyncProperty(validRegistrationData, async (data) => {
        // Mock supabase to return rate-limit error
        mockedSignUp.mockResolvedValue({
          data: { user: null, session: null },
          error: {
            code: "over_email_send_rate_limit",
            message: "Email rate limit exceeded",
            name: "AuthApiError",
            status: 429,
          },
        } as any);

        try {
          await registerUser(data);
          // If it doesn't throw, the test should fail
          expect.fail("registerUser should have thrown an error");
        } catch (error: any) {
          // The expected behavior: error should have .code preserved
          expect(error.code).toBe("over_email_send_rate_limit");
        }
      }),
      { numRuns: 20 }
    );
  });
});
