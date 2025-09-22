import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { marked } from "marked";
import { renderStreamData } from "./streaming_logic";
import React, { useRef, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

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

  // Modal for 401 stream error
  const [show401Modal, setShow401Modal] = useState(false);

  // Example: auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loadingBot]);

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

    // OAuth 401 handler: logout and redirect to login
    useEffect(() => {
      // Check if any bot message contains 401 OAuth failure
      const has401 = messages.some(
        (msg) => msg.sender === "bot" && /401.*Oau.*thất bại/i.test(msg.text)
      );
      if (has401) {
        // Clear local/session storage if needed
        if (typeof window !== "undefined") {
          localStorage.clear();
          sessionStorage.clear();
        }
        // Redirect to login page
  window.location.href = "/";
      }
        // Check for [Stream error] HTTP 401
        const hasStream401 = messages.some(
          (msg) => /\[Stream error\]\s*HTTP 401/i.test(msg.text)
        );
        if (hasStream401) {
          setShow401Modal(true);
        }
    }, [messages, router]);

  return (
  <div className={`flex-1 overflow-hidden rounded-xl border border-gray-700 bg-gray-800 shadow-sm`}> 
      {/* 401 Stream Error Modal */}
      {show401Modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 min-w-[300px] text-center">
            <div className="text-lg font-semibold mb-2 text-red-600 dark:text-red-400">[Stream error] HTTP 401</div>
            <div className="mb-4 text-gray-700 dark:text-gray-200">Your login session has expired or is invalid. Please log in again.</div>
            <button
              className="px-4 py-2 rounded bg-blue-600 text-white font-medium hover:bg-blue-700"
              onClick={() => {
                setShow401Modal(false);
                if (typeof window !== "undefined") {
                  localStorage.clear();
                  sessionStorage.clear();
                }
                window.location.href = "/";
              }}
            >Continue</button>
          </div>
        </div>
      )}
    <div className="h-full overflow-y-auto p-4 space-y-3" role="log" aria-live="polite" aria-relevant="additions" aria-label="Chat messages">
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
      {data.database && <div><span className="font-bold">Database:</span> {data.database}</div>}
      {data.tables && <div><span className="font-bold">Tables:</span> {Array.isArray(data.tables) ? data.tables.join(", ") : data.tables}</div>}
      {data.columns && <div><span className="font-bold">Columns:</span> {Array.isArray(data.columns) ? data.columns.join(", ") : data.columns}</div>}
      {data.SQL && (
        <div>
          <span className="font-bold">SQL:</span>
          <SyntaxHighlighter language="sql" style={oneDark} customStyle={{ borderRadius: "0.5rem", fontSize: "0.95em", marginTop: "0.25rem" }}>
            {data.SQL}
          </SyntaxHighlighter>
        </div>
      )}
      {data.reasons && <div className="italic text-gray-400">{data.reasons}</div>}
      {data.result && Array.isArray(data.result) && data.result.length > 0 && (
        <div>
          <span className="font-bold">Result:</span>
          <table className="min-w-[200px] border mt-2 text-sm">
            <thead>
              <tr>
                {Object.keys(data.result[0]).map((h) => (
                  <th key={h} className="border px-2 py-1 bg-gray-800 text-gray-100">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.result.map((row: any, i: number) => (
                <tr key={i}>
                  {Object.keys(row).map((h) => (
                    <td key={h} className="border px-2 py-1">{row[h]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
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
                    {msg.sender === 'user' && !loadingBot && (
                      <div className="flex gap-1 mt-2 flex-wrap opacity-90">
                        <button
                          className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800"
                          onClick={() => startEdit(msg.id, msg.text)}
                        >Edit</button>
                        <button
                          className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800"
                          onClick={() => onResend(msg.id)}
                        >Resend</button>
                        <button
                          className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800"
                          onClick={() => onDelete(msg.id)}
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

