// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
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
          <button className="mode-button mode-selected mode-left">
            Guided mode
          </button>
          <button className="mode-button mode-other mode-right">
            <a href="/analysis">Chat mode</a>
          </button>
        </div>
      </header>
    </div>
  );
}
