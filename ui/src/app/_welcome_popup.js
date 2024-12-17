// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { Modal, Button } from "antd";
import Cookies from "js-cookie";

const COOKIE_NAME = "haiven_welcome_shown";
const COOKIE_EXPIRY = 365;

const WelcomePopup = ({ welcomeConfig, showBeforeLogin = false }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);

    if (!isMounted || !welcomeConfig) return;

    const showWelcomeMessage = () => {
      if (showBeforeLogin) {
        setIsVisible(true);
        return;
      }

      const hasSeenWelcome =
        Cookies.get(COOKIE_NAME) || localStorage.getItem(COOKIE_NAME);

      if (!hasSeenWelcome) {
        setIsVisible(true);
      }
    };

    showWelcomeMessage();

    return () => {
      setIsMounted(false);
    };
  }, [welcomeConfig, showBeforeLogin, isMounted]);

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

  if (!isMounted || !welcomeConfig) return null;

  return (
    <Modal
      title={welcomeConfig.title || "Welcome to Haiven"}
      open={isVisible}
      onCancel={handleClose}
      footer={[
        <Button key="close" type="primary" onClick={handleClose}>
          {showBeforeLogin ? "Continue to Login" : "I understand"}
        </Button>,
      ]}
      centered
      style={{ height: "90%" }}
      bodyStyle={{ maxHeight: "calc(100vh - 200px)", overflowY: "auto" }}
    >
      <div
        style={{ overflowY: "auto", maxHeight: "100%" }}
        dangerouslySetInnerHTML={{ __html: welcomeConfig.message }}
      />
    </Modal>
  );
};

export default WelcomePopup;
