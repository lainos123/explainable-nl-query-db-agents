import type { ChatMessage } from "./page";
import { streamAgents, deleteAgentsCache } from "../services/api";
const SEP = "\n\n---\n\n";

export function useResendDeleteEdit(messages: ChatMessage[], setMessages: (fn: (prev: ChatMessage[]) => ChatMessage[]) => void, setLoadingBot: (v: boolean) => void) {
  const genId = () => crypto.randomUUID();

  const editMessage = (id: string, newText: string) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, text: newText, updatedAt: Date.now() } : m));
    setTimeout(() => {
      const msg = messages.find(m => m.id === id && m.sender === "user");
      if (!msg) return;
      setMessages(prev => {
        const idx = prev.findIndex(m => m.id === id);
        if (idx === -1) return prev;
        const next = [...prev];
        if (next[idx+1] && next[idx+1].sender === "bot") next.splice(idx+1, 1);
        return next;
      });
      const botId = genId();
      setLoadingBot(true);
      setMessages(prev => {
        const idx = prev.findIndex(m => m.id === id);
        const copy = [...prev];
        copy.splice(idx + 1, 0, { id: botId, sender: "bot", text: "", createdAt: Date.now() });
        return copy;
      });
      let lastAgent: string | null = null;
      // reuse current parameters from localStorage, same as initial send
      const model = localStorage.getItem('agent_llm_model') || 'gpt-5-mini';
      const top_k = parseInt(localStorage.getItem('agent_top_k') || '5');
      const include_reasons = localStorage.getItem('agent_include_reasons') !== 'false';
      const include_process = localStorage.getItem('agent_include_process') !== 'false';
      streamAgents({ query: newText, model, top_k, include_reasons, include_process }, {
        onEvent: (evt) => {
          const isContent = !!(evt && (evt.output || evt.error));
          let sepNow = false;
          if (isContent && evt?.agent) {
            if (lastAgent && evt.agent !== lastAgent) sepNow = true;
            lastAgent = evt.agent;
          }
          if (evt?.output) {
            const chunk = JSON.stringify(evt.output);
            setMessages(prev => prev.map(m => {
              if (m.id !== botId) return m;
              const prefix = m.text ? (sepNow ? SEP : "\n") : "";
              return { ...m, text: (m.text || "") + prefix + chunk };
            }));
          } else if (evt?.error) {
            setMessages(prev => prev.map(m => {
              if (m.id !== botId) return m;
              const prefix = m.text ? (sepNow ? SEP : "\n") : "";
              return { ...m, text: (m.text || "") + prefix + `Error: ${evt.error}` };
            }));
          }
        },
        onError: (err) => {
          setMessages(prev => prev.map(m => m.id === botId ? { ...m, text: (m.text ? m.text + "\n" : "") + `\n[Stream error] ${err.message}` } : m));
        },
        onDone: () => setLoadingBot(false),
      });
    }, 0);
  };

  const deleteMessage = (id: string) => {
    setMessages(prev => {
      const idx = prev.findIndex(m => m.id === id);
      if (idx === -1) return prev;
      const toDelete: string[] = [id];
      if (prev[idx].sender === "user" && prev[idx+1] && prev[idx+1].sender === "bot") {
        toDelete.push(prev[idx+1].id);
      }
      return prev.filter(m => !toDelete.includes(m.id));
    });
    deleteAgentsCache().catch(() => void 0);
  };

  const resendUserMessage = (id: string) => {
    const msg = messages.find(m => m.id === id && m.sender === "user");
    if (!msg) return;
    setMessages(prev => {
      const idx = prev.findIndex(m => m.id === id);
      if (idx === -1) return prev;
      const next = [...prev];
      if (next[idx+1] && next[idx+1].sender === "bot") next.splice(idx+1, 1);
      return next;
    });
    const botId = genId();
    setLoadingBot(true);
    setMessages(prev => {
      const idx = prev.findIndex(m => m.id === id);
      const copy = [...prev];
      copy.splice(idx + 1, 0, { id: botId, sender: "bot", text: "", createdAt: Date.now() });
      return copy;
    });
    let lastAgent: string | null = null;
    const model = localStorage.getItem('agent_llm_model') || 'gpt-5-mini';
    const top_k = parseInt(localStorage.getItem('agent_top_k') || '5');
    const include_reasons = localStorage.getItem('agent_include_reasons') !== 'false';
    const include_process = localStorage.getItem('agent_include_process') !== 'false';
    streamAgents({ query: msg.text, model, top_k, include_reasons, include_process }, {
      onEvent: (evt) => {
        const isContent = !!(evt && (evt.output || evt.error));
        let sepNow = false;
        if (isContent && evt?.agent) {
          if (lastAgent && evt.agent !== lastAgent) sepNow = true;
          lastAgent = evt.agent;
        }
        if (evt?.output) {
          const chunk = JSON.stringify(evt.output);
          setMessages(prev => prev.map(m => {
            if (m.id !== botId) return m;
            const prefix = m.text ? (sepNow ? SEP : "\n") : "";
            return { ...m, text: (m.text || "") + prefix + chunk };
          }));
        } else if (evt?.error) {
          setMessages(prev => prev.map(m => {
            if (m.id !== botId) return m;
            const prefix = m.text ? (sepNow ? SEP : "\n") : "";
            return { ...m, text: (m.text || "") + prefix + `Error: ${evt.error}` };
          }));
        }
      },
      onError: (err) => {
        setMessages(prev => prev.map(m => m.id === botId ? { ...m, text: (m.text ? m.text + "\n" : "") + `\n[Stream error] ${err.message}` } : m));
      },
      onDone: () => setLoadingBot(false),
    });
  };

  return { editMessage, deleteMessage, resendUserMessage };
}
