// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { List, Typography } from "antd";

const Citations = ({ citations }) => {
  if (!citations || !Array.isArray(citations) || citations.length === 0) {
    return null;
  }

  return (
    <div className="citations-section">
      <Typography.Title level={5} style={{ marginTop: "0" }}>
        Sources
      </Typography.Title>
      <List
        size="small"
        itemLayout="horizontal"
        dataSource={citations}
        style={{ fontSize: "12px" }}
        renderItem={(citation) => {
          // Handle both string URLs and object citations
          const url = typeof citation === "string" ? citation : citation.url;

          if (!url) return null;

          return (
            <List.Item style={{ padding: "2px 0" }}>
              <ul
                style={{
                  listStyleType: "disc",
                  margin: 0,
                  paddingLeft: "20px",
                }}
              >
                <li>
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontSize: "12px", lineHeight: "1.2" }}
                  >
                    {url}
                  </a>
                </li>
              </ul>
            </List.Item>
          );
        }}
      />
    </div>
  );
};

export default Citations;
