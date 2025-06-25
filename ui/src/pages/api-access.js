// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Typography } from "antd";
import TemporaryLinkGenerator from "../app/_temporary_link_generator";

const { Title, Paragraph } = Typography;

const ApiAccessPage = () => {
  return (
    <div className="api-access-page">
      <div style={{ marginBottom: "24px" }}>
        <Title level={1}>API Access Management</Title>
        <Paragraph>
          Generate temporary links that can be shared with external users to
          create API keys for programmatic access to Haiven. These links provide
          a secure way to distribute authentication credentials.
        </Paragraph>
        <Paragraph>
          <strong>How it works:</strong>
        </Paragraph>
        <ol>
          <li>Generate a temporary link below</li>
          <li>Share the temporary link with the intended user</li>
          <li>
            The user opens the link in their browser to automatically generate
            their API key
          </li>
          <li>
            The API key is displayed once and must be copied and saved securely
          </li>
        </ol>
      </div>

      <TemporaryLinkGenerator />
    </div>
  );
};

export default ApiAccessPage;
