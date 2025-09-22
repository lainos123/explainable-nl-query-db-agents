"use client"

import React, { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { performLogout } from "./logout";
import Menu from "./menu";
import MobileMenu from "./mobile_menu";
import { useStreamingLogic } from "./streaming_logic";
import { useResendDeleteEdit } from "./resend_delete_edit";
import ChatBox from "./chatbox";
import InsertBox from "./insert_box";
import { streamAgents, deleteAgentsCache } from "../services/api";

export interface ChatMessage {
	id: string;
	sender: "user" | "bot";
	text: string;
	createdAt: number;
	updatedAt?: number;
}

export default function ChatbotPage() {
	const router = useRouter();
	const [menuMinimized, setMenuMinimized] = useState(false);
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [loadingBot, setLoadingBot] = useState(false);
	const [entering, setEntering] = useState(true);
	const [username, setUsername] = useState<string | null>(null);
	const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
	// const { sendUserMessage } = useStreaming(setMessages, setLoadingBot);

	useEffect(() => {
		// entrance overlay
		const t = setTimeout(() => setEntering(false), 600);
		return () => clearTimeout(t);
	}, []);

	// Auth guard: if no access token, bounce to login
	useEffect(() => {
		if (typeof window === "undefined") return;
		const token = localStorage.getItem("access_token");
		const u = localStorage.getItem("username");
		if (!token) {
			// Hard redirect ensures clean state
			router.replace("/");
			return;
		}
		setUsername(u);
	}, [router]);

	// Dragging disabled per request


		// Use logic hooks
		const { sendUserMessage } = useStreamingLogic(setMessages, setLoadingBot);
		const { editMessage, deleteMessage, resendUserMessage } = useResendDeleteEdit(messages, setMessages, setLoadingBot);

	return (
		<div className={`min-h-screen w-full flex bg-gray-900 text-gray-100 relative`}> 
			{/* Desktop sidebar with smooth slide */
			}
			<aside
				className={`hidden md:flex md:fixed md:inset-y-0 md:left-0 w-72 border-r border-gray-700 bg-gray-900/80 backdrop-blur-sm transition-transform duration-300 ease-in-out will-change-transform z-30 ${menuMinimized ? "-translate-x-full" : "translate-x-0"}`}
				aria-hidden={menuMinimized}
			>
				<div className="w-72 h-full p-4">
					<Menu minimized={menuMinimized} setMinimized={setMenuMinimized} username={username} onRequestLogout={() => setShowLogoutConfirm(true)} />
				</div>
			</aside>

						{/* Mobile overlay menu */}
						<MobileMenu minimized={menuMinimized} setMinimized={setMenuMinimized} username={username} onRequestLogout={() => setShowLogoutConfirm(true)} />

			<main className={`flex flex-col h-screen w-full relative transition-all duration-300 ease-in-out ${menuMinimized ? "md:pl-0" : "md:pl-72"}`}>
				<div className="flex flex-col flex-1 max-w-4xl w-full mx-auto px-4 py-6 gap-4">
					<ChatBox
						messages={messages}
						loadingBot={loadingBot}
						onEdit={editMessage}
						onDelete={deleteMessage}
						onResend={resendUserMessage}
						username={username}
					/>
					<InsertBox onSend={sendUserMessage} sending={loadingBot} />
				</div>
			</main>
			{menuMinimized && (
				<button
					className="fixed left-3 top-3 z-50 select-none rounded-full h-10 md:h-11 px-3 md:px-4 flex items-center gap-2 text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-lg backdrop-blur-md transition-colors"
					onClick={() => setMenuMinimized(false)}
					title="Open menu"
					aria-label="Open menu"
				>
					{/* Icon + label */}
					<svg className="w-4 h-4 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
						<line x1="3" y1="7" x2="21" y2="7" />
						<line x1="3" y1="12" x2="21" y2="12" />
						<line x1="3" y1="17" x2="16" y2="17" />
					</svg>
					<span className="text-xs md:text-sm font-medium">Menu</span>
				</button>
			)}

			{/* Entering overlay */}
			{entering && (
				<div className="absolute inset-0 grid place-items-center bg-gray-900/70 backdrop-blur-sm">
					<div className="flex items-center gap-3 text-gray-200">
						<span role="img" aria-label="cat" className="text-2xl animate-bounce">🐱</span>
						<span>Loading chat…</span>
					</div>
				</div>
			)}

			{/* Logout confirm modal */}
			{showLogoutConfirm && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div className="absolute inset-0 bg-black/50" onClick={() => setShowLogoutConfirm(false)} />
					<div className="relative z-10 w-[92vw] max-w-sm rounded-xl border border-gray-700 bg-gray-900 p-5 shadow-2xl">
						<h2 className="text-lg font-semibold mb-2">Log out?</h2>
						<p className="text-sm text-gray-300 mb-4">You will need to sign in again to continue.</p>
						<div className="flex justify-end gap-2">
							<button
								className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-800 hover:bg-gray-700 text-gray-100 text-sm"
								onClick={() => setShowLogoutConfirm(false)}
							>
								Cancel
							</button>
							<button
								className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-sm"
								onClick={() => performLogout("/")}
							>
								Yes, log out
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

