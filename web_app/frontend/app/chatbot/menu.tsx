import React from "react";
import "./menu.css";

interface MenuProps {
  theme: "light" | "dark";
  setTheme: (t: "light" | "dark") => void;
  minimized: boolean;
  setMinimized: (m: boolean) => void;
}

const Menu: React.FC<MenuProps> = ({ theme, setTheme, minimized, setMinimized }) => {
  if (minimized) {
    return (
      <div className={`chatbot-menu-panel minimized${theme === "dark" ? " chatbot-dark" : ""}`}> 
        <div className="chatbot-menu-bubble" onClick={() => setMinimized(false)} title="Open menu">
          <span>≡</span>
        </div>
      </div>
    );
  }
  return (
    <aside className={`chatbot-menu-panel${theme === "dark" ? " chatbot-dark" : ""}`}> 
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 className="chatbot-menu-title">Settings</h1>
        <button onClick={() => setMinimized(true)} style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer" }} title="Minimize menu">–</button>
      </div>
      <div className="chatbot-menu-row" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <h2 className="chatbot-menu-label" style={{ fontSize: 12, fontWeight: 600, letterSpacing: 0.5, textTransform: "uppercase", opacity: .75 }}>Theme</h2>
        <select
          className="chatbot-menu-select"
          value={theme}
          aria-label="Theme selection"
          onChange={e => setTheme(e.target.value as "light" | "dark")}
          style={{
            background: "var(--ai-bg-inset)",
            border: "1px solid var(--ai-border)",
            color: "var(--ai-text)",
            padding: "0.55rem 0.65rem",
            borderRadius: "var(--ai-radius-md)",
            fontSize: 14,
            cursor: "pointer",
            boxShadow: "var(--ai-shadow-sm)",
            transition: "var(--ai-transition)",
            outline: "none"
          }}
          onFocus={e => (e.currentTarget.style.boxShadow = "0 0 0 3px rgba(var(--ai-accent-rgb),0.35)")}
          onBlur={e => (e.currentTarget.style.boxShadow = "var(--ai-shadow-sm)")}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
    </aside>
  );
};

export default Menu;

