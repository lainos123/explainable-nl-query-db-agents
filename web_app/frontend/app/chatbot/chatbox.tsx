import React, { useRef, useEffect, useState } from "react";
import "./chatbox.css";

interface ChatBoxProps {
  theme: "light" | "dark";
  messages: { id: string; sender: "user" | "bot"; text: string }[];
  loadingBot: boolean;
  onEdit: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onResend: (id: string) => void;
}
const ChatBox: React.FC<ChatBoxProps> = ({ theme, messages, loadingBot, onEdit, onDelete, onResend }) => {
  const [editId, setEditId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [dots, setDots] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  return (
  <div className={`chatbot-window surface${theme === "dark" ? " dark" : ""}`}> 
      <div className="chatbot-messages" role="log" aria-live="polite" aria-relevant="additions" aria-label="Chat messages">
        {messages.map((msg) => {
          const isEditing = editId === msg.id;
          return (
            <div key={msg.id} className={`chatbot-bubble-row ${msg.sender}`}>
              <div className={`chatbot-avatar ${msg.sender}`}>{msg.sender === "user" ? "U" : "🤖"}</div>
              <div className={`chatbot-bubble ${msg.sender}`}> 
                {isEditing ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    <textarea
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      rows={Math.min(8, Math.max(1, editValue.split(/\n/).length))}
                      style={{ resize: "vertical", width: "100%", background: "var(--ai-bg-inset)", color: "inherit", border: "1px solid var(--ai-border)", borderRadius: 8, padding: "6px 8px", fontSize: "0.85rem" }}
                    />
                    <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                      <button onClick={cancelEdit} style={miniBtnStyle}>Cancel</button>
                      <button onClick={saveEdit} style={{ ...miniBtnStyle, background: "var(--ai-accent-gradient)", color: "#fff", border: "1px solid rgba(var(--ai-accent-rgb),0.5)" }}>Save</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                    <div style={actionBarStyle}>
                      {msg.sender === 'user' && (
                        <>
                          <button style={miniBtnStyle} onClick={() => startEdit(msg.id, msg.text)}>Edit</button>
                          <button style={miniBtnStyle} onClick={() => onResend(msg.id)}>Resend</button>
                        </>
                      )}
                      <button style={miniBtnStyle} onClick={() => onDelete(msg.id)}>Delete</button>
                      {msg.sender === 'bot' && (
                        <button style={miniBtnStyle} onClick={() => startEdit(msg.id, msg.text)}>Edit</button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}
        {loadingBot && (
          <div className="chatbot-bubble-row bot">
            <div className="chatbot-avatar bot">🤖</div>
            <div className="chatbot-bubble bot">
              <span><span className="chatbot-spinner" />Under construction{dots}</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatBox;

// Inline style objects (kept small & reusable) – could be refactored to CSS
const miniBtnStyle: React.CSSProperties = {
  background: 'var(--ai-bg-inset)',
  border: '1px solid var(--ai-border)',
  color: 'var(--ai-text)',
  fontSize: '0.65rem',
  padding: '4px 8px',
  borderRadius: 6,
  cursor: 'pointer',
  lineHeight: 1.1,
  display: 'inline-flex',
  alignItems: 'center',
  gap: 4,
};

const actionBarStyle: React.CSSProperties = {
  display: 'flex',
  gap: 6,
  marginTop: 8,
  flexWrap: 'wrap',
  opacity: .9,
};

