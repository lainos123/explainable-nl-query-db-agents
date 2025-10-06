// fetch.ts — apiFetch and helpers
import { getAccessToken, tryRefresh } from "./auth";
import { performLogout } from "./logout";
import { API_URL } from "./config";

const MAX_ATTEMPTS = 10;
const BACKOFF_BASE_MS = 300;

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}

function messagesToMarkdown(messages: any[]): string {
  const mdParts: string[] = ["# Chat history\n\n"];
  for (const m of messages) {
    const t = m?.createdAt ? new Date(m.createdAt).toISOString() : "";
    const sender = m?.sender || "user";
    mdParts.push(`**${sender}** - ${t}\n\n`);
    mdParts.push((m?.text || "") + "\n\n---\n\n");
  }
  return mdParts.join("");
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  let token = getAccessToken();

  const normalizedEndpoint = endpoint || "";
  const isDownloadEndpoint = /download-chat-md\/?$/.test(normalizedEndpoint);
  let bodyToSend: any = options.body;
  let headers = { ...(options.headers || {}) } as Record<string, any>;

  if (isDownloadEndpoint) {
    try {
      if (typeof options.body === "string") {
        const parsed = JSON.parse(options.body);
        if (parsed && Array.isArray(parsed.messages)) {
          bodyToSend = messagesToMarkdown(parsed.messages);
          headers["Content-Type"] = "text/markdown";
        }
      } else if (
        options.body &&
        typeof options.body === "object" &&
        !(options.body instanceof FormData)
      ) {
        const maybe = options.body as any;
        if (maybe.messages && Array.isArray(maybe.messages)) {
          bodyToSend = messagesToMarkdown(maybe.messages);
          headers["Content-Type"] = "text/markdown";
        }
      }
    } catch (e) {
      // fallback
    }
  } else {
    if (options.body && !(options.body instanceof FormData)) {
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }
  }

  if (
    bodyToSend &&
    !(bodyToSend instanceof FormData) &&
    typeof bodyToSend !== "string"
  ) {
    try {
      bodyToSend = JSON.stringify(bodyToSend);
    } catch {}
  }

  let lastErr: any = null;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        body: bodyToSend,
        headers: {
          ...headers,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      // Auth errors: try refresh once
      if (res.status === 401 || res.status === 403) {
        const ok = await tryRefresh();
        if (ok) {
          token = getAccessToken();
          const retried = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            body: bodyToSend,
            headers: {
              ...headers,
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
          });
          if (!retried.ok) {
            if (retried.status === 401 || retried.status === 403) {
              performLogout("/");
              return;
            }
            throw new Error(`HTTP ${retried.status}`);
          }
          const ct2 = retried.headers.get("content-type") || "";
          if (ct2.includes("application/json")) return retried.json();
          return retried.text();
        } else {
          performLogout("/");
          return;
        }
      }

      if (!res.ok) {
        if (res.status >= 500 && attempt < MAX_ATTEMPTS) {
          lastErr = new Error(`HTTP ${res.status}`);
          await delay(BACKOFF_BASE_MS * attempt);
          continue;
        }
        const text = await res.text().catch(() => "");
        throw new Error(text || `HTTP ${res.status}`);
      }

      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) return res.json();
      return res.text();
    } catch (err: any) {
      lastErr = err;
      if (attempt < MAX_ATTEMPTS) {
        await delay(BACKOFF_BASE_MS * attempt);
        continue;
      }
      throw err;
    }
  }
  throw lastErr || new Error("Request failed after retries");
}

export default apiFetch;
