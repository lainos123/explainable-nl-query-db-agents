// API utilities for backend interaction (JSON + SSE streaming)
const API_URL = process.env.NEXT_PUBLIC_API_URL

function getAccessToken() {
  if (typeof window === "undefined") return null;
  // Align with rest of app which uses "access_token"
  return localStorage.getItem("access_token");
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = getAccessToken();

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!res.ok) {
    // Bubble up error text/json
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

// Stream agents pipeline via SSE over fetch (works with auth headers)
export type AgentsStreamHandlers = {
  onEvent?: (evt: any) => void; // raw parsed SSE JSON from backend "data: ..."
  onError?: (err: Error) => void;
  onDone?: () => void;
};

export function streamAgents(payload: any, handlers: AgentsStreamHandlers = {}) {
  const { onEvent, onError, onDone } = handlers;
  const token = getAccessToken();
  const controller = new AbortController();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  (async () => {
    try {
      const res = await fetch(`${API_URL}/api/agents/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No readable stream from response");

      // Parse SSE: split on double newlines; process lines starting with 'data:'
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let parts = buffer.split(/\n\n/);
        buffer = parts.pop() || "";
        for (const part of parts) {
          const lines = part.split(/\n/).map(l => l.trim());
          for (const line of lines) {
            if (line.startsWith("data:")) {
              const jsonStr = line.slice(5).trim();
              if (!jsonStr) continue;
              try {
                const evt = JSON.parse(jsonStr);
                onEvent?.(evt);
              } catch (e) {
                // ignore parse error but notify
                onError?.(new Error("Failed to parse SSE data"));
              }
            }
          }
        }
      }
      // Flush leftover buffer (if any complete data line)
      if (buffer.includes("data:")) {
        try {
          const last = buffer.trim().split(/\n/).find(l => l.startsWith("data:"));
          if (last) onEvent?.(JSON.parse(last.slice(5).trim()));
        } catch {}
      }
      onDone?.();
    } catch (err: any) {
      if (err?.name === "AbortError") return; // cancelled
      onError?.(err instanceof Error ? err : new Error(String(err)));
      onDone?.();
    }
  })();

  return {
    cancel: () => controller.abort(),
  };
}

export async function getAgentsLast() {
  return apiFetch("/api/agents/");
}

export async function deleteAgentsCache() {
  return apiFetch("/api/agents/cache/", { method: "DELETE" });
}
