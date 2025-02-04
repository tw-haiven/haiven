// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { Modal, Button } from "antd";
import Cookies from "js-cookie";
import ReactMarkdown from "react-markdown";

const COOKIE_NAME = "haiven_welcome_shown";
const COOKIE_EXPIRY = 365;

const DisclaimerPopup = ({ disclaimerConfig, showBeforeLogin = false }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);

    if (!isMounted || !disclaimerConfig) return;

    const showDisclaimerMessage = () => {
      if (showBeforeLogin) {
        setIsVisible(true);
        return;
      }

      const hasSeenDisclaimer =
        Cookies.get(COOKIE_NAME) || localStorage.getItem(COOKIE_NAME);

      if (!hasSeenDisclaimer) {
        setIsVisible(true);
      }
    };

    showDisclaimerMessage();

    return () => {
      setIsMounted(false);
    };
  }, [disclaimerConfig, showBeforeLogin, isMounted]);

  const handleClose = () => {
    if (!showBeforeLogin) {
      try {
        Cookies.set(COOKIE_NAME, "true", { expires: COOKIE_EXPIRY });
      } catch (e) {
        localStorage.setItem(COOKIE_NAME, "true");
      }
    }
    setIsVisible(false);
  };

  if (!isMounted || !disclaimerConfig) return null;

  return (
    <Modal
      title={disclaimerConfig.title || "Welcome to Haiven"}
      open={isVisible}
      onCancel={handleClose}
      footer={[
        <Button key="close" type="primary" onClick={handleClose}>
          {showBeforeLogin ? "Continue to Login" : "I understand"}
        </Button>,
      ]}
      centered
      className="disclaimer-popup"
    >
      <div style={{ overflowY: "auto", maxHeight: "100%" }}>
        <ReactMarkdown>{disclaimerConfig.message}</ReactMarkdown>
      </div>
    </Modal>
  );
};

export default DisclaimerPopup;
