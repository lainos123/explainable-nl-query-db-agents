import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { marked } from "marked";
import { renderStreamData } from "./streaming_logic";
import React, { useRef, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { performLogout } from "../services/logout";

interface ChatBoxProps {
  messages: { id: string; sender: "user" | "bot"; text: string }[];
  loadingBot: boolean;
  onEdit: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onResend: (id: string) => void;
  username?: string | null;
}
const ChatBox: React.FC<ChatBoxProps> = ({ messages, loadingBot, onEdit, onDelete, onResend, username }) => {
  const router = useRouter();
  const [editId, setEditId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [dots, setDots] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Chat cache state (avoid reading localStorage during render to prevent hydration mismatch)
  const [cachedMessages, setCachedMessages] = useState<{ id: string; sender: "user" | "bot"; text: string }[]>([]);
  // Track whether we've synced the initial cache to avoid overwriting it with an empty array
  const restoredRef = useRef<boolean>(false);

  // Restore cache after mount
  useEffect(() => {
    try {
      const cache = localStorage.getItem("chatbot_messages");
      if (cache) {
        const parsed = JSON.parse(cache);
        if (Array.isArray(parsed)) {
          setCachedMessages(parsed);
          restoredRef.current = parsed.length > 0;
        }
      }
    } catch (e) {
      // ignore
    }
  }, []);

  // 401 handling is centralized via performLogout; no separate modal is needed

  // Example: auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loadingBot, cachedMessages]);

  // Persist messages to cache
  useEffect(() => {
    if (typeof window !== "undefined") {
      // Only write to cache if we have messages, or if we've previously restored
      // a non-empty cache (so clearing is still possible). This prevents a
      // fresh mount with empty messages from erasing stored chat before the
      // page-level initializer runs.
      if (messages.length > 0 || restoredRef.current) {
        try {
          localStorage.setItem("chatbot_messages", JSON.stringify(messages));
        } catch (e) {
          // ignore storage errors
        }
      }
    }
    setCachedMessages(messages);
    if (messages.length > 0) restoredRef.current = true;
  }, [messages]);

  // Example: loading dots
  useEffect(() => {
    if (!loadingBot) return setDots("");
    const interval = setInterval(() => {
      setDots(prev => (prev.length < 3 ? prev + "." : ""));
    }, 500);
    return () => clearInterval(interval);
  }, [loadingBot]);

  const startEdit = (id: string, current: string) => {
    setEditId(id);
    setEditValue(current);
  };
  const cancelEdit = () => { setEditId(null); setEditValue(""); };
  const saveEdit = () => {
    if (editId) {
      onEdit(editId, editValue.trim());
      cancelEdit();
    }
  };

  // You can lift state up and pass setMessages, setLoading, etc. as props if needed

    // NOTE: removed content-inspection-based logout. Authentication
    // handling is centralized in `apiFetch` / streamAgents which will
    // attempt a token refresh before forcing a logout. Leaving
    // message-content-based logout in place caused premature logouts.

  return (
  <div className="flex-1 h-full min-h-0 overflow-hidden rounded-xl bg-gray-900 shadow-sm"> 
      {/* 401 Stream Error handled via performLogout (single OK alert). */}
  <div className="h-full overflow-y-auto p-4 space-y-3 scrollbar-none" role="log" aria-live="polite" aria-relevant="additions" aria-label="Chat messages">
        {messages.length === 0 && !loadingBot && (
          <div className="flex items-start gap-0">
            <div className="max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm bg-gray-700 text-gray-100 break-words [overflow-wrap:anywhere]">
              <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">
                <div className="font-medium mb-1">Hello{username ? `, ${username}` : ""}! 👋</div>
                <div className="text-gray-200">What query would you like to run against the dataset? Ask in natural language, e.g., "What is the average age of students?".</div>
                <div className="text-xs text-gray-300 mt-2">Tip: Press Enter to send, Shift+Enter for a new line.</div>
              </div>
            </div>
          </div>
        )}
        {messages.map((msg) => {
          const isEditing = editId === msg.id;
          return (
            <div key={msg.id} className={`flex items-start gap-0 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm break-words [overflow-wrap:anywhere] ${msg.sender === 'user' ? 'bg-violet-600 text-white' : 'bg-gray-700 text-gray-100'}`}> 
                {isEditing ? (
                  <div className="flex flex-col gap-2">
                    <textarea
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      rows={Math.min(8, Math.max(1, editValue.split(/\n/).length))}
                      className="w-full resize-y bg-white/70 dark:bg-gray-800/70 text-inherit border border-gray-300 dark:border-gray-600 rounded-md p-2 text-sm"
                    />
                    <div className="flex gap-2 justify-end">
                      <button onClick={cancelEdit} className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800">Cancel</button>
                      <button onClick={saveEdit} className="px-2 py-1 text-xs rounded bg-blue-600 text-white border border-blue-700">Save</button>
                    </div>
                  </div>
                ) : (
                  <>
                    {msg.sender === 'bot' ? (
                      <div className="space-y-3">
                        {msg.text
                          ? (() => {
                              // Split by separator and render each part
                              const parts = msg.text.split(/\n\n-+\n\n/);
                              return parts.map((part, idx) => {
                                let rendered;
                                try {
                                  const parsed = JSON.parse(part);
                                  // Custom HTML rendering from JSON
                                  rendered = <BotJsonRender data={parsed} />;
                                } catch {
                                  rendered = <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">{part}</div>;
                                }
// Custom bot JSON to HTML renderer
function BotJsonRender({ data }: { data: any }) {
  // Error
  if (data.error) return <div className="text-red-500 font-semibold">❌ Error: {data.error}</div>;
  if (data.success === false) return <div className="text-yellow-500 font-semibold">⚠️ Failed: {data.message || "Unknown error"}</div>;

  return (
    <div className="space-y-2">
      {data.query && <div><span className="font-bold">Query:</span> <span className="bg-gray-900 px-2 py-1 rounded text-sm">{data.query}</span></div>}
      {data.database && <div><span className="font-bold">Database:</span> {Array.isArray(data.database)
        ? data.database.map((db: string, i: number) => <span key={i} className="bg-gray-900 px-2 py-1 rounded text-sm mx-1">{db}</span>)
        : <span className="bg-gray-900 px-2 py-1 rounded text-sm">{data.database}</span>}
      </div>}
      {data.tables && <div><span className="font-bold">Tables:</span> {Array.isArray(data.tables)
        ? data.tables.map((t: string, i: number) => <span key={i} className="bg-gray-900 px-2 py-1 rounded text-sm mx-1">{t}</span>)
        : <span className="bg-gray-900 px-2 py-1 rounded text-sm">{data.tables}</span>}
      </div>}
      {data.columns && <div><span className="font-bold">Columns:</span> {Array.isArray(data.columns)
        ? data.columns.map((c: string, i: number) => <span key={i} className="bg-gray-900 px-2 py-1 rounded text-sm mx-1">{c}</span>)
        : <span className="bg-gray-900 px-2 py-1 rounded text-sm">{data.columns}</span>}
      </div>}
      {data.SQL && (
        <div className="flex flex-col items-start">
          <span className="font-bold mb-1">SQL:</span>
          <div
            className="chatbot-sql-block"
            style={{
              width: '100%',
              maxWidth: '100%',
              overflowX: 'auto',
              border: '1px solid #333',
              borderRadius: '0.5rem',
              background: '#18181b',
              padding: '0.5em',
              wordBreak: 'break-word',
              whiteSpace: 'pre-wrap',
            }}
          >
            <SyntaxHighlighter
              language="sql"
              style={oneDark}
              customStyle={{
                background: "transparent",
                margin: 0,
                padding: 0,
                fontSize: "0.95em",
                borderRadius: "0.5rem",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
              wrapLongLines={true}
            >
              {data.SQL}
            </SyntaxHighlighter>
          </div>
        </div>
      )}
  {data.reasons && <div className="italic text-gray-400">My reason is: {data.reasons}</div>}
      {data.result && Array.isArray(data.result) && data.result.length > 0 && (() => {
        // Responsive columns/rows
        let colCount = 2, rowCount = 5;
        if (typeof window !== "undefined") {
          if (window.matchMedia("(min-width: 2560px)").matches) {
            colCount = 10; rowCount = 15;
          } else if (window.matchMedia("(min-width: 1440px)").matches) {
            colCount = 8; rowCount = 15;
          } else if (window.matchMedia("(min-width: 1200px)").matches) {
            colCount = 3; rowCount = 15;
          } else if (window.matchMedia("(min-width: 800px)").matches) {
            colCount = 3; rowCount = 10;
          }
        }
        const allHeaders = Object.keys(data.result[0]);
        const showHeaders = allHeaders.slice(0, colCount);
        const hasMoreCols = allHeaders.length > colCount;
        const showRows = data.result.slice(0, rowCount);
        const hasMoreRows = data.result.length > rowCount;
        return (
          <div>
            <span className="font-bold">Result:</span>
            <div className="flex gap-2 mb-2">
              <button
                className="px-3 py-1 rounded bg-blue-600 text-white text-xs font-medium hover:bg-blue-700"
                onClick={() => {
                  try {
                    // Save full result to sessionStorage so /result page can render it
                    sessionStorage.setItem('last_full_result', JSON.stringify(data));
                  } catch (e) {
                    // ignore storage errors
                  }
                  // navigate in-app to the result page
                  try { router.push('/result'); } catch (e) { window.location.href = '/result'; }
                }}
              >View all columns & rows</button>
              <button
                className="px-3 py-1 rounded bg-green-600 text-white text-xs font-medium hover:bg-green-700"
                onClick={() => {
                  // CSV generator
                  function toCSV(headers: string[], rows: Array<Record<string, any>>) {
                    const esc = (v: any) => '"' + String(v).replace(/"/g, '""') + '"';
                    return [headers.join(',') , ...rows.map((r: Record<string, any>) => headers.map((h: string) => esc(r[h])).join(','))].join('\r\n');
                  }
                  const csvData = toCSV(allHeaders, data.result);
                  const blob = new Blob([csvData], { type: 'text/csv' });
                  const a = document.createElement('a');
                  a.href = URL.createObjectURL(blob);
                  a.download = 'result.csv';
                  a.click();
                }}
              >Download CSV</button>
            </div>
            <table className="min-w-[200px] border mt-2 text-sm">
              <thead>
                <tr>
                  {showHeaders.map((h) => (
                    <th key={h} className="border px-2 py-1 bg-gray-800 text-gray-100">{h}</th>
                  ))}
                  {hasMoreCols && <th className="border px-2 py-1 bg-gray-800 text-gray-100">...</th>}
                </tr>
              </thead>
              <tbody>
                {showRows.map((row: any, i: number) => (
                  <tr key={i}>
                    {showHeaders.map((h) => (
                      <td key={h} className="border px-2 py-1">{row[h]}</td>
                    ))}
                    {hasMoreCols && <td className="border px-2 py-1 text-center">...</td>}
                  </tr>
                ))}
                {hasMoreRows && (
                  <tr>
                    <td colSpan={showHeaders.length + (hasMoreCols ? 1 : 0)} className="border px-2 py-1 text-center text-xs text-gray-400">...and {data.result.length - rowCount} more rows</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        );
      })()}
      {/* Fallback: show full JSON if no known keys */}
      {!data.query && !data.database && !data.tables && !data.columns && !data.SQL && !data.reasons && !data.result && (
        <pre className="bg-gray-900 rounded p-2 text-xs overflow-x-auto">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
}
                                return (
                                  <React.Fragment key={idx}>
                                    {idx > 0 && <div className="h-px bg-gray-500/60" role="separator" />}
                                    {rendered}
                                  </React.Fragment>
                                );
                              });
                            })()
                          : <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]" />}
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">{msg.text}</div>
                    )}
                    {msg.sender === 'user' && (
                      <div className="flex gap-1 mt-2 flex-wrap opacity-90">
                        <button
                          className={`px-2 py-1 text-xs rounded border border-gray-600 ${loadingBot ? 'bg-gray-600 text-gray-300 cursor-not-allowed opacity-70' : 'bg-gray-800'}`}
                          onClick={() => startEdit(msg.id, msg.text)}
                          disabled={loadingBot}
                          title={loadingBot ? 'Please wait for the bot to finish' : 'Edit message'}
                        >Edit</button>
                        <button
                          className={`px-2 py-1 text-xs rounded border border-gray-600 ${loadingBot ? 'bg-gray-600 text-gray-300 cursor-not-allowed opacity-70' : 'bg-gray-800'}`}
                          onClick={() => onResend(msg.id)}
                          disabled={loadingBot}
                          title={loadingBot ? 'Please wait for the bot to finish' : 'Resend message'}
                        >Resend</button>
                        <button
                          className={`px-2 py-1 text-xs rounded border border-gray-600 ${loadingBot ? 'bg-gray-600 text-gray-300 cursor-not-allowed opacity-70' : 'bg-gray-800'}`}
                          onClick={() => onDelete(msg.id)}
                          disabled={loadingBot}
                          title={loadingBot ? 'Please wait for the bot to finish' : 'Delete message'}
                        >Delete</button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          );
        })}
        {loadingBot && (
          <div className="flex items-start gap-0">
            <div className="max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm bg-gray-700 text-gray-100">
              <span>
                <span
                  className="inline-block w-3 h-3 rounded-full mr-2 animate-blink-green"
                  style={{ background: 'linear-gradient(90deg,#22c55e 60%,#16a34a 100%)' }}
                />
                Thinking{dots}
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatBox;

