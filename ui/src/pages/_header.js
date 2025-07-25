// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import Link from "next/link";
import { Button } from "antd";
import { RiPushpinLine } from "react-icons/ri";
import Pinboard from "./pinboard";
import { FEATURES } from "../app/feature_toggle";

export default function Header({ featureToggleConfig }) {
  const [isPinboardVisible, setIsPinboardVisible] = useState(false);

  const openPinboard = () => {
    setIsPinboardVisible(true);
  };

  const closePinboard = () => {
    setIsPinboardVisible(false);
  };

  const openForm = () => {
    // Open the form in a new tab
    window.open(
      "https://docs.google.com/forms/d/e/1FAIpQLSessXVgqe0CBv3NWtcmqq8-lYSPalP38PYQjI77QwI_1qS8Vw/viewform",
      "_blank",
    );
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
              <span>
                <Link
                  href="#"
                  onClick={(e) => {
                    e.preventDefault(); // prevents navigation
                    openForm();
                  }}
                >
                  Submit Prompt
                </Link>
              </span>

              <span type="link">
                <Link href="/about">About</Link>
              </span>
              <span type="link">
                <Link href="/knowledge">Knowledge Overview</Link>
              </span>
              {featureToggleConfig[FEATURES.API_KEY_AUTH] === true && (
                <span type="link">
                  <Link href="/api-keys">API Keys</Link>
                </span>
              )}
            </div>
            <div className="separator"></div>
            <div className="pinboard">
              <Button
                type="link"
                onClick={openPinboard}
                style={{ color: "white" }}
              >
                <RiPushpinLine fontSize="large" />
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
