import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { RegisterForm } from "./RegisterForm";

/**
 * **Validates: Requirements 2.1**
 *
 * Bug Condition Exploration Test:
 * When registerUser throws an error with code "over_email_send_rate_limit",
 * RegisterForm should display "Too many attempts. Please wait a few minutes before trying again."
 *
 * On UNFIXED code, this test is EXPECTED TO FAIL because RegisterForm
 * does not check .code and displays the raw error message instead.
 */

// Mock useAuth hook
vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from "../hooks/useAuth";

const mockedUseAuth = vi.mocked(useAuth);

describe("RegisterForm - Bug Condition: Rate Limit Error Display", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display "Too many attempts. Please wait a few minutes before trying again." when rate-limit error occurs', async () => {
    const user = userEvent.setup();

    // Mock useAuth to return a register function that throws with rate-limit code
    const rateLimitError: any = new Error("Email rate limit exceeded");
    rateLimitError.code = "over_email_send_rate_limit";

    mockedUseAuth.mockReturnValue({
      register: vi.fn().mockRejectedValue(rateLimitError),
      login: vi.fn(),
      logout: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: false,
    } as any);

    render(
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    );

    // Fill in form with valid data
    await user.type(screen.getByLabelText(/full name/i), "John Doe");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByPlaceholderText(/create a strong password/i), "StrongPass1");

    // Submit the form
    await user.click(screen.getByRole("button", { name: /create account/i }));

    // Wait for the error message
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toHaveTextContent(
        "Too many attempts. Please wait a few minutes before trying again."
      );
    });
  });
});
