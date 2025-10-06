// sse.ts — streamAgents implementation
import { getAccessToken, tryRefresh } from "./auth";
import { performLogout } from "./logout";
import { API_URL } from "./config";

const MAX_ATTEMPTS = 10;
const BACKOFF_BASE_MS = 300;

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}

export type AgentsStreamHandlers = {
  onEvent?: (evt: any) => void;
  onError?: (err: Error) => void;
  onDone?: () => void;
};

export function streamAgents(
  payload: any,
  handlers: AgentsStreamHandlers = {}
) {
  const { onEvent, onError, onDone } = handlers;
  const controller = new AbortController();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  (async () => {
    try {
      let res: Response | null = null;
      for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        const tokenNow = getAccessToken();
        try {
          res = await fetch(`${API_URL}/api/agents/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(tokenNow ? { Authorization: `Bearer ${tokenNow}` } : {}),
            },
            body: JSON.stringify(payload),
            signal: controller.signal,
          });
        } catch (err) {
          if (attempt < MAX_ATTEMPTS) {
            await delay(BACKOFF_BASE_MS * attempt);
            continue;
          }
          onError?.(err instanceof Error ? err : new Error(String(err)));
          onDone?.();
          return;
        }

        if (!res) break;
        if (res.ok) break;

        if (res.status === 401 || res.status === 403) {
          const refreshed = await tryRefresh();
          if (refreshed) {
            continue; // retry
          } else {
            performLogout("/");
            return;
          }
        }

        if (res.status >= 500 && attempt < MAX_ATTEMPTS) {
          await delay(BACKOFF_BASE_MS * attempt);
          continue;
        }

        onError?.(new Error(`HTTP ${res.status}`));
        onDone?.();
        return;
      }

      if (!res) {
        onError?.(new Error("No response from server"));
        onDone?.();
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        onError?.(new Error("No readable stream from response"));
        onDone?.();
        return;
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() || "";
        for (const part of parts) {
          const lines = part.split(/\r?\n/).map((l) => l.trim());
          for (const line of lines) {
            if (!line || line.startsWith(":")) continue;
            if (line.startsWith("data:")) {
              const jsonStr = line.slice(5).trim();
              if (!jsonStr) continue;
              try {
                const evt = JSON.parse(jsonStr);
                if (evt.status === "finished") {
                  onDone?.();
                  return;
                }
                onEvent?.(evt);
              } catch (e) {
                onError?.(new Error("Failed to parse SSE data"));
              }
            }
          }
        }
      }

      if (buffer) {
        try {
          const lines = buffer.trim().split(/\r?\n/).map((l) => l.trim());
          const lastData = lines.reverse().find((l) => l.startsWith("data:"));
          if (lastData) {
            const evt = JSON.parse(lastData.slice(5).trim());
            if (evt.status === "finished") {
              onDone?.();
              return;
            }
            onEvent?.(evt);
          }
        } catch {}
      }

      onDone?.();
    } catch (err: any) {
      if (err?.name === "AbortError") return;
      onError?.(err instanceof Error ? err : new Error(String(err)));
      onDone?.();
    }
  })();

  return {
    cancel: () => controller.abort(),
  };
}

export default streamAgents;
