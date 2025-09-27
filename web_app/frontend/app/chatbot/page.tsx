"use client"

import React, { useState } from "react";
// Shared types used by other chatbot modules
export type ChatMessage = {
  id: string;
  sender: "user" | "bot";
  text: string;
  createdAt: number;
  updatedAt?: number;
};
import Menu from "./menu";
import MobileMenu from "./mobile_menu";
import ChatBox from "./chatbox";
import InsertBox, { InsertBoxHandle } from "./insert_box";
import { useChatbotLogic } from "./chatbot_logic";

export default function ChatbotPage() {
  const {
    messages, setMessages,
    loadingBot, username,
    menuMinimized, setMenuMinimized,
    showLogoutConfirm, setShowLogoutConfirm,
    logoutLoading, handleLogout,
    editMessage, deleteMessage, resendUserMessage,
    sendUserMessage, insertRef,
  } = useChatbotLogic();

  return (
    <div className="min-h-screen w-full flex bg-gray-900 text-gray-100 relative">
      {/* Sidebar desktop */}
      <aside
        className={`hidden md:flex md:fixed md:inset-y-0 md:left-0 w-72 border-r border-gray-700 bg-gray-900/80 backdrop-blur-sm transition-transform duration-300 ease-in-out z-30 ${menuMinimized ? "-translate-x-full" : "translate-x-0"}`}
      >
        <div className="w-72 h-full p-4">
          <Menu minimized={menuMinimized} setMinimized={setMenuMinimized} username={username} onRequestLogout={() => setShowLogoutConfirm(true)} />
        </div>
      </aside>

      {/* Mobile overlay menu */}
      <MobileMenu minimized={menuMinimized} setMinimized={setMenuMinimized} username={username} onRequestLogout={() => setShowLogoutConfirm(true)} />

      {/* Main chat */}
      <main className={`flex flex-col h-screen w-full relative transition-all duration-300 ease-in-out ${menuMinimized ? "md:pl-0" : "md:pl-72"}`}>
        <div className="flex flex-col flex-1 h-full min-h-0 px-2 md:px-8 py-6 gap-4">
          <ChatBox
            messages={messages}
            loadingBot={loadingBot}
            onEdit={editMessage}
            onDelete={deleteMessage}
            onResend={resendUserMessage}
            username={username}
          />
          <InsertBox ref={insertRef} onSend={sendUserMessage} sending={loadingBot} />
        </div>
      </main>

      {/* Button open menu when sidebar is hidden */}
      {menuMinimized && (
        <button
          className="fixed left-3 top-3 z-50 rounded-full h-10 md:h-11 px-3 flex items-center gap-2 text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-lg backdrop-blur-md transition-colors"
          onClick={() => setMenuMinimized(false)}
        >
          <svg className="w-4 h-4 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="7" x2="21" y2="7" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="17" x2="16" y2="17" />
          </svg>
          <span className="text-xs md:text-sm font-medium">Menu</span>
        </button>
      )}

      {/* Modal logout */}
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
                className={`px-3 py-1.5 rounded-lg text-white text-sm ${logoutLoading ? 'bg-gray-600 cursor-not-allowed opacity-70' : 'bg-violet-600 hover:bg-violet-700'}`}
                onClick={handleLogout}
                disabled={logoutLoading}
              >
                {logoutLoading ? 'Logging out…' : 'Yes, log out'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
