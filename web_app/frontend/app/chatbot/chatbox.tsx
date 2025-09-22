import React, { useRef, useEffect, useState } from "react";

interface ChatBoxProps {
  messages: { id: string; sender: "user" | "bot"; text: string }[];
  loadingBot: boolean;
  onEdit: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onResend: (id: string) => void;
  username?: string | null;
  onPause?: () => void;
}
const ChatBox: React.FC<ChatBoxProps> = ({ messages, loadingBot, onEdit, onDelete, onResend, username, onPause }) => {
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
  <div className={`flex-1 overflow-hidden rounded-xl border border-gray-700 bg-gray-800 shadow-sm`}> 
    <div className="h-full overflow-y-auto p-4 space-y-3" role="log" aria-live="polite" aria-relevant="additions" aria-label="Chat messages">
        {messages.length === 0 && !loadingBot && (
          <div className="flex items-start gap-0">
            <div className="max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm bg-gray-700 text-gray-100 break-words [overflow-wrap:anywhere]">
              <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">
                <div className="font-medium mb-1">Hello{username ? `, ${username}` : ""}! 👋</div>
                <div className="text-gray-200">What query would you like to run against the dataset? Ask in natural language in any language you like, but remember to make it relevant, e.g., "What is the average age of students?".</div>
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
                      <button onClick={saveEdit} className="px-2 py-1 text-xs rounded bg-violet-600 text-white border border-violet-700">Save</button>
                    </div>
                  </div>
                ) : (
                  <>
                    {msg.sender === 'bot' ? (
                      <div className="space-y-3">
                        {msg.text
                          ? msg.text.split(/\n\n-+\n\n/g).map((part, idx) => {
                              const isError = part.trim() === 'Error, please try again';
                              return (
                                <React.Fragment key={idx}>
                                  {idx > 0 && <div className="h-px bg-gray-500/60" role="separator" />}
                                  <div className={`whitespace-pre-wrap break-words [overflow-wrap:anywhere] ${isError ? 'text-red-400 font-medium' : ''}`}>{part}</div>
                                </React.Fragment>
                              );
                            })
                          : <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]" />}
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">{msg.text}</div>
                    )}
                    {msg.sender === 'user' && (
                      <div className="flex gap-1 mt-2 flex-wrap opacity-90">
                        <button className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800" onClick={() => startEdit(msg.id, msg.text)}>Edit</button>
                        <button className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800" onClick={() => onResend(msg.id)}>Resend</button>
                        <button className="px-2 py-1 text-xs rounded border border-gray-600 bg-gray-800" onClick={() => onDelete(msg.id)}>Delete</button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          );
        })}
        {loadingBot && (
          <div className="flex items-start gap-2">
            <div className="max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm bg-gray-700 text-gray-100">
              <span>
                <span className="inline-block w-3 h-3 rounded-full bg-green-500 animate-pulse mr-2" />
                thinking{dots}
              </span>
            </div>
            {onPause && (
              <button
                type="button"
                onClick={onPause}
                className="relative inline-flex items-center justify-center px-3 py-2 rounded-md overflow-hidden text-white text-xs font-medium"
                aria-label="Pause streaming"
                title="Pause streaming"
              >
                <span className="absolute inset-0 rounded-md [background:conic-gradient(from_var(--angle),#22c55e_0deg,#8b5cf6_120deg,#ec4899_240deg,#22c55e_360deg)] animate-[spin_2.4s_linear_infinite] opacity-80"></span>
                <span className="absolute inset-[2px] rounded-[6px] bg-gray-800 border border-gray-700" />
                <span className="relative z-10 flex items-center gap-1">
                  <span className="inline-block w-2.5 h-2.5 bg-white/70 animate-pulse rounded-sm" />
                  Pause
                </span>
              </button>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatBox;

