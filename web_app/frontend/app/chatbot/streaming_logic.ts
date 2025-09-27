// Separator and formatting helpers (merged from streaming_presenting.ts)
export const SEP = "\n\n------------------------\n\n";

export function formatAgentOutput(text: string, agent?: string, lastAgent?: string): string {
  // Add separator if agent changes
  if (agent && lastAgent && agent !== lastAgent) {
    return SEP + text;
  }
  return text;
}
// Standardized stream output rendering
export function renderStreamData(data: any): string {
  // Check for error JSON first
  if (data && typeof data === "object" && (data.error || data.success === false)) {
    if (data.error) return `❌ **Error:** ${data.error}`;
    if (data.success === false) return `⚠️ **Failed:** ${data.message || "Unknown error"}`;
  }

  let out = "";
  const keys = ["query", "database", "tables", "columns", "SQL", "reasons", "result"];
  let hasKnownKey = false;

  if (data.query) {
    out += `### Query\n\`${data.query}\`\n\n`;
    hasKnownKey = true;
  }
  if (data.database) {
    out += `**Database:** ${data.database}\n\n`;
    hasKnownKey = true;
  }
  if (data.tables) {
    out += `**Tables:** ${Array.isArray(data.tables) ? data.tables.join(", ") : data.tables}\n\n`;
    hasKnownKey = true;
  }
  if (data.columns) {
    out += `**Columns:** ${Array.isArray(data.columns) ? data.columns.join(", ") : data.columns}\n\n`;
    hasKnownKey = true;
  }
  if (data.SQL) {
    out += `### SQL\n\`\`\`sql\n${data.SQL}\n\`\`\`\n\n`;
    hasKnownKey = true;
  }
  if (data.reasons) {
    out += `> ${data.reasons}\n\n`;
    hasKnownKey = true;
  }
  if (data.result) {
    const headers = Object.keys(data.result[0] || {});
    const rows = data.result.map((r: any) => `| ${headers.map(h => r[h]).join(" | ")} |`);
    out += `### Result\n| ${headers.join(" | ")} |\n| ${headers.map(() => "---").join(" | ")} |\n${rows.join("\n")}\n\n`;
    hasKnownKey = true;
  }

  // If no known keys, render full JSON
  if (!hasKnownKey) {
    return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
  }

  return out || "ℹ️ No data parsed.";
}
import type { ChatMessage } from "./page";
import { streamAgents, deleteAgentsCache, apiFetch } from "../services/api";

export function useStreamingLogic(setMessages: (fn: (prev: ChatMessage[]) => ChatMessage[]) => void, setLoadingBot: (v: boolean) => void) {
  const genId = () => crypto.randomUUID();

  const sendUserMessage = (text: string) => {
    if (!text.trim()) return;
    const userMsg: ChatMessage = { id: genId(), sender: "user", text: text.trim(), createdAt: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setLoadingBot(true);
    const botId = genId();
    setMessages((prev) => [...prev, { id: botId, sender: "bot", text: "", createdAt: Date.now() }]);
    let lastAgent: string | null = null;
    streamAgents({ query: userMsg.text }, {
      onEvent: (evt) => {
        const isContent = !!(evt && (evt.output || evt.error));
          // If server sends usage payload mid-stream, update local cache and notify listeners
          if (evt && evt.usage) {
            try {
              localStorage.setItem("usage_cache", JSON.stringify(evt.usage));
            } catch (e) {}
            try {
              window.dispatchEvent(new CustomEvent("usage_updated", { detail: evt.usage }));
            } catch (e) {}
          }
        let sepNow = false;
        if (isContent && evt?.agent) {
          if (lastAgent && evt.agent !== lastAgent) sepNow = true;
          lastAgent = evt.agent;
        }
        if (evt?.output) {
          const chunk = JSON.stringify(evt.output);
          setMessages((prev) => prev.map(m => {
            if (m.id !== botId) return m;
            const prefix = m.text ? (sepNow ? SEP : "\n") : "";
            return { ...m, text: (m.text || "") + prefix + chunk };
          }));
        } else if (evt?.error) {
          setMessages((prev) => prev.map(m => {
            if (m.id !== botId) return m;
            const prefix = m.text ? (sepNow ? SEP : "\n") : "";
            return { ...m, text: (m.text || "") + prefix + `Error: ${evt.error}` };
          }));
        }
      },
      onError: (err) => {
        setMessages((prev) => prev.map(m => m.id === botId ? { ...m, text: (m.text ? m.text + "\n" : "") + `\n[Stream error] ${err.message}` } : m));
      },
      onDone: async () => {
        // Chat finished streaming
        setLoadingBot(false);
        try {
          const data = await apiFetch('/api/core/usage/');
          if (typeof data === 'undefined' || !data) return;
          try { localStorage.setItem('usage_cache', JSON.stringify(data)); } catch (e) {}
          try { window.dispatchEvent(new CustomEvent('usage_updated', { detail: data })); } catch (e) {}
        } catch (e) {
          // network or other failure; do nothing so UI keeps cached usage
        }
        // Persist latest chat messages to server (background sync). This ensures server has
        // the full conversation when a stream completes. Only attempt if user is authenticated.
        try {
          const token = localStorage.getItem('access_token');
          if (token) {
            try {
              const raw = localStorage.getItem('chatbot_messages') || '[]';
              const messages = JSON.parse(raw);
              if (Array.isArray(messages)) {
                await apiFetch('/api/core/chats/', { method: 'POST', body: JSON.stringify({ messages }) });
              }
            } catch (e) {
              // ignore any persistence failures
            }
          }
        } catch (e) {}
      },
    });
  };

  return { sendUserMessage };
}
