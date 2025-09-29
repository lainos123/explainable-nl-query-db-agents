import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from "react";

interface InsertBoxProps {
  onSend: (text: string) => void;
  sending: boolean;
}

export interface InsertBoxHandle {
  insertText: (text: string, append?: boolean) => void;
  focus: () => void;
}

const InsertBox = forwardRef<InsertBoxHandle, InsertBoxProps>(({ onSend, sending }, ref) => {
  const [input, setInput] = useState("");
  const [runAnim, setRunAnim] = useState(false);
  const textRef = useRef<HTMLTextAreaElement | null>(null);
  // history navigation (like PowerShell)
  const HISTORY_KEY = "chat_input_history";
  const MAX_HISTORY = 50;
  const historyRef = useRef<string[]>([]);
  const histIndexRef = useRef<number>(0); // points to position in history (0..len), len means current editing buffer
  const tempBufferRef = useRef<string>("");

  // Auto resize up to 15 lines
  useEffect(() => {
    const el = textRef.current;
    if (!el) return;
    const lineHeight = 20; // approximate
    const maxLines = 15;
    const maxHeight = lineHeight * maxLines;
    el.style.height = 'auto';
    const newH = Math.min(el.scrollHeight, maxHeight);
    el.style.height = newH + 'px';
    if (el.scrollHeight > maxHeight) {
      el.style.overflowY = 'auto';
    } else {
      el.style.overflowY = 'hidden';
    }
  }, [input]);

  const handleSend = () => {
    if (!input.trim() || sending) return;
    setRunAnim(true);
    onSend(input);
    // save to history
    try {
      const h = historyRef.current || [];
      // avoid duplicate consecutive entries
      if (h[h.length - 1] !== input) {
        h.push(input);
        if (h.length > MAX_HISTORY) h.splice(0, h.length - MAX_HISTORY);
        historyRef.current = h;
        localStorage.setItem(HISTORY_KEY, JSON.stringify(h));
      }
    } catch (e) {
      // ignore storage errors
    }
    setInput("");
    // reset history navigation pointer to end
    histIndexRef.current = (historyRef.current || []).length;
    setTimeout(() => setRunAnim(false), 500);
  };

  // expose imperative handle
  useImperativeHandle(ref, () => ({
    insertText: (text: string, append = false) => {
      try {
        if (append) setInput((s) => s + text);
        else setInput(text);
        // focus the textarea
        setTimeout(() => textRef.current?.focus(), 0);
      } catch (e) {
        // ignore
      }
    },
    focus: () => {
      try { textRef.current?.focus(); } catch (e) {}
    }
  }), []);

  // load history on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) historyRef.current = parsed;
      }
    } catch (e) {
      historyRef.current = [];
    }
    histIndexRef.current = (historyRef.current || []).length;
  }, []);

  return (
  <div className="flex items-end gap-2 border-t border-gray-700 pt-3">
      <textarea
        ref={textRef}
        value={input}
        className="flex-1 min-h-9 max-h-64 border border-gray-700 rounded-md bg-gray-900 p-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
            return;
          }

          // Arrow key history navigation
          if (e.key === "ArrowUp" || e.key === "ArrowDown") {
            const hist = historyRef.current || [];
            const len = hist.length;
            // initialize pointer to end if first time
            if (typeof histIndexRef.current !== 'number' || histIndexRef.current < 0) histIndexRef.current = len;

            if (e.key === "ArrowUp") {
              e.preventDefault();
              if (histIndexRef.current === len) {
                // store current buffer before navigating
                tempBufferRef.current = input;
              }
              if (len === 0) return;
              histIndexRef.current = Math.max(0, histIndexRef.current - 1);
              const v = hist[histIndexRef.current] || "";
              setInput(v);
            } else {
              // ArrowDown
              e.preventDefault();
              if (len === 0) return;
              histIndexRef.current = Math.min(len, histIndexRef.current + 1);
              if (histIndexRef.current === len) {
                // restore temp buffer
                setInput(tempBufferRef.current || "");
              } else {
                setInput(hist[histIndexRef.current] || "");
              }
            }
          }
        }}
        placeholder="Type your message... (Enter to send, Shift+Enter for new line, arrows to navigate history)"
        disabled={sending}
        rows={1}
        style={{ resize: "none", minWidth: '0', width: '100%' }}
        aria-label="Message input"
      />
      <button
        onClick={handleSend}
        className={`inline-flex items-center justify-center rounded-md px-3 py-2 transition border
          ${sending
            ? 'border-purple-500 bg-gray-900 text-white opacity-80 cursor-progress'
            : 'bg-gray-900 text-white border-purple-500 hover:bg-gray-800'}
          ${runAnim ? 'scale-95' : ''}`}
        disabled={sending || !input.trim()}
        title={sending ? 'Running...' : 'Send'}
        aria-label={sending ? 'Pause/Running' : 'Send message'}
        style={{ minWidth: '48px', minHeight: '40px', width: '48px', height: '40px', cursor: sending ? 'progress' : 'pointer' }}
      >
        {sending ? (
          <span className="relative flex items-center w-full h-full justify-center">
            <span className="animate-spin">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="#a78bfa" strokeWidth="3" opacity="0.7" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="#38bdf8" strokeWidth="3" strokeLinecap="round" />
              </svg>
            </span>
          </span>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        )}
      </button>
    </div>
  );
});

export default InsertBox;

