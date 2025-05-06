// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  Col,
  Row,
  Button,
  Input,
  Card,
  List,
  Typography,
  Form,
  ConfigProvider,
  Collapse,
} from "antd";
import { RiSendPlane2Line } from "react-icons/ri";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "../pages/_chat_header";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";
import Citations from "../pages/_citations";

const { Title } = Typography;

export default function CompanyResearchPageNew() {
  const [researchConfig, setResearchConfig] = useState(null);
  const [companyName, setCompanyName] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);

  const availableResearchConfig = {
    company: {
      title: "Company Research",
      key: "company",
      column1: [{ title: "Business Snapshot", property: "business_brief" }],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Domain Terms", property: "domain_terms" },
      ],
      column3: [{ title: "Domain Functions", property: "domain_functions" }],
    },
    "ai-tool": {
      title: "AI Tool Research",
      key: "ai-tool",
      column1: [
        { title: "Business Snapshot", property: "business_brief" },
        { title: "Reception", property: "reception" },
      ],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Did you know?", property: "other_tidbits" },
      ],
      column3: [
        {
          title: "Software Delivery Lifecycle Support",
          property: "software_lifecycle",
        },
        { title: "Key resources", property: "key_resources" },
      ],
    },
  };

  const searchParams = useSearchParams();

  useEffect(() => {
    const configParam = searchParams.get("config");
    console.log({ configParam });
    if (configParam && availableResearchConfig[configParam]) {
      setResearchConfig(availableResearchConfig[configParam]);
    } else {
      setResearchConfig(availableResearchConfig.company);
    }
  }, [searchParams]);

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
        body: JSON.stringify({ userinput: input, config: researchConfig.key }),
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

  const title = researchConfig && (
    <div className="title">
      <h3>
        {researchConfig.title}
        <HelpTooltip text="Get a company brief" />
      </h3>
    </div>
  );

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
          style={{ display: "flex", maxWidth: "450px" }}
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
            {!loading && (
              <Button htmlType="submit" icon={<RiSendPlane2Line />}>
                Research
              </Button>
            )}
          </Form.Item>
        </Form>
      </div>
    );
  };

  const createColumn = (columnConfig) => {
    return (
      <Col xs={24} lg={8} className="results-column">
        {columnConfig.map((item, index) => (
          <Card
            key={index}
            title={item.title}
            loading={loading && !companyData[item.property]}
          >
            {Array.isArray(companyData[item.property]) ? (
              companyData[item.property].map((listItem, listIndex) => (
                <Card
                  key={index + "-" + listIndex}
                  size="small"
                  className="inner-result"
                >
                  <DynamicDataRenderer data={listItem} />
                </Card>
              ))
            ) : (
              <DynamicDataRenderer data={companyData[item.property]} />
            )}
          </Card>
        ))}
      </Col>
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
      <ChatHeader
        models={{ chat: { name: "Perplexity AI" } }}
        titleComponent={title}
      />
      <div className="company-research dashboard">
        {inputAreaRender()}

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
            <div className="research-results-section">
              <div className="title-container">
                <Title level={3}>
                  {companyData.business_brief?.company_name || companyName}
                </Title>

                <StopLoad />
              </div>

              <Row gutter={[12, 12]} className="results-row">
                {createColumn(researchConfig.column1)}
                {createColumn(researchConfig.column2)}
                {createColumn(researchConfig.column3)}
              </Row>
            </div>

            <div className="follow-up-container">
              <div style={{ marginTop: "1em" }}>
                <h3>What you can do next</h3>
                <p>Generate content based on the cards above.</p>
              </div>
              <Collapse
                // items={followUpCollapseItems}
                className="second-step-collapsable"
                data-testid="follow-up-collapse"
              />
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
