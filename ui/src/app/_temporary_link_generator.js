// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Button, Card, Input, Typography, message, Space, Alert } from "antd";
import { RiLinkM, RiFileCopyLine, RiCheckLine } from "react-icons/ri";
import { getTemporaryLink } from "./_boba_api";

const { Title, Text, Paragraph } = Typography;

const TemporaryLinkGenerator = () => {
  const [temporaryLink, setTemporaryLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const generateLink = () => {
    setLoading(true);
    setCopied(false);
    setError("");

    getTemporaryLink(
      (data) => {
        setTemporaryLink(data.temporary_link);
        setLoading(false);
      },
      (err) => {
        setError(err.message || "Failed to generate temporary link");
        setLoading(false);
      },
    );
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(temporaryLink);
      setCopied(true);
      message.success("Link copied to clipboard!");

      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      message.error("Failed to copy link to clipboard");
    }
  };

  return (
    <div className="temporary-link-generator">
      <Card>
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div>
            <Title level={3}>
              <RiLinkM style={{ marginRight: "8px" }} />
              Generate Temporary API Link
            </Title>
            <Paragraph>
              Generate a secure temporary link that can be shared with external
              users. When they open this link in their browser, they will
              automatically receive an API key for accessing Haiven
              programmatically. This link is secure and has a limited lifespan.
            </Paragraph>
          </div>

          <div>
            <Button
              type="primary"
              onClick={generateLink}
              loading={loading}
              icon={<RiLinkM />}
              size="large"
            >
              {loading ? "Generating..." : "Generate Temporary Link"}
            </Button>
          </div>

          {error && (
            <Alert message="Error" description={error} type="error" showIcon />
          )}

          {temporaryLink && (
            <div>
              <Text strong>Generated Temporary Link:</Text>
              <div style={{ marginTop: "8px" }}>
                <Space.Compact style={{ width: "100%" }}>
                  <Input
                    value={temporaryLink}
                    readOnly
                    style={{ width: "calc(100% - 120px)" }}
                  />
                  <Button
                    type={copied ? "default" : "primary"}
                    onClick={copyToClipboard}
                    icon={copied ? <RiCheckLine /> : <RiFileCopyLine />}
                    style={{ width: "120px" }}
                  >
                    {copied ? "Copied!" : "Copy Link"}
                  </Button>
                </Space.Compact>
              </div>
              <div style={{ marginTop: "8px" }}>
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  Share this link with the external user. When they open it in
                  their browser, they will automatically receive their API key.
                  This link is temporary and will expire.
                </Text>
              </div>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default TemporaryLinkGenerator;
