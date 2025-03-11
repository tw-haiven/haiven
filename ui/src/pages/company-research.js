// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import {
  Col,
  Row,
  Button,
  Input,
  Card,
  Spin,
  List,
  Typography,
  Form,
} from "antd";
import { SearchOutlined, StopOutlined } from "@ant-design/icons";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";

const { Title, Text } = Typography;

export default function CompanyResearchPage() {
  const [companyName, setCompanyName] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);

  const handleSearch = async (input) => {
    if (!input.trim()) {
      toast.warning("Please enter a company name");
      return;
    }

    setCompanyName(input);
    setDisableInput(true);
    setCompanyData(null);
    setCitations([]);
    setError(null);

    const uri = `/api/research`;

    let jsonResponse = "";

    fetchSSE(
      uri,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userinput: input }),
        signal: startLoad(),
      },
      {
        json: true,
        onErrorHandle: (err) => {
          setDisableInput(false);
          setError("Error fetching company data. Please try again.");
          console.error("Error:", err);
          abortLoad();
        },
        onFinish: () => {
          setDisableInput(false);
          if (jsonResponse === "") {
            setError("No data received. Please try again.");
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          try {
            if (data.data) {
              jsonResponse += data.data;

              // Clean up the response if needed
              jsonResponse = jsonResponse.trim();

              // Try to parse the JSON even if it's incomplete
              try {
                const parsedData = parse(jsonResponse);
                if (parsedData && typeof parsedData === "object") {
                  setCompanyData(parsedData);
                }
              } catch (error) {
                // This is expected for partial JSON, no need to log every attempt
              }
            } else if (data.metadata) {
              // Safely handle citations if they exist in metadata
              if (data.metadata.citations) {
                setCitations(data.metadata.citations);
              }
            }
          } catch (error) {
            console.log(
              "Error processing message:",
              error,
              "data received:",
              data,
            );
          }
        },
      },
    );
  };

  // Helper function to convert camelCase or snake_case to readable text
  const toReadableText = (key) => {
    return key
      .replace(/_/g, " ")
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase())
      .trim();
  };

  // Dynamic renderer for any object data
  const DynamicDataRenderer = ({
    data,
    excludeKeys = [],
    skipTitles = false,
  }) => {
    if (!data || typeof data !== "object") {
      return <Text>No data available</Text>;
    }

    return (
      <List
        itemLayout="horizontal"
        size="small"
        dataSource={Object.entries(data).filter(
          ([key]) => !excludeKeys.includes(key),
        )}
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
  const renderValue = (value, parentKey) => {
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
      // For nested objects, check if they're special cases like vision, priorities, kpis
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

  // Specific component for competitors which may have a special format
  const CompetitorsList = ({ competitors }) => {
    if (
      !competitors ||
      !Array.isArray(competitors) ||
      competitors.length === 0
    ) {
      return <Text>No competitor information available</Text>;
    }

    return (
      <List
        itemLayout="vertical"
        size="small"
        dataSource={competitors}
        renderItem={(item) => (
          <List.Item style={{ padding: "4px 0" }}>
            <Text strong>{item.name}</Text>
            {item.rationale && (
              <div style={{ marginTop: "2px" }}>
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  Rationale:
                </Text>{" "}
                {item.rationale}
              </div>
            )}
            {item.acquisitions && (
              <div style={{ marginTop: "2px" }}>
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  Key Acquisitions:
                </Text>{" "}
                {item.acquisitions}
              </div>
            )}
          </List.Item>
        )}
      />
    );
  };

  const Citations = ({ citations }) => {
    if (!citations || !Array.isArray(citations) || citations.length === 0) {
      return null;
    }

    return (
      <div className="citations-section">
        <Title
          level={5}
          style={{ marginTop: "0", marginBottom: "8px", fontSize: "14px" }}
        >
          Sources
        </Title>
        <List
          size="small"
          itemLayout="horizontal"
          dataSource={citations}
          style={{ fontSize: "12px" }}
          renderItem={(citation, index) => {
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

  const inputAreaRender = () => {
    const [form] = Form.useForm();

    const handleKeyDown = (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.submit();
      }
    };

    if (disableInput) {
      return null;
    }

    return (
      <div className="search-container" style={{ marginBottom: "20px" }}>
        <Form
          onFinish={async (value) => {
            await handleSearch(value.companyName);
            form.resetFields();
          }}
          form={form}
          initialValues={{ companyName: "" }}
          className="company-search-form"
          style={{ display: "flex", alignItems: "center" }}
        >
          <Form.Item
            name="companyName"
            rules={[{ required: true, message: "Please enter a company name" }]}
            style={{ marginBottom: 0, marginRight: "10px", flex: 1 }}
          >
            <Input
              placeholder="Enter company name"
              disabled={loading}
              onKeyDown={handleKeyDown}
              style={{ width: "100%", maxWidth: "300px" }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            {loading ? (
              <Button
                type="default"
                icon={<StopOutlined />}
                onClick={() => abortLoad()}
              >
                Stop
              </Button>
            ) : (
              <Button
                type="primary"
                htmlType="submit"
                icon={<SearchOutlined />}
              >
                Research
              </Button>
            )}
          </Form.Item>
        </Form>
      </div>
    );
  };

  return (
    <div className="company-research dashboard">
      <div className="title">
        <h3>
          Company Research
          <HelpTooltip text="Research companies to understand their business model, market position, competitors, and future prospects." />
        </h3>
      </div>

      {inputAreaRender()}

      {loading && (
        <div
          className="loading-container"
          style={{ textAlign: "center", margin: "40px 0" }}
        >
          <Spin size="large" />
          <div style={{ marginTop: "10px" }}>Researching {companyName}...</div>
        </div>
      )}

      {error && (
        <div
          className="error-container"
          style={{ color: "red", margin: "20px 0" }}
        >
          {error}
        </div>
      )}

      {companyData && (
        <div>
          <div className="research-results">
            <Title level={3}>
              {companyData.business_brief?.comopany_name || companyName}
            </Title>

            <Row
              gutter={[12, 12]}
              style={{ height: "calc(100vh - 250px)", minHeight: "600px" }}
            >
              {/* Column 1: Business Brief (Business Snapshot) */}
              <Col xs={24} lg={8} style={{ height: "100%" }}>
                {companyData.business_brief && (
                  <Card
                    title="Business Snapshot"
                    loading={loading && !companyData.business_brief}
                    style={{ height: "100%", overflow: "auto" }}
                    headStyle={{ backgroundColor: "var(--color-light-gray)" }}
                    bodyStyle={{ padding: "12px" }}
                  >
                    <DynamicDataRenderer
                      data={companyData.business_brief}
                      excludeKeys={["comopany_name"]}
                    />
                  </Card>
                )}
              </Col>

              {/* Column 2: Vision & Strategic Priorities, Competitors, Domain Terms */}
              <Col xs={24} lg={8} style={{ height: "100%" }}>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    height: "100%",
                    gap: "12px",
                  }}
                >
                  {/* Vision & Strategic Priorities */}
                  {companyData.org_priorities && (
                    <Card
                      title="Vision & Strategic Priorities"
                      loading={loading && !companyData.org_priorities}
                      style={{ flex: "1 0 auto" }}
                      headStyle={{ backgroundColor: "var(--color-light-gray)" }}
                      bodyStyle={{ padding: "12px" }}
                    >
                      <DynamicDataRenderer data={companyData.org_priorities} />
                    </Card>
                  )}

                  {/* Competitors */}
                  {companyData.competitors && (
                    <Card
                      title="Competitors"
                      loading={loading && !companyData.competitors}
                      style={{ flex: "1 0 auto" }}
                      headStyle={{ backgroundColor: "var(--color-light-gray)" }}
                      bodyStyle={{ padding: "12px" }}
                    >
                      <CompetitorsList competitors={companyData.competitors} />
                    </Card>
                  )}

                  {/* Domain Terms */}
                  {companyData.domain_terms && (
                    <Card
                      title="Domain Terms"
                      loading={loading && !companyData.domain_terms}
                      style={{ flex: "1 0 auto" }}
                      headStyle={{ backgroundColor: "var(--color-light-gray)" }}
                      bodyStyle={{ padding: "12px" }}
                    >
                      <List
                        itemLayout="horizontal"
                        size="small"
                        dataSource={companyData.domain_terms}
                        renderItem={(item) => (
                          <List.Item style={{ padding: "4px 0" }}>
                            <div style={{ width: "100%" }}>
                              <Text strong>{item.term}</Text>
                              {item.acronym && (
                                <Text type="secondary"> ({item.acronym})</Text>
                              )}
                              {item.meaning && (
                                <div
                                  style={{ marginTop: "2px", fontSize: "13px" }}
                                >
                                  {item.meaning}
                                </div>
                              )}
                            </div>
                          </List.Item>
                        )}
                      />
                    </Card>
                  )}
                </div>
              </Col>

              {/* Column 3: Domain Functions */}
              <Col xs={24} lg={8} style={{ height: "100%" }}>
                {companyData.domain_functions && (
                  <Card
                    title="Domain Functions"
                    loading={loading && !companyData.domain_functions}
                    style={{ height: "100%", overflow: "auto" }}
                    headStyle={{ backgroundColor: "var(--color-light-gray)" }}
                    bodyStyle={{ padding: "12px" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "12px",
                      }}
                    >
                      {companyData.domain_functions.map((item, index) => (
                        <Card
                          key={index}
                          size="small"
                          title={item.name}
                          headStyle={{
                            backgroundColor: "var(--color-light-gray)",
                            padding: "8px 12px",
                          }}
                          bodyStyle={{ padding: "8px 12px" }}
                        >
                          <DynamicDataRenderer
                            data={item}
                            excludeKeys={["name"]}
                          />
                        </Card>
                      ))}
                    </div>
                  </Card>
                )}
              </Col>
            </Row>
          </div>

          <div
            className="citations-container"
            style={{
              marginTop: "16px",
              padding: "12px",
              backgroundColor: "var(--color-light-gray)",
              borderRadius: "4px",
            }}
          >
            <Citations citations={citations} />
          </div>
        </div>
      )}
    </div>
  );
}
