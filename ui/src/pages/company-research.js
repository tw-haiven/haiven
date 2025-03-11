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
  ConfigProvider,
} from "antd";
import { SearchOutlined, StopOutlined } from "@ant-design/icons";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";

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
        className="competitor-list"
        renderItem={(item, index) => (
          <Card
            key={index}
            size="small"
            title={item.name}
            className="inner-result"
          >
            {item.rationale && (
              <div>
                <Text>
                  <strong>Rationale:</strong> {item.rationale}
                </Text>
              </div>
            )}
            {item.acquisitions && (
              <div>
                <Text>
                  <strong>Key Acquisitions:</strong> {item.acquisitions}
                </Text>
              </div>
            )}
          </Card>
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

  return (
    <ConfigProvider
      theme={{
        components: {
          Card: {
            headerBg: "var(--color-sapphire)",
          },
        },
      }}
    >
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
            <div style={{ marginTop: "10px" }}>
              Researching {companyName}...
            </div>
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
          <div className="research-results">
            <div className="research-results-section" style={{ width: "100%" }}>
              <Title level={3}>
                {companyData.business_brief?.comopany_name || companyName}
              </Title>

              <Row gutter={[12, 12]} className="results-row">
                <Col xs={24} lg={8} className="results-column">
                  {companyData.business_brief && (
                    <Card
                      title="Business Snapshot"
                      loading={loading && !companyData.business_brief}
                    >
                      <DynamicDataRenderer
                        data={companyData.business_brief}
                        excludeKeys={["comopany_name"]}
                      />
                    </Card>
                  )}
                </Col>

                <Col xs={24} lg={8} className="results-column">
                  {companyData.org_priorities && (
                    <Card
                      title="Vision & Strategic Priorities"
                      loading={loading && !companyData.org_priorities}
                    >
                      <DynamicDataRenderer data={companyData.org_priorities} />
                    </Card>
                  )}

                  {companyData.competitors && (
                    <Card
                      title="Competitors"
                      loading={loading && !companyData.competitors}
                    >
                      <CompetitorsList competitors={companyData.competitors} />
                    </Card>
                  )}

                  {companyData.domain_terms && (
                    <Card
                      title="Domain Terms"
                      loading={loading && !companyData.domain_terms}
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
                </Col>

                <Col xs={24} lg={8} className="results-column">
                  {companyData.domain_functions && (
                    <Card
                      title="Domain Functions"
                      loading={loading && !companyData.domain_functions}
                    >
                      <div className="results-column">
                        {companyData.domain_functions.map((item, index) => (
                          <Card
                            key={index}
                            size="small"
                            title={item.name}
                            className="inner-result"
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

            <Row gutter={[12, 12]} className="results-row citations-container">
              <Citations citations={citations} />
            </Row>
          </div>
        )}
      </div>
    </ConfigProvider>
  );
}
