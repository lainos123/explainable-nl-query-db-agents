import { ChatMessage } from "./page";
import { streamAgents, deleteAgentsCache } from "../services/api";
import { SEP, formatAgentOutput } from "./streaming_presenting";

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
      onDone: () => {
        setLoadingBot(false);
      },
    });
  };

  return { sendUserMessage };
}
