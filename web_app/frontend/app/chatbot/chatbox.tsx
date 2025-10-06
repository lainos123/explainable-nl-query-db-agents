import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { marked } from "marked";
import { renderStreamData } from "./streaming_logic";
import React, { useRef, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { performLogout } from "../services/logout";
import { apiFetch } from "../services/api";

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
  
  // State for setup messages
  const [hasApiKey, setHasApiKey] = useState<boolean>(false);
  const [hasDatabases, setHasDatabases] = useState<boolean>(false);
  const [isClient, setIsClient] = useState<boolean>(false);

  // Check if we're on the client side to avoid hydration issues
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Check setup status
  useEffect(() => {
    if (!isClient) return;
    
    const checkSetupStatus = async () => {
      try {
        // Determine if a user auth token exists; without it, skip API calls
        const token = localStorage.getItem('access_token');
        if (!token) {
          setHasApiKey(false);
          setHasDatabases(false);
          return;
        }

        // Query backend for API key presence
        try {
          const ak = await apiFetch('/api/core/apikeys/');
          const hasKey = !!(ak && (ak.has_key === true || ak.api_key));
          setHasApiKey(hasKey);
        } catch (_) {
          setHasApiKey(false);
        }

        // Query backend for uploaded databases
        try {
          const files = await apiFetch('/api/core/files/');
          setHasDatabases(Array.isArray(files) && files.length > 0);
        } catch (_) {
          setHasDatabases(false);
        }
      } catch (_) {
        setHasApiKey(false);
        setHasDatabases(false);
      }
    };
    
    checkSetupStatus();
  }, [isClient]);

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
              <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm break-words [overflow-wrap:anywhere] ${msg.sender === 'user' ? 'bg-purple-500/25 text-white border border-purple-500' : 'bg-gray-900 text-gray-100 border border-purple-500/40'}`}> 
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
  const [include_reasons, setIncludeReasons] = React.useState(localStorage.getItem('agent_include_reasons') === 'true');
  const [include_process, setIncludeProcess] = React.useState(localStorage.getItem('agent_include_process') === 'true');
  const [include_inputs, setIncludeInputs] = React.useState(localStorage.getItem('agent_include_inputs') === 'true');

  // Listen for parameter changes
  React.useEffect(() => {
    const handleParamChange = () => {
      setIncludeReasons(localStorage.getItem('agent_include_reasons') === 'true');
      setIncludeProcess(localStorage.getItem('agent_include_process') === 'true');
      setIncludeInputs(localStorage.getItem('agent_include_inputs') === 'true');
    };

    window.addEventListener('agent_params_changed', handleParamChange);
    return () => window.removeEventListener('agent_params_changed', handleParamChange);
  }, []);

  // Determine which agent this output is from based on the data structure
  const getAgentInfo = (data: any) => {
    // Unified purple-themed styling for all agents to match app feel
    const purpleBadge = "bg-purple-600";
    if (data.SQL) {
      return {
        name: "Agent C - SQL Generation",
        description: "Generates the final SQL query",
        color: purpleBadge,
      };
    } else if (data.tables || data.relevant_tables) {
      return {
        name: "Agent B - Table Selection",
        description: "Selects relevant tables from the database",
        color: purpleBadge,
      };
    } else if (data.database) {
      return {
        name: "Agent A - Database Selection",
        description: "Identifies the most relevant database",
        color: purpleBadge,
      };
    }
    return null;
  };

  const agentInfo = getAgentInfo(data);

  return (
    <div className="space-y-3">
      {agentInfo && (
        <div className={`bg-gray-900 border-2 border-purple-500 text-white px-3 py-2 rounded-lg`}>
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
              <div>4. <span className="text-blue-400">Similarity Search</span> - Find top-K schemas with highest similarity scores</div>
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

      {/* Input Section - only show if enabled and there's content */}
      {include_inputs && (data.query || data.retrieved_schemas || data.database || data.relevant_tables) && (
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
              {[...data.retrieved_schemas]
                .sort((a: any, b: any) => {
                  const sa = typeof a?.similarity === 'number' ? a.similarity : undefined;
                  const sb = typeof b?.similarity === 'number' ? b.similarity : undefined;
                  if (sa !== undefined || sb !== undefined) {
                    return Number(sb ?? 0) - Number(sa ?? 0);
                  }
                  const da = typeof a?.score === 'number' ? a.score : undefined;
                  const db = typeof b?.score === 'number' ? b.score : undefined;
                  if (da !== undefined || db !== undefined) {
                    // Older payloads: score is distance. Lower is better → sort ascending
                    if (da === undefined && db === undefined) return 0;
                    if (da === undefined) return 1;
                    if (db === undefined) return -1;
                    return Number(da) - Number(db);
                  }
                  return 0;
                })
                .map((schema: any, i: number) => (
                <div key={i} className="mb-2 p-2 bg-gray-800 rounded text-xs">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-blue-400 font-medium">
                      #{i + 1} {typeof schema.similarity === 'number' ? `Similarity: ${schema.similarity}` : (typeof schema.score === 'number' ? `Score (lower is better): ${schema.score}` : '')}
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
                  className="text-blue-400 hover:text-blue-300 underline block"
                  onClick={async () => {
                    try {
                      const schemaData = await apiFetch(`/api/agents/schema/${encodeURIComponent(data.database)}/ab/`);
                      
                      // Create a more detailed display for the schema
                      const tables = schemaData.schemas || [];
                      let displayText = `Summarised Schema for ${data.database}:\n\n`;
                      displayText += `Found ${tables.length} tables:\n\n`;
                      
                      tables.forEach((table: any, index: number) => {
                        displayText += `${index + 1}. ${table.table}\n`;
                        displayText += `   Columns: ${table.columns.join(', ')}\n\n`;
                      });
                      
                      displayText += `\nThis contains database, table, and column info from the selected database.`;
                      
                      // Use a more robust display method
                      const newWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
                      if (newWindow) {
                        newWindow.document.write(`
                          <html>
                            <head><title>Schema for ${data.database}</title></head>
                            <body style="font-family: monospace; padding: 20px; white-space: pre-wrap; text-align: left;">
                              <h2>Summarised Schema for ${data.database}</h2>
                              <p><strong>Found ${tables.length} tables:</strong></p>
                              ${tables.map((table: any, index: number) => 
                                `<div style="margin: 15px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9; text-align: left;">
                                  <h3>${index + 1}. ${table.table}</h3>
                                  <p><strong>Columns:</strong> ${table.columns.join(', ')}</p>
                                </div>`
                              ).join('')}
                              <p><em>This contains database, table, and column info from the selected database.</em></p>
                            </body>
                          </html>
                        `);
                        newWindow.document.close();
                      } else {
                        // Fallback to alert if popup is blocked
                        alert(displayText);
                      }
                    } catch (error) {
                      console.error('Schema loading error:', error);
                      alert(`Failed to load schema: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
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
                  onClick={async () => {
                    try {
                      const schemaData = await apiFetch(`/api/agents/schema/${encodeURIComponent(data.database)}/c/`);
                      
                      // Create a more detailed display for the full schema
                      const schema = schemaData.schema || {};
                      const tables = schema.tables || {};
                      const tableNames = Object.keys(tables);
                      
                      let displayText = `Full Schema for ${data.database}:\n\n`;
                      displayText += `Found ${tableNames.length} tables with complete schema:\n\n`;
                      
                      tableNames.forEach((tableName: string, index: number) => {
                        const tableInfo = tables[tableName];
                        displayText += `${index + 1}. ${tableName}\n`;
                        displayText += `   Columns: ${tableInfo.columns.join(', ')}\n`;
                        if (tableInfo.primary_key && tableInfo.primary_key.length > 0) {
                          displayText += `   Primary Keys: ${tableInfo.primary_key.join(', ')}\n`;
                        }
                        if (tableInfo.foreign_keys && tableInfo.foreign_keys.length > 0) {
                          displayText += `   Foreign Keys: ${tableInfo.foreign_keys.map((fk: any) => 
                            `${fk.from_column} -> ${fk.ref_table}.${fk.ref_column}`
                          ).join(', ')}\n`;
                        }
                        displayText += '\n';
                      });
                      
                      displayText += `\nThis contains complete schema with PK/FK relationships for SQL generation.`;
                      
                      // Use a more robust display method
                      const newWindow = window.open('', '_blank', 'width=1000,height=700,scrollbars=yes');
                      if (newWindow) {
                        newWindow.document.write(`
                          <html>
                            <head><title>Full Schema for ${data.database}</title></head>
                            <body style="font-family: monospace; padding: 20px; white-space: pre-wrap;">
                              <h2>Full Schema for ${data.database}</h2>
                              <p><strong>Found ${tableNames.length} tables with complete schema:</strong></p>
                              ${tableNames.map((tableName: string, index: number) => {
                                const tableInfo = tables[tableName];
                                return `<div style="margin: 15px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;">
                                  <h3>${index + 1}. ${tableName}</h3>
                                  <p><strong>Columns:</strong> ${tableInfo.columns.join(', ')}</p>
                                  ${tableInfo.primary_key && tableInfo.primary_key.length > 0 ? 
                                    `<p><strong>Primary Keys:</strong> ${tableInfo.primary_key.join(', ')}</p>` : ''}
                                  ${tableInfo.foreign_keys && tableInfo.foreign_keys.length > 0 ? 
                                    `<p><strong>Foreign Keys:</strong> ${tableInfo.foreign_keys.map((fk: any) => 
                                      `${fk.from_column} → ${fk.ref_table}.${fk.ref_column}`
                                    ).join(', ')}</p>` : ''}
                                </div>`;
                              }).join('')}
                              <p><em>This contains complete schema with PK/FK relationships for SQL generation.</em></p>
                            </body>
                          </html>
                        `);
                        newWindow.document.close();
                      } else {
                        // Fallback to alert if popup is blocked
                        alert(displayText);
                      }
                    } catch (error) {
                      console.error('Schema loading error:', error);
                      alert(`Failed to load schema: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
                  }}
                >
                  Full Schema ({data.database})
                </button>
                <button 
                  className="text-green-400 hover:text-green-300 underline block mt-2"
                  onClick={async () => {
                    try {
                      const schemaData = await apiFetch(`/api/agents/schema/${encodeURIComponent(data.database)}/c/`);
                      
                      // Create interactive schema visualization
                      const schema = schemaData.schema || {};
                      const tables = schema.tables || {};
                      
                      // Generate the interactive HTML with NetworkX-style visualization
                      const interactiveHtml = `
                        <!DOCTYPE html>
                        <html>
                        <head>
                          <title>Interactive Schema for ${data.database}</title>
                          <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
                          <style>
                            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                            #network { width: 100%; height: 80vh; border: 1px solid #ccc; background-color: white; border-radius: 8px; }
                            .header { text-align: center; margin-bottom: 20px; }
                            .controls { margin-bottom: 15px; text-align: center; }
                            .controls button { margin: 5px; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
                            .btn-primary { background-color: #007bff; color: white; }
                            .btn-secondary { background-color: #6c757d; color: white; }
                            .btn-success { background-color: #28a745; color: white; }
                            
                            .legend { 
                              margin: 20px 0; 
                              padding: 15px; 
                              background-color: #f8f9fa; 
                              border: 1px solid #dee2e6; 
                              border-radius: 8px; 
                            }
                            .legend h3 { 
                              margin: 0 0 10px 0; 
                              color: #333; 
                              font-size: 16px; 
                            }
                            .legend-items { 
                              display: flex; 
                              flex-wrap: wrap; 
                              gap: 15px; 
                              align-items: center; 
                            }
                            .legend-item { 
                              display: flex; 
                              align-items: center; 
                              gap: 8px; 
                              font-size: 14px; 
                              color: #555; 
                            }
                            .legend-node { 
                              width: 20px; 
                              height: 20px; 
                              border: 2px solid; 
                              border-radius: 3px; 
                            }
                            .table-node { 
                              background-color: #5BBCD6; 
                              border-color: #4A9BC7; 
                              border-radius: 3px; 
                            }
                            .pk-node { 
                              background-color: #FFD700; 
                              border-color: #FFA500; 
                              border-radius: 50%; 
                            }
                            .fk-node { 
                              background-color: #FF6B6B; 
                              border-color: #FF4444; 
                              border-radius: 50%; 
                            }
                            .column-node { 
                              background-color: #a4e6a0; 
                              border-color: #90C695; 
                              border-radius: 50%; 
                            }
                            .legend-edge { 
                              width: 30px; 
                              height: 3px; 
                              border-radius: 2px; 
                            }
                            .has-column { 
                              background-color: #999999; 
                            }
                            .fk-relationship { 
                              background: repeating-linear-gradient(
                                90deg,
                                #FF0000,
                                #FF0000 3px,
                                transparent 3px,
                                transparent 6px
                              );
                            }
                          </style>
                        </head>
                        <body>
                          <div class="header">
                            <h1>Interactive Schema: ${data.database}</h1>
                            <p>Click and drag nodes to explore the database structure. Red edges show foreign key relationships.</p>
                            
                            <div class="legend">
                              <h3>Legend:</h3>
                              <div class="legend-items">
                                <div class="legend-item">
                                  <div class="legend-node table-node"></div>
                                  <span>Table</span>
                                </div>
                                <div class="legend-item">
                                  <div class="legend-node pk-node"></div>
                                  <span>Primary Key</span>
                                </div>
                                <div class="legend-item">
                                  <div class="legend-node fk-node"></div>
                                  <span>Foreign Key</span>
                                </div>
                                <div class="legend-item">
                                  <div class="legend-node column-node"></div>
                                  <span>Column</span>
                                </div>
                                <div class="legend-item">
                                  <div class="legend-edge has-column"></div>
                                  <span>Table-Column Relationship</span>
                                </div>
                                <div class="legend-item">
                                  <div class="legend-edge fk-relationship"></div>
                                  <span>Foreign Key Relationship</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div class="controls">
                            <button class="btn-primary" onclick="fitNetwork()">Fit to Screen</button>
                            <button class="btn-success" onclick="resetView()">Reset View</button>
                          </div>
                          
                          <div id="network"></div>
                          
                          <script>
                            let nodes = new vis.DataSet([]);
                            let edges = new vis.DataSet([]);
                            
                            // Schema data from backend
                            const schemaData = ${JSON.stringify(tables)};
                            
                            // Create nodes and edges
                            function createNetwork() {
                              const nodeList = [];
                              const edgeList = [];
                              
                              // Add table nodes
                              Object.keys(schemaData).forEach(tableName => {
                                const tableInfo = schemaData[tableName];
                                nodeList.push({
                                  id: tableName,
                                  label: tableName,
                                  group: 'table',
                                  color: { background: '#5BBCD6', border: '#4A9BC7' },
                                  shape: 'box',
                                  font: { size: 16, color: 'white' },
                                  title: \`Table: \${tableName}\\nPrimary Keys: \${tableInfo.primary_key?.join(', ') || 'None'}\\nColumns: \${tableInfo.columns?.join(', ') || 'None'}\`
                                });
                                
                                // Add column nodes
                                tableInfo.columns?.forEach(column => {
                                  const columnId = \`\${tableName}.\${column}\`;
                                  const isPrimaryKey = tableInfo.primary_key?.includes(column);
                                  const isForeignKey = tableInfo.foreign_keys?.some(fk => fk.from_column === column);
                                  
                                  nodeList.push({
                                    id: columnId,
                                    label: column,
                                    group: 'column',
                                    color: { 
                                      background: isPrimaryKey ? '#FFD700' : isForeignKey ? '#FF6B6B' : '#a4e6a0',
                                      border: isPrimaryKey ? '#FFA500' : isForeignKey ? '#FF4444' : '#90C695'
                                    },
                                    shape: 'ellipse',
                                    font: { size: 12 },
                                    title: \`Column: \${column}\\nTable: \${tableName}\\nType: \${isPrimaryKey ? 'Primary Key' : isForeignKey ? 'Foreign Key' : 'Regular Column'}\`
                                  });
                                  
                                  // Add edge from table to column
                                  edgeList.push({
                                    from: tableName,
                                    to: columnId,
                                    color: { color: '#999999' },
                                    arrows: 'to',
                                    title: 'HAS_COLUMN'
                                  });
                                });
                                
                                // Add foreign key edges
                                tableInfo.foreign_keys?.forEach(fk => {
                                  const fromColumn = \`\${tableName}.\${fk.from_column}\`;
                                  const toColumn = \`\${fk.ref_table}.\${fk.ref_column}\`;
                                  
                                  edgeList.push({
                                    from: fromColumn,
                                    to: toColumn,
                                    color: { color: '#FF0000' },
                                    arrows: 'to',
                                    title: \`Foreign Key: \${tableName}.\${fk.from_column} → \${fk.ref_table}.\${fk.ref_column}\`,
                                    dashes: true
                                  });
                                });
                              });
                              
                              nodes = new vis.DataSet(nodeList);
                              edges = new vis.DataSet(edgeList);
                              
                              // Create network
                              const container = document.getElementById('network');
                              const data = { nodes: nodes, edges: edges };
                              const options = {
                                nodes: {
                                  borderWidth: 2,
                                  shadow: true,
                                  font: { face: 'Arial' }
                                },
                                edges: {
                                  width: 2,
                                  shadow: true,
                                  font: { size: 10, color: '#666' }
                                },
                                physics: {
                                  enabled: true,
                                  solver: 'forceAtlas2Based',
                                  forceAtlas2Based: {
                                    gravitationalConstant: -50,
                                    centralGravity: 0.01,
                                    springLength: 100,
                                    springConstant: 0.08
                                  },
                                  stabilization: { iterations: 200 }
                                },
                                groups: {
                                  table: {
                                    shape: 'box',
                                    color: { background: '#5BBCD6', border: '#4A9BC7' }
                                  },
                                  column: {
                                    shape: 'ellipse',
                                    color: { background: '#a4e6a0', border: '#90C695' }
                                  }
                                }
                              };
                              
                              network = new vis.Network(container, data, options);
                              
                              // Add event listeners
                              network.on("selectNode", function (params) {
                                if (params.nodes.length > 0) {
                                  const nodeId = params.nodes[0];
                                  const node = nodes.get(nodeId);
                                  console.log("Selected node:", node);
                                }
                              });
                            }
                            
                            // Control functions
                            function fitNetwork() {
                              network.fit();
                            }
                            
                            function resetView() {
                              network.setData({ nodes: nodes, edges: edges });
                              network.fit();
                            }
                            
                            // Initialize network when page loads
                            let network;
                            window.onload = function() {
                              createNetwork();
                            };
                          </script>
                        </body>
                        </html>
                      `;
                      
                      // Open interactive schema in new window
                      const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes');
                      if (newWindow) {
                        newWindow.document.write(interactiveHtml);
                        newWindow.document.close();
                      } else {
                        alert('Popup blocked! Please allow popups for this site to view the interactive schema.');
                      }
                    } catch (error) {
                      console.error('Interactive schema loading error:', error);
                      alert(`Failed to load interactive schema: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
                  }}
                >
                  View Interactive Schema Graph
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
            <div className="bg-gray-900 text-gray-100 px-3 py-2 rounded-lg border-2 border-gray-200">
              <div className="font-semibold text-sm">Query Execution</div>
              <div className="text-xs opacity-90">Running SQL query on the selected database</div>
            </div>

            {/* Tools/Data Access (shown only when detailed description is enabled) */}
            {include_process && (
              <div className="bg-gray-800 rounded-lg p-3">
                <div className="text-xs font-semibold text-gray-300 mb-2">🛠️ Execution Environment</div>
                <div className="text-xs text-gray-400 space-y-1">
                  <div>• <span className="text-blue-400">SQLite Database</span> - Direct execution on uploaded database file</div>
                  <div>• <span className="text-blue-400">Query Engine</span> - Native SQLite query processing</div>
                  <div>• <span className="text-blue-400">Result Streaming</span> - Real-time data retrieval and formatting</div>
                </div>
              </div>
            )}

            {/* Execution Results */}
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-xs font-semibold text-gray-300 mb-2">📊 Query Results</div>
              <div className="text-xs text-gray-400 mb-2">
                Found {data.result.length} rows in the database
              </div>
            <div className="flex gap-2 mb-2">
              <button
                className="px-3 py-1 rounded text-xs font-medium bg-gray-900 text-white border border-purple-500 hover:bg-gray-800"
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
                className="px-3 py-1 rounded text-xs font-medium bg-gray-900 text-white border border-purple-500 hover:bg-gray-800"
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
        
        {/* Setup Messages - Show if API key or databases are missing */}
        {(() => {
          if (isClient && !loadingBot) {
            return (
              <div className="mt-4 space-y-3">
            {/* API Key Setup Message */}
            {!hasApiKey && (
              <div className="bg-red-600 text-white px-4 py-3 rounded-lg border border-red-500 shadow-lg">
                <div className="flex items-center gap-2">
                  <svg className="w-6 h-6 text-red-200" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <div className="font-bold text-lg">API Key Required</div>
                    <div className="text-sm opacity-90 mt-1">You must add your OpenAI API key in settings before you can use the agents.</div>
                  </div>
                </div>
                <button 
                  onClick={() => window.location.href = '/settings'}
                  className="mt-3 px-4 py-2 bg-red-500 hover:bg-red-400 text-white text-sm font-semibold rounded transition-colors shadow-md"
                >
                  Go to Settings
                </button>
              </div>
            )}
            
            {/* Database Upload Message */}
            {hasApiKey && !hasDatabases && (
              <div className="bg-orange-600 text-white px-4 py-3 rounded-lg border border-orange-500 shadow-lg">
                <div className="flex items-center gap-2">
                  <svg className="w-6 h-6 text-orange-200" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <div className="font-bold text-lg">No Databases Found</div>
                    <div className="text-sm opacity-90 mt-1">Upload your SQLite database files to start querying with natural language.</div>
                  </div>
                </div>
                <button 
                  onClick={() => window.location.href = '/view-files'}
                  className="mt-3 px-4 py-2 bg-orange-500 hover:bg-orange-400 text-white text-sm font-semibold rounded transition-colors shadow-md"
                >
                  Upload Databases
                </button>
              </div>
            )}
              </div>
            );
          }
          return null;
        })()}
      </div>
    </div>
  );
};

export default ChatBox;

