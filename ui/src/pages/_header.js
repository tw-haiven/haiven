// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import Link from "next/link";
import { Button } from "antd";

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
        <div className="header-links">
          <span type="link">
            <Link href="/about">About</Link>
          </span>
          <span type="link">
            <Link href="/knowledge">Knowledge Overview</Link>
          </span>
        </div>
      </header>
    </div>
  );
}
