import React from "react";
import Menu from "./menu";

interface MobileMenuProps {
  minimized: boolean;
  setMinimized: (v: boolean) => void;
  username: string | null;
  onRequestLogout: () => void;
}

const MobileMenu: React.FC<MobileMenuProps> = ({ minimized, setMinimized, username, onRequestLogout }) => {
  if (minimized) return null;

  return (
    <div className="md:hidden">
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40 bg-black/50"
        onClick={() => setMinimized(true)}
      />
      {/* Side drawer */}
      <div className="fixed left-0 top-0 bottom-0 z-50 w-72 max-w-[80vw] bg-gray-900 border-r border-gray-700 p-4 shadow-xl">
        <Menu
          minimized={false}  
          setMinimized={setMinimized}
          username={username}
          onRequestLogout={onRequestLogout}
        />
      </div>
    </div>
  );
};

export default MobileMenu;
