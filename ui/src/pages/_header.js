import { Menu } from "antd";
import Image from "next/image";

export default function Header() {
  return (
    <div className="page-header">
      <header class="header">
        <div class="left-section">
          <div class="logo">
            <img src="/boba/thoughtworks_logo.png" alt="Logo" />
          </div>
          <div class="separator"></div>
          <div class="title">Haiven team assistant</div>
        </div>
        <div class="mode-switch">
          <span>Choose your working mode</span>
          <button class="mode-button" id="standardMode">
            Guided mode
          </button>
          <button class="mode-button" id="advancedMode">
            Chat mode
          </button>
        </div>
      </header>
    </div>
  );
}
