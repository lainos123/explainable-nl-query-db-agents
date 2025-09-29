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

  // Check parameters from localStorage with state for dynamic updates
  const [include_reasons, setIncludeReasons] = React.useState(localStorage.getItem('agent_include_reasons') !== 'false');
  const [include_process, setIncludeProcess] = React.useState(localStorage.getItem('agent_include_process') !== 'false');

  // Listen for parameter changes
  React.useEffect(() => {
    const handleParamChange = () => {
      setIncludeReasons(localStorage.getItem('agent_include_reasons') !== 'false');
      setIncludeProcess(localStorage.getItem('agent_include_process') !== 'false');
    };

    window.addEventListener('agent_params_changed', handleParamChange);
    return () => window.removeEventListener('agent_params_changed', handleParamChange);
  }, []);

  // Determine which agent this output is from based on the data structure
  const getAgentInfo = (data: any) => {
    if (data.SQL) {
      return {
        name: "Agent C - SQL Generation",
        description: "Generates the final SQL query",
        color: "bg-purple-600"
      };
    } else if (data.tables || data.relevant_tables) {
      return {
        name: "Agent B - Table Selection", 
        description: "Selects relevant tables from the database",
        color: "bg-blue-600"
      };
    } else if (data.database) {
      return {
        name: "Agent A - Database Selection",
        description: "Identifies the most relevant database",
        color: "bg-green-600"
      };
    }
    return null;
  };

  const agentInfo = getAgentInfo(data);

  return (
    <div className="space-y-3">
      {agentInfo && (
        <div className={`${agentInfo.color} text-white px-3 py-2 rounded-lg`}>
          <div className="font-semibold text-sm">{agentInfo.name}</div>
          <div className="text-xs opacity-90">{agentInfo.description}</div>
        </div>
      )}

      {/* Agent Process Section */}
      {agentInfo && include_process && (
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-300 mb-2">🔄 Agent Process</div>
          {agentInfo.name === "Agent A - Database Selection" && (
            <div className="text-xs text-gray-400 space-y-1">
              <div>1. <span className="text-blue-400">Schema Loading</span> - Load full list of all summarised schemas from schema_ab.jsonl 
                <button 
                  className="text-blue-400 hover:text-blue-300 underline ml-2"
                  onClick={() => {
                    const example = [
                      {"database": "student_transcripts_tracking", "table": "Students", "columns": ["student_id", "first_name", "last_name"]},
                      {"database": "online_exams", "table": "Students", "columns": ["Student_ID", "First_Name", "Last_Name"]},
                      {"database": "e_learning", "table": "Students", "columns": ["student_id", "personal_name", "family_name"]}
                    ];
                    alert(`Summarized Schema List (schema_ab.jsonl):\n\n${JSON.stringify(example, null, 2)}\n\nContains database, table, and column info from ALL databases for similarity search.`);
                  }}
                >
                  (view summarised schema example)
                </button>
              </div>
              <div>2. <span className="text-blue-400">Schema Embedding</span> - Convert each schema (database + table + columns) to OpenAI text-embedding-ada-002 vectors</div>
              <div>3. <span className="text-blue-400">Query Embedding</span> - Convert user query to same OpenAI embedding vector</div>
              <div>4. <span className="text-blue-400">Similarity Search</span> - Find top-K schemas with highest cosine similarity scores</div>
              <div>5. <span className="text-blue-400">LLM Decision</span> - Pass retrieved schemas + scores to LLM to select best database with reasoning</div>
            </div>
          )}
          {agentInfo.name === "Agent B - Table Selection" && (
            <div className="text-xs text-gray-400 space-y-1">
              <div>1. <span className="text-blue-400">Database Filtering</span> - Load summarised schema (schema_ab.jsonl) for the selected database only</div>
              <div>2. <span className="text-blue-400">Table Extraction</span> - Parse all available tables and their metadata</div>
              <div>3. <span className="text-blue-400">Relevance Analysis</span> - Analyze which tables are most relevant to the query</div>
              <div>4. <span className="text-blue-400">LLM Selection</span> - Pass table information to LLM to select relevant tables</div>
            </div>
          )}
          {agentInfo.name === "Agent C - SQL Generation" && (
            <div className="text-xs text-gray-400 space-y-1">
              <div>1. <span className="text-blue-400">Schema Loading</span> - Load full schema (schema_c.json) with PK/FK relationships</div>
              <div>2. <span className="text-blue-400">Table Filtering</span> - Focus on selected tables from Agent B</div>
              <div>3. <span className="text-blue-400">Relationship Mapping</span> - Analyze foreign key constraints and join possibilities</div>
              <div>4. <span className="text-blue-400">LLM Generation</span> - Pass full context to LLM to generate optimized SQL query</div>
            </div>
          )}
        </div>
      )}

      {/* Input Section - only show if there's content */}
      {(data.query || data.retrieved_schemas || data.database || data.relevant_tables) && (
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-300 mb-2">Input to Agent</div>
        {data.query && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">User Query:</span>
            <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">{data.query}</div>
          </div>
        )}
        {/* For Agent A: Show retrieved schemas from similarity search */}
        {agentInfo?.name === "Agent A - Database Selection" && data.retrieved_schemas && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Top-K Similar Schemas:</span>
            <div className="bg-gray-900 rounded text-sm mt-1 p-2">
              <div className="text-xs text-gray-500 mb-2">
                Semantic similarity search found {data.retrieved_schemas.length} most relevant schemas:
              </div>
              {data.retrieved_schemas.map((schema: any, i: number) => (
                <div key={i} className="mb-2 p-2 bg-gray-800 rounded text-xs">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-blue-400 font-medium">
                      #{i + 1} Score: {schema.score}
                    </span>
                    <span className="text-green-400">{schema.database}</span>
                  </div>
                  <div className="text-gray-300">
                    <span className="text-yellow-400">{schema.table}</span>
                    {schema.columns && schema.columns.length > 0 && (
                      <span className="text-gray-400 ml-2">
                        ({schema.columns.slice(0, 5).join(', ')}{schema.columns.length > 5 ? '...' : ''})
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {/* For Agent B: Show database from Agent A */}
        {agentInfo?.name === "Agent B - Table Selection" && data.database && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Database:</span>
            <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">{data.database}</div>
          </div>
        )}
        {/* For Agent C: Show database and tables from previous agents */}
        {agentInfo?.name === "Agent C - SQL Generation" && (
          <>
            {data.database && (
              <div className="mb-2">
                <span className="text-xs text-gray-400">Database:</span>
                <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">{data.database}</div>
              </div>
            )}
            {data.relevant_tables && (
              <div className="mb-2">
                <span className="text-xs text-gray-400">Possible Relevant Tables:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {Array.isArray(data.relevant_tables)
                    ? data.relevant_tables.map((t: string, i: number) => (
                        <span key={i} className="bg-gray-900 px-2 py-1 rounded text-xs">{t}</span>
                      ))
                    : <span className="bg-gray-900 px-2 py-1 rounded text-xs">{data.relevant_tables}</span>}
                </div>
              </div>
            )}
          </>
        )}
        
        {/* Schema Input Section - Only for agents that use schema data as input */}
        {agentInfo && (agentInfo.name === "Agent B - Table Selection" || agentInfo.name === "Agent C - SQL Generation") && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Schema Data:</span>
            {agentInfo.name === "Agent B - Table Selection" && data.database && (
              <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">
                <button 
                  className="text-blue-400 hover:text-blue-300 underline"
                  onClick={() => {
                    // Show filtered schema for selected database
                    const example = {
                      "database": data.database,
                      "table": "Students",
                      "columns": ["student_id", "first_name", "last_name", "email_address"]
                    };
                    alert(`Summarised Schema for ${data.database}:\n\n${JSON.stringify(example, null, 2)}\n\nContains database, table, and column info from the selected database.`);
                  }}
                >
                  Summarised Schema ({data.database} only)
                </button>
              </div>
            )}
            {agentInfo.name === "Agent C - SQL Generation" && data.database && (
              <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">
                <button 
                  className="text-blue-400 hover:text-blue-300 underline"
                  onClick={() => {
                    // Show full schema example
                    const example = {
                      "database": data.database,
                      "tables": {
                        "Students": {
                          "columns": ["student_id", "first_name", "last_name", "email_address"],
                          "primary_keys": ["student_id"],
                          "foreign_keys": []
                        },
                        "Courses": {
                          "columns": ["course_id", "course_name", "instructor_id"],
                          "primary_keys": ["course_id"],
                          "foreign_keys": [{"column": "instructor_id", "references": "Instructors.instructor_id"}]
                        }
                      }
                    };
                    alert(`Full Schema for ${data.database}:\n\n${JSON.stringify(example, null, 2)}\n\nContains complete schema with PK/FK relationships for SQL generation.`);
                  }}
                >
                  Full Schema ({data.database})
                </button>
              </div>
            )}
          </div>
        )}
        </div>
      )}

      {/* Output Section - only show if there's content */}
      {(data.database || data.tables || data.SQL) && (
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-300 mb-2">Agent Output</div>
        
        {/* Agent A Output: Selected Database */}
        {agentInfo?.name === "Agent A - Database Selection" && data.database && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Selected Database:</span>
            <div className="bg-gray-900 px-2 py-1 rounded text-sm mt-1">{data.database}</div>
          </div>
        )}
        
        {/* Agent B Output: Relevant Tables */}
        {agentInfo?.name === "Agent B - Table Selection" && data.tables && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Relevant Tables:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {Array.isArray(data.tables)
                ? data.tables.map((t: string, i: number) => (
                    <span key={i} className="bg-gray-900 px-2 py-1 rounded text-xs">{t}</span>
                  ))
                : <span className="bg-gray-900 px-2 py-1 rounded text-xs">{data.tables}</span>}
            </div>
          </div>
        )}

        {/* Agent C Output: Generated SQL */}
        {agentInfo?.name === "Agent C - SQL Generation" && data.SQL && (
          <div className="mb-2">
            <span className="text-xs text-gray-400">Generated SQL:</span>
            <div className="mt-2">
              <SyntaxHighlighter
                language="sql"
                style={oneDark}
                customStyle={{
                  margin: 0,
                  background: '#1a1a1a',
                  fontSize: '0.875rem',
                  lineHeight: '1.5',
                  borderRadius: '0.375rem',
                  border: '1px solid #333',
                }}
                wrapLongLines={true}
              >
                {data.SQL}
              </SyntaxHighlighter>
            </div>
          </div>
        )}
        </div>
      )}

      {/* Reasoning Section */}
      {data.reasons && include_reasons && (
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-300 mb-2">💭 Agent Reasoning</div>
          <div className="text-sm text-gray-300 italic">{data.reasons}</div>
          
        </div>
      )}
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
          <div className="space-y-3">
            {/* Query Execution Header */}
            <div className="bg-orange-600 text-white px-3 py-2 rounded-lg">
              <div className="font-semibold text-sm">Query Execution</div>
              <div className="text-xs opacity-90">Running SQL query on the selected database</div>
            </div>

            {/* Tools/Data Access */}
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-xs font-semibold text-gray-300 mb-2">🛠️ Execution Environment</div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>• <span className="text-blue-400">SQLite Database</span> - Direct execution on uploaded database file</div>
                <div>• <span className="text-blue-400">Query Engine</span> - Native SQLite query processing</div>
                <div>• <span className="text-blue-400">Result Streaming</span> - Real-time data retrieval and formatting</div>
              </div>
            </div>

            {/* Execution Results */}
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-xs font-semibold text-gray-300 mb-2">📊 Query Results</div>
              <div className="text-xs text-gray-400 mb-2">
                Found {data.result.length} rows in the database
              </div>
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

