// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useEffect } from "react";
import {
  Typography,
  Card,
  Button,
  Input,
  Space,
  Alert,
  Modal,
  Spin,
} from "antd";
import { useRouter } from "next/router";
import {
  RiKeyLine,
  RiFileCopyLine,
  RiCheckLine,
  RiEyeLine,
  RiEyeOffLine,
} from "react-icons/ri";
import { generateApiKey } from "../app/_boba_api";
import Head from "next/head";

const { Title, Text, Paragraph } = Typography;

const GenerateApiKeyPage = () => {
  const router = useRouter();
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [tokenFromUrl, setTokenFromUrl] = useState("");
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    // Extract token from URL query parameters
    if (router.query.token) {
      const token = router.query.token;
      setTokenFromUrl(token);
      setInitializing(false);
      // Automatically generate API key
      generateApiKeyFromToken(token);
    } else {
      setInitializing(false);
      setError(
        "No token provided in the link. Please check your temporary link and try again.",
      );
    }
  }, [router.query]);

  const generateApiKeyFromToken = (token) => {
    setLoading(true);
    setCopied(false);
    setError("");

    generateApiKey(
      token,
      (data) => {
        setApiKey(data.api_key);
        setLoading(false);
        setShowModal(true);
        setShowApiKey(false);
      },
      (err) => {
        setError(err.message || "Failed to generate API key");
        setLoading(false);
      },
    );
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(apiKey);
      setCopied(true);

      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to copy API key to clipboard");
    }
  };

  const handleModalClose = () => {
    setShowModal(false);
    setApiKey("");
    setShowApiKey(false);
    setCopied(false);
  };

  const toggleApiKeyVisibility = () => {
    setShowApiKey(!showApiKey);
  };

  const maskApiKey = (key) => {
    if (!key) return "";
    if (key.length <= 8) return "*".repeat(key.length);
    return (
      key.substring(0, 4) +
      "*".repeat(key.length - 8) +
      key.substring(key.length - 4)
    );
  };

  if (initializing) {
    return (
      <>
        <Head>
          <title>Generate API Key - Haiven</title>
        </Head>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
          }}
        >
          <Spin size="large" />
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>Generate API Key - Haiven</title>
      </Head>
      <div
        style={{
          minHeight: "100vh",
          backgroundColor: "#f5f5f5",
          padding: "40px 20px",
        }}
      >
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <Title level={1}>Haiven API Key Generation</Title>
            <Paragraph>
              Generate your API key for programmatic access to Haiven services.
            </Paragraph>
          </div>

          <Card>
            <Space direction="vertical" size="large" style={{ width: "100%" }}>
              {loading && (
                <div style={{ textAlign: "center" }}>
                  <Spin size="large" />
                  <div style={{ marginTop: "16px" }}>
                    <Text>Generating your API key...</Text>
                  </div>
                </div>
              )}

              {error && (
                <Alert
                  message="Error"
                  description={error}
                  type="error"
                  showIcon
                />
              )}

              {!loading && !error && !showModal && (
                <div style={{ textAlign: "center" }}>
                  <Title level={3}>
                    <RiKeyLine style={{ marginRight: "8px" }} />
                    Processing your request...
                  </Title>
                  <Paragraph>
                    Your API key is being generated. Please wait a moment.
                  </Paragraph>
                </div>
              )}
            </Space>
          </Card>

          <Modal
            title={
              <span>
                <RiKeyLine style={{ marginRight: "8px" }} />
                Your Haiven API Key
              </span>
            }
            open={showModal}
            onCancel={handleModalClose}
            footer={null}
            width={700}
            maskClosable={false}
            centered
          >
            <Space direction="vertical" size="large" style={{ width: "100%" }}>
              <Alert
                message="🔑 Important: Save this API key now!"
                description="This API key will not be shown again. Copy it to a secure location before closing this window. You'll need this key to authenticate API requests to Haiven."
                type="warning"
                showIcon
              />

              <div>
                <Text strong style={{ fontSize: "16px" }}>
                  Your API Key:
                </Text>
                <div style={{ marginTop: "12px" }}>
                  <Space.Compact style={{ width: "100%" }}>
                    <Input
                      value={showApiKey ? apiKey : maskApiKey(apiKey)}
                      readOnly
                      style={{
                        width: "calc(100% - 200px)",
                        fontFamily: "monospace",
                        fontSize: "14px",
                      }}
                    />
                    <Button
                      onClick={toggleApiKeyVisibility}
                      icon={showApiKey ? <RiEyeOffLine /> : <RiEyeLine />}
                      style={{ width: "80px" }}
                    >
                      {showApiKey ? "Hide" : "Show"}
                    </Button>
                    <Button
                      type="primary"
                      onClick={copyToClipboard}
                      icon={copied ? <RiCheckLine /> : <RiFileCopyLine />}
                      style={{ width: "120px" }}
                    >
                      {copied ? "Copied!" : "Copy"}
                    </Button>
                  </Space.Compact>
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "#f6f8fa",
                  padding: "16px",
                  borderRadius: "6px",
                }}
              >
                <Text strong>How to use your API key:</Text>
                <ul style={{ marginTop: "8px", marginBottom: "0" }}>
                  <li>
                    Include it in the Authorization header:{" "}
                    <code>Bearer YOUR_API_KEY</code>
                  </li>
                  <li>
                    Store it securely in your application's environment
                    variables
                  </li>
                  <li>
                    Never share it publicly or commit it to version control
                  </li>
                </ul>
              </div>

              <div style={{ textAlign: "right" }}>
                <Button type="primary" onClick={handleModalClose} size="large">
                  I've saved my API key
                </Button>
              </div>
            </Space>
          </Modal>
        </div>
      </div>
    </>
  );
};

// This tells Next.js to render this page without the main layout
GenerateApiKeyPage.getLayout = function getLayout(page) {
  return page;
};

export default GenerateApiKeyPage;
