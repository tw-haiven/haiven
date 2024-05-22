import { Menu } from "antd";
import Image from "next/image";

export default function Header() {
  return (
    <div className="page-header">
      <header className="header">
        <div className="left-section">
          <div className="logo">
            <img src="/boba/thoughtworks_logo.png" alt="Logo" />
          </div>
          <div className="separator"></div>
          <div className="title">Haiven team assistant</div>
        </div>
        <div className="mode-switch">
          <span>Choose your working mode</span>
          <button className="mode-button" id="standardMode">
            Guided mode
          </button>
          <button className="mode-button" id="advancedMode">
            Chat mode
          </button>
        </div>
      </header>
    </div>
  );
}
