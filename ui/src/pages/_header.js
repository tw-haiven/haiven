// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import Link from "next/link";
import { Button } from "antd";
import { PinIcon } from "lucide-react";
import Pinboard from "./pinboard";

export default function Header() {
  const [isPinboardVisible, setIsPinboardVisible] = useState(false);

  const openPinboard = () => {
    setIsPinboardVisible(true);
  };

  const closePinboard = () => {
    setIsPinboardVisible(false);
  };

  return (
    <>
      <div className="page-header">
        <header className="header">
          <div className="left-section">
            <div className="logo">
              <img src="/boba/thoughtworks_logo.png" alt="Logo" />
            </div>
            <div className="separator"></div>
            <div className="title">Haiven team assistant</div>
          </div>
          <div
            className="header-links"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div>
              <span type="link">
                <Link href="/about">About</Link>
              </span>
              <span type="link">
                <Link href="/knowledge">Knowledge Overview</Link>
              </span>
            </div>
            <div className="separator"></div>
            <div className="pinboard">
              <Button
                type="link"
                onClick={openPinboard}
                style={{ color: "white" }}
              >
                <PinIcon size={14} style={{ transform: "rotate(45deg)" }} />
                Pinboard
              </Button>
            </div>
          </div>
        </header>
      </div>
      <Pinboard isModalVisible={isPinboardVisible} onClose={closePinboard} />
    </>
  );
}
