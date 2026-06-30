import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthGate } from "@/components/AuthGate";

const mockFetchResponse = (ok: boolean) =>
  Promise.resolve({
    ok,
  } as Response);

describe("AuthGate", () => {
  it("shows login form when session is not authenticated", async () => {
    const fetchMock = vi.fn().mockImplementation(() => mockFetchResponse(false));
    vi.stubGlobal("fetch", fetchMock);

    render(<AuthGate />);

    expect(await screen.findByRole("heading", { name: /sign in to kanban/i })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/me", {
      credentials: "include",
    });
  });

  it("logs in and logs out", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => mockFetchResponse(false))
      .mockImplementationOnce(() => mockFetchResponse(true))
      .mockImplementationOnce(() => mockFetchResponse(true));
    vi.stubGlobal("fetch", fetchMock);

    render(<AuthGate />);

    await screen.findByRole("heading", { name: /sign in to kanban/i });

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("heading", { name: /kanban studio/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log out/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /log out/i }));

    expect(await screen.findByRole("heading", { name: /sign in to kanban/i })).toBeInTheDocument();
  });
});
