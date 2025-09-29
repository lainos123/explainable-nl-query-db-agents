"use client";

import React from "react";
import { useRouter } from 'next/navigation';
import { apiFetch } from "../services/api";
import { deleteAgentsCache } from "../services/api";

interface MenuProps {
  minimized: boolean;
  setMinimized: (m: boolean) => void;
  username?: string | null;
  onRequestLogout?: () => void;
}

const Menu: React.FC<MenuProps> = ({ minimized, setMinimized, username, onRequestLogout }) => {
  if (minimized) return null;

  // single source of truth: usage comes from agents API cache or SSE usage events
  const usageApi = `http://localhost:8000/api/core/usage/`;
  const agentsApi = `http://localhost:8000/api/agents/`;
  const getToken = () => localStorage.getItem("access_token");

  // backend now may return a slim usage object; make fields optional
  const [usage, setUsage] = React.useState<{
    max_chats?: number;
    max_gb?: number;
    chats_used_today?: number;
    used_bytes?: number;
    max_bytes?: number;
    seconds_until_reset?: number;
  } | null>(null);

  // countdown to usage reset (server-provided). We'll store seconds_until_reset and optionally server_time
  const [countdown, setCountdown] = React.useState<string>('-');
  // internal state to keep remaining seconds (derived from server seconds_until_reset)
  const [remainingSeconds, setRemainingSeconds] = React.useState<number | null>(null);

  React.useEffect(() => {
    // live tick: decrement remainingSeconds if present
    const tick = () => {
      setRemainingSeconds((s) => {
        if (s == null) return s;
        const ns = Math.max(0, s - 1);
        return ns;
      });
    };
    const iv = setInterval(tick, 1000);
    return () => clearInterval(iv);
  }, []);

  const router = useRouter();

  // format remainingSeconds into readable countdown
  React.useEffect(() => {
    if (remainingSeconds == null) {
      setCountdown('-');
      return;
    }
    const sec = Math.max(0, Math.floor(remainingSeconds || 0));
    const days = Math.floor(sec / (24 * 3600));
    const hrs = Math.floor((sec % (24 * 3600)) / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = sec % 60;
    setCountdown(`${days}d ${hrs}h ${mins}m ${secs}s`);
  }, [remainingSeconds]);

  React.useEffect(() => {
    const token = getToken();
    if (!token) return;
    let mounted = true;
    // Initialize from local cache first
    try {
      const cached = localStorage.getItem("usage_cache");
      if (cached) {
        const parsed = JSON.parse(cached);
        if (parsed && mounted) {
          setUsage(parsed);
          if (typeof parsed.seconds_until_reset === 'number') setRemainingSeconds(Math.max(0, Math.floor(parsed.seconds_until_reset)));
        }
      }
    } catch (e) {
      // ignore parse errors
    }

    // Try to fetch recent cached agents result which may include usage in the same response.
    // Behavior: Do a single GET attempt. If it returns 404 (no cache), start a one-time POST
    // to /api/agents/ to trigger the pipeline, but don't retry on failure or disconnect.
    const fetchFromAgentsCache = async () => {
      try {
        const tokenNow = getToken();
        if (!tokenNow) {
          // No token available; skip calling agents API entirely
          return;
        }
        // use full URL so we can inspect status codes directly
        let res: Response | null = null;
        try {
          res = await fetch(agentsApi, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${tokenNow}`,
            },
          });
        } catch (_) {
          // Network or CORS error; fall back to usage endpoint below
          res = null;
        }

        if (!mounted) return;

        if (res && res.status === 200) {
          const agentsData = await res.json().catch(() => null);
          if (!mounted) return;
          const u = agentsData?.usage || agentsData;
          if (u) {
            setUsage(u);
            try { localStorage.setItem('usage_cache', JSON.stringify(u)); } catch {}
            if (typeof u.seconds_until_reset === 'number') setRemainingSeconds(Math.max(0, Math.floor(u.seconds_until_reset)));
            return;
          }
        }

        // If 404 => no cached result: start a one-time pipeline run (POST) but don't await the full stream
        if (res && res.status === 404) {
          try {
            // fire-and-forget start: backend will stream SSE; we intentionally don't keep the connection
            // open here (if client disconnects it's fine per requirement). We still include auth.
            fetch(agentsApi, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${tokenNow}`,
              },
              body: JSON.stringify({}),
            }).catch(() => {});
          } catch (_) {
            // ignore any start errors; we'll fallback to usage endpoint below
          }
        }

        // Fallback: request the usage endpoint (always safe)
        try {
          const udata = await apiFetch('/api/core/usage/');
          if (!mounted) return;
          if (udata) {
            setUsage(udata);
            try { localStorage.setItem('usage_cache', JSON.stringify(udata)); } catch {}
            if (typeof udata.seconds_until_reset === 'number') setRemainingSeconds(Math.max(0, Math.floor(udata.seconds_until_reset)));
          }
        } catch (e) {
          // ignore errors; rely on cached usage
        }
      } catch (e) {
        // ignore errors; rely on cached usage
      }
    };

    // initial fetch attempt
    fetchFromAgentsCache();

    // listen for usage updates dispatched elsewhere (e.g. SSE stream or agents cache update)
    const onUsageUpdated = (e: any) => {
      try {
        const d = e?.detail;
        if (d) {
          setUsage(d);
          try { localStorage.setItem("usage_cache", JSON.stringify(d)); } catch {}
          if (typeof d.seconds_until_reset === 'number') setRemainingSeconds(Math.max(0, Math.floor(d.seconds_until_reset)));
        }
      } catch (_) {}
    };
    window.addEventListener("usage_updated", onUsageUpdated as EventListener);

    // no need to poll here — countdown handled by remainingSeconds and SSE events.
    const interval = setInterval(() => {}, 1000);

    return () => {
      mounted = false;
      clearInterval(interval);
      window.removeEventListener("usage_updated", onUsageUpdated as EventListener);
    };
  }, []);

  // Local UI loading flags
  const [downloadLoading, setDownloadLoading] = React.useState(false);

  const fmtHMS = (s: number) => {
    const sec = Math.max(0, Math.floor(s || 0));
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const ss = sec % 60;
    return `${h}h ${m}m ${ss}s`;
  };


  return (
    <div className="flex flex-col gap-4">
      {/* User info + logout/minimize */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-violet-600 text-white grid place-items-center text-xs">
            {(username?.[0] || "?").toUpperCase()}
          </div>
          <div className="truncate">
            <div className="text-sm font-medium truncate" title={username || undefined}>
              {username || "User"}
            </div>
          </div>
        </div>
        {/* empty space reserved for bottom usage card */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              // Open logout confirmation (actual clearing happens in performLogout)
              onRequestLogout?.();
            }}
            className="inline-flex items-center gap-1 rounded-full h-8 px-3 text-xs font-medium text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-sm backdrop-blur-md transition-colors"
            title="Logout"
            aria-label="Logout"
          >
            <svg
              className="w-3.5 h-3.5 text-gray-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>Logout</span>
          </button>
          <button
            onClick={() => setMinimized(true)}
            className="inline-flex items-center gap-1 rounded-full h-8 px-3 text-xs font-medium text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-sm backdrop-blur-md transition-colors"
            title="Minimize menu"
            aria-label="Minimize menu"
          >
            <svg
              className="w-3.5 h-3.5 text-gray-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Hide</span>
          </button>
        </div>
      </div>

      {/* Parameter Selection Section */}
      <div className="mt-4 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="text-xs font-semibold text-gray-300 mb-3">Agent Parameters</div>
        
        {/* LLM Model */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 block mb-1">LLM Model:</label>
          <select 
            className="w-full px-2 py-1 bg-gray-900 text-white text-xs rounded border border-gray-600"
            defaultValue="gpt-5-mini"
            onChange={(e) => {
              localStorage.setItem('agent_llm_model', e.target.value);
            }}
          >
            <option value="gpt-5-mini">GPT-5 Mini (Default)</option>
            <option value="gpt-4o-mini">GPT-4o Mini (Fast)</option>
            <option value="gpt-4o">GPT-4o (Advanced)</option>
            <option value="gpt-4">GPT-4 (Legacy)</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Legacy)</option>
          </select>
        </div>

        {/* Top-K Similar Schemas */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 block mb-1">Top-K Similar Schemas (Agent A):</label>
          <input 
            type="number" 
            min="1" 
            max="20" 
            defaultValue="5"
            className="w-full px-2 py-1 bg-gray-900 text-white text-xs rounded border border-gray-600"
            onChange={(e) => {
              localStorage.setItem('agent_top_k', e.target.value);
            }}
          />
        </div>

        {/* Include Reasons */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 block mb-1">Show Reasoning:</label>
          <select 
            className="w-full px-2 py-1 bg-gray-900 text-white text-xs rounded border border-gray-600"
            defaultValue="false"
            onChange={(e) => {
              localStorage.setItem('agent_include_reasons', e.target.value);
              // Trigger re-render of current messages
              window.dispatchEvent(new CustomEvent('agent_params_changed'));
            }}
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>

        {/* Include Agent Process */}
        <div className="mb-0">
          <label className="text-xs text-gray-400 block mb-1">Show Detailed Description of Agent:</label>
          <select 
            className="w-full px-2 py-1 bg-gray-900 text-white text-xs rounded border border-gray-600"
            defaultValue="false"
            onChange={(e) => {
              localStorage.setItem('agent_include_process', e.target.value);
              // Trigger re-render of current messages
              window.dispatchEvent(new CustomEvent('agent_params_changed'));
            }}
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>

        {/* Include Agent Inputs */}
        <div className="mt-3">
          <label className="text-xs text-gray-400 block mb-1">Show Agent Inputs:</label>
          <select 
            className="w-full px-2 py-1 bg-gray-900 text-white text-xs rounded border border-gray-600"
            defaultValue="false"
            onChange={(e) => {
              localStorage.setItem('agent_include_inputs', e.target.value);
              // Trigger re-render of current messages
              window.dispatchEvent(new CustomEvent('agent_params_changed'));
            }}
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>
      </div>

      {/* Clear chat session (after parameters) */}
      <button
        className="w-full px-3 py-2 rounded text-xs font-medium bg-gray-900 text-gray-100 border border-purple-500 hover:bg-gray-800"
        onClick={() => {
          (async () => {
            if (!window.confirm("Are you sure you want to clear the chat session?")) return;
            try {
              try { localStorage.removeItem("chatbot_messages"); } catch {}
              try { await apiFetch("/api/core/chats/", { method: "DELETE" }); } catch {}
              try { await deleteAgentsCache(); } catch {}
            } finally {
              window.location.reload();
            }
          })();
        }}
      >
        Clear chat session
      </button>


      {/* Usage (bottom) */}
      <div className="mt-3 mb-3">
        <div className="rounded-lg bg-gray-800/60 border border-white/10 p-3 text-xs text-gray-300">
          <div className="font-medium mb-1 text-xs">Usage</div>
          {usage ? (
            <div className="grid grid-cols-1 gap-1">
              <div>Chats: <span className="font-semibold">{usage.chats_used_today ?? 0}</span> / <span className="text-gray-400">{usage.max_chats ?? '-'}</span></div>
              <div>Reset at: <span className="font-semibold">{countdown}</span></div>
            </div>
          ) : (
            <div className="text-gray-400">Loading usage...</div>
          )}
        </div>
      </div>
      <button
        className="w-full px-3 py-2 rounded text-xs font-medium bg-gray-900 text-gray-100 border border-white/10 hover:bg-gray-800"
        onClick={() => {
          // navigate in-app instead of opening a new tab
          router.push('/view-files');
        }}
      >
        View/Import/Delete Databases
      </button>
      <button
        className="w-full px-3 py-2 rounded text-xs font-medium bg-gray-900 text-gray-100 border border-white/10 hover:bg-gray-800 mt-3"
        onClick={() => {
          router.push('/settings');
        }}
      >
        API Key Settings
      </button>

      
        <button
          className="w-full px-3 py-2 rounded text-xs font-medium bg-gray-900 text-gray-100 border border-white/10 hover:bg-gray-800 mt-3 disabled:opacity-70"
          onClick={async () => {
            setDownloadLoading(true);
            try {
              const raw = localStorage.getItem("chatbot_messages") || "[]";
              const messages = JSON.parse(raw);
              // Use apiFetch which attempts refresh automatically
              try {
                const text = await apiFetch("/api/core/download-chat-md/", { method: "POST", body: JSON.stringify({ messages, filename: `chat_${Date.now()}.md` }) });
                if (typeof text === "string") {
                  const blob = new Blob([text], { type: "text/markdown" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `chat_${Date.now()}.md`;
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  URL.revokeObjectURL(url);
                  setDownloadLoading(false);
                  return;
                }
              } catch (e) {
                // ignore and fallback to client generation
              }

              // fallback local generation
              const mdParts: string[] = ["# Chat history\n\n"];
              for (const m of messages) {
                const t = m.createdAt ? new Date(m.createdAt).toISOString() : "";
                mdParts.push(`**${m.sender || 'user'}** - ${t}\n\n`);
                mdParts.push((m.text || "") + "\n\n---\n\n");
              }
              const blob = new Blob([mdParts.join("")], { type: "text/markdown" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `chat_${Date.now()}.md`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              URL.revokeObjectURL(url);
            } catch (e) {
              alert("Failed to download chat history: " + String(e));
            } finally {
              setDownloadLoading(false);
            }
          }}
          disabled={downloadLoading}
        >
          {downloadLoading ? 'Preparing...' : 'Download chat history (MD)'}
        </button>
    </div>
  );
};

export default Menu;
