"use client"

import React, { useState, useCallback } from "react";
import "./page.css";
import Menu from "./menu";
import ChatBox from "./chatbox";
import InsertBox from "./insert_box";

export interface ChatMessage {
	id: string;
	sender: "user" | "bot";
	text: string;
	createdAt: number;
	updatedAt?: number;
}

export default function ChatbotPage() {
	const [theme, setTheme] = useState<"light" | "dark">("light");
	const [menuMinimized, setMenuMinimized] = useState(false);
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [loadingBot, setLoadingBot] = useState(false);

	// Generate id helper
	const genId = () => crypto.randomUUID();

	const sendUserMessage = useCallback((text: string) => {
		if (!text.trim()) return;
		const userMsg: ChatMessage = { id: genId(), sender: "user", text: text.trim(), createdAt: Date.now() };
		setMessages(prev => [...prev, userMsg]);
		// Simulate bot reply
		setLoadingBot(true);
		setTimeout(() => {
			setMessages(prev => [...prev, { id: genId(), sender: "bot", text: "Under construction", createdAt: Date.now() }]);
			setLoadingBot(false);
		}, 650);
	}, []);

	const editMessage = useCallback((id: string, newText: string) => {
		setMessages(prev => prev.map(m => m.id === id ? { ...m, text: newText, updatedAt: Date.now() } : m));
	}, []);

	const deleteMessage = useCallback((id: string) => {
		setMessages(prev => {
			const idx = prev.findIndex(m => m.id === id);
			if (idx === -1) return prev;
			const toDelete: string[] = [id];
			// If user message followed by bot answer -> also remove answer
			if (prev[idx].sender === "user" && prev[idx+1] && prev[idx+1].sender === "bot") {
				toDelete.push(prev[idx+1].id);
			}
			return prev.filter(m => !toDelete.includes(m.id));
		});
	}, []);

	const resendUserMessage = useCallback((id: string) => {
		setMessages(prev => {
			const idx = prev.findIndex(m => m.id === id && m.sender === "user");
			if (idx === -1) return prev;
			// Remove existing bot reply if immediately after
			let next = [...prev];
			if (next[idx+1] && next[idx+1].sender === "bot") {
				next.splice(idx+1, 1);
			}
			return next;
		});
		setLoadingBot(true);
		setTimeout(() => {
			setMessages(prev => {
				const idx = prev.findIndex(m => m.id === id);
				if (idx === -1) return prev; // user removed mid-flight
				const insertionIndex = idx + 1;
				const copy = [...prev];
				copy.splice(insertionIndex, 0, { id: genId(), sender: "bot", text: "Under construction", createdAt: Date.now() });
				return copy;
			});
			setLoadingBot(false);
		}, 520);
	}, []);

	return (
		<div className={`chatbot-root-full${theme === "dark" ? " dark" : ""}${menuMinimized ? " menu-hidden" : ""}`}> 
			{!menuMinimized && (
				<Menu theme={theme} setTheme={setTheme} minimized={menuMinimized} setMinimized={setMenuMinimized} />
			)}
			<main style={{ display: "flex", flexDirection: "column", height: "100vh", width: "100%", position: "relative" }}>
				<div className="chatbot-center-wrap">
					<ChatBox
						theme={theme}
						messages={messages}
						loadingBot={loadingBot}
						onEdit={editMessage}
						onDelete={deleteMessage}
						onResend={resendUserMessage}
					/>
					<InsertBox theme={theme} onSend={sendUserMessage} sending={loadingBot} />
				</div>
			</main>
			{menuMinimized && (
				<button
					style={{
						position: "fixed",
						left: 18,
						bottom: 24,
						background: "var(--ai-accent-gradient)",
						border: "1px solid rgba(var(--ai-accent-rgb),0.5)",
						color: "#fff",
						borderRadius: 20,
						padding: "0.85rem 1.1rem 0.8rem",
						fontWeight: 600,
						cursor: "pointer",
						boxShadow: "0 8px 30px -12px rgba(var(--ai-accent-rgb),0.65),0 0 0 1px rgba(var(--ai-accent-rgb),0.4)",
						letterSpacing: 0.5,
						fontSize: 14,
					}}
					onClick={() => setMenuMinimized(false)}
					title="Open menu"
				>
					≡ Menu
				</button>
			)}
		</div>
	);
}

