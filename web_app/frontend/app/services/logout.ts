// Centralized client-side logout helper.
// - Clears common auth/session keys from storage
// - Redirects to the provided path (defaults to "/")
export function performLogout(redirectTo: string = "/") {
  try {
    if (typeof window !== "undefined") {
      // Remove various possible token keys used by the app historically
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("username");
      // Remove chat cache so chat session is cleared on explicit logout
      localStorage.removeItem("chatbot_messages");
      // Optionally clear other app-specific caches
      // sessionStorage.clear(); // Uncomment if you also store sensitive data there
    }
  } catch {
    // ignore storage errors
  }
  if (typeof window !== "undefined") {
    // Always show a simple notice with a single OK button before redirecting
    try {
      window.alert("Logged out...");
    } catch {}
    window.location.href = redirectTo;
  }
}
