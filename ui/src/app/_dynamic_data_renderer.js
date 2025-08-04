// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import { List, Card, Typography } from "antd";

const { Text } = Typography;

const EXCLUDE = [
  "title",
  "hidden",
  "exclude",
  "id",
  "scenarios",
  "self-review",
];

// Helper function to convert camelCase or snake_case to readable text
export const toReadableText = (key) => {
  return key
    .replace(/[_-]/g, " ")
    .replace(/([A-Z])/g, " $1")
    .replace(/\s+/g, " ")
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
};

export const scenarioToText = (data, exclude = [], headerLevel = 2) => {
  // When called through Array.map, the second parameter is the index, not the exclude array
  // Check if exclude is a number (index from map) and reset it
  if (typeof exclude === "number") {
    headerLevel = 2; // Reset to default
    exclude = [];
  }

  // Create header with the appropriate number of # symbols
  const headerPrefix = "#".repeat(headerLevel);
  let markdown = `${headerPrefix} ${data.title}\n\n`;
  const excludeKeys = EXCLUDE.concat(exclude);
  Object.keys(data).forEach((key) => {
    if (key === "scenarios" && Array.isArray(data[key])) {
      // Process child scenarios with one level deeper header and append to parent's markdown
      data[key].forEach((s) => {
        markdown += scenarioToText(s, exclude, headerLevel + 1);
      });
    } else if (!excludeKeys.includes(key)) {
      const value = data[key];
      if (Array.isArray(value)) {
        markdown += `**${key.charAt(0).toUpperCase() + key.slice(1)}:**\n${value.map((item) => `- ${item}`).join("\n")}\n\n`;
      } else {
        markdown += `**${key.charAt(0).toUpperCase() + key.slice(1)}:**\n${value}\n\n`;
      }
    }
  });
  return markdown;
};

// Dynamic renderer for any object data
export const DynamicDataRenderer = ({
  data,
  exclude = [],
  skipTitles = false,
  className = "",
}) => {
  if (!data) {
    return <Text></Text>;
  }

  if (typeof data === "string") {
    return <Text>{data}</Text>;
  }

  if (typeof data !== "object") {
    return <Text></Text>;
  }

  // Render URLs
  if (
    Object.keys(data).length === 2 &&
    Object.keys(data).every((key) => ["title", "url"].includes(key))
  ) {
    return (
      <a href={data.url} target="_blank" rel="noopener noreferrer">
        {data.title}
      </a>
    );
  }

  const excludeKeys = EXCLUDE.concat(exclude);

  return (
    <List
      itemLayout="horizontal"
      size="small"
      dataSource={Object.entries(data).filter(
        ([key]) => !excludeKeys.includes(key),
      )}
      className={className}
      renderItem={([key, value]) => {
        if (value === null || value === undefined) return null;

        return (
          <List.Item style={{ padding: "4px 0" }}>
            <div style={{ width: "100%" }}>
              {!skipTitles && <Text strong>{toReadableText(key)}:</Text>}
              {renderValue(value, key)}
            </div>
          </List.Item>
        );
      }}
    />
  );
};

// Helper to render different value types
export const renderValue = (value, parentKey) => {
  if (value === undefined || value === null) {
    return <span> -</span>; // Replace "Unknown" with a dash
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return <span> None</span>;

    if (typeof value[0] === "object" && value[0] !== null) {
      // Array of objects
      return (
        <List
          itemLayout="vertical"
          dataSource={value}
          renderItem={(item, index) => (
            <List.Item>
              <Card
                size="small"
                title={item.name || item.title || `Item ${index + 1}`}
                style={{ marginBottom: "8px" }}
              >
                <DynamicDataRenderer
                  data={item}
                  excludeKeys={["name", "title"]}
                />
              </Card>
            </List.Item>
          )}
        />
      );
    } else {
      // Array of primitives
      return (
        <ul style={{ margin: "0 0 0 20px", paddingLeft: 0 }}>
          {value.map((item, index) => (
            <li key={index}>{item || "-"}</li>
          ))}
        </ul>
      );
    }
  } else if (typeof value === "object" && value !== null) {
    // For nested objects, check if they're special cases
    // These objects have a property with the same name as the parent key
    const hasMatchingProperty = parentKey && value[parentKey] !== undefined;

    if (hasMatchingProperty) {
      // If the object has a property matching its parent key, just show that value directly
      return (
        <div>
          <span>{value[parentKey]}</span>
          {/* Render other properties if any */}
          {Object.keys(value).length > 1 && (
            <DynamicDataRenderer data={value} excludeKeys={[parentKey]} />
          )}
        </div>
      );
    } else {
      // Standard nested object
      return <DynamicDataRenderer data={value} />;
    }
  } else if (value === "") {
    // Empty string
    return <span> -</span>;
  } else {
    // Primitive value
    return <span> {value}</span>;
  }
};

export default DynamicDataRenderer;
