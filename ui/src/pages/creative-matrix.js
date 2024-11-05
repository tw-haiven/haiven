// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { Input, Button, Spin, Select, Collapse, message } from "antd";
import { MenuFoldOutlined } from "@ant-design/icons";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";
import { fetchSSE } from "../app/_fetch_sse";
import Disclaimer from "./_disclaimer";

let ctrl;

const CreativeMatrix = ({ models }) => {
  const [rowsCSV, setRowsCSV] = useState("For Customers, For Employees");
  const [columnsCSV, setColumnsCSV] = useState(
    "For Tactical or Operational Tasks, For Creative or Strategic Tasks",
  );
  const [prompt, setPrompt] = useState(
    "Inspire me with generative AI use cases for Nike",
  );
  const [ideaQualifiers, setIdeaQualifiers] = useState("");
  const [numberOfIdeas, setNumberOfIdeas] = useState(3);
  const [rows, setRows] = useState(rowsCSV.split(",").map((v) => v.trim()));
  const [columns, setColumns] = useState(
    columnsCSV.split(",").map((v) => v.trim()),
  );
  const [isExpanded, setIsExpanded] = useState(true);
  const [isLoading, setLoading] = useState(false);
  const [matrix, setMatrix] = useState([]);
  const [templates, setTemplates] = useState([
    {
      name: "Template: GenAI Use Case Exploration Matrix",
      prompt: "Inspire me with generative AI use cases for Nike",
      rowsCSV: "For Customers, For Employees",
      columnsCSV:
        "For Tactical or Operational Tasks, For Creative or Strategic Tasks",
    },
    {
      name: "Template: GenAI Industry Examples",
      prompt: "How might we use generative AI?",
      rowsCSV:
        "To create new products, To streamline operations, To reach new customers",
      columnsCSV: "Financial Services, Healthcare, Retail",
    },
    {
      name: "Template: GenAI Value Chain Use Cases",
      prompt:
        "Inspire me with generative AI use cases across the wealth management value chain",
      rowsCSV: "For clients, For employees",
      columnsCSV:
        "Client acquisition, Financial planning, Portfolio construction, Investment execution, Performance monitoring, Reporting & Communication",
    },
    {
      name: "Template: Product Ideation Matrix",
      prompt:
        "How might make package holidays more attractive to our customers?",
      rowsCSV: "Inclusions, Partnerships, Discounts, Experiences",
      columnsCSV: "Families, Couples, Young Singles, Retirees",
    },
    {
      name: "Template: Blank Matrix",
      prompt: '"How might we" question',
      rowsCSV: "Row 1, Row 2, Row 3",
      columnsCSV: "Column 1, Column 2, Column 3",
    },
  ]);

  const onChangeRowsCSV = (e) => {
    setRowsCSV(e.target.value);
    setRows(e.target.value.split(",").map((v) => v.trim()));
  };

  const onChangeColumnsCSV = (e) => {
    setColumnsCSV(e.target.value);
    setColumns(e.target.value.split(",").map((v) => v.trim()));
  };

  const onChangePrompt = (e) => {
    setPrompt(e.target.value);
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onChangeTemplate = (e) => {
    const template = templates.find((t) => t.name === e);
    setPrompt(template.prompt);
    setRowsCSV(template.rowsCSV);
    setColumnsCSV(template.columnsCSV);
    setRows(template.rowsCSV.split(",").map((v) => v.trim()));
    setColumns(template.columnsCSV.split(",").map((v) => v.trim()));
    setMatrix([]);
  };

  const handleSelectChange = (value) => {
    setNumberOfIdeas(value);
  };

  function onChangeIdeaQualifiers(e) {
    console.log(e);
    setIdeaQualifiers(e.join(", "));
  }

  const getMatrixCellValues = (rowIdx, columnIdx) => {
    const row = matrix[rowIdx] || [{ columns: [] }];
    const cell = (row && row.columns && row.columns[columnIdx]) || [
      { column: [], ideas: [] },
    ];
    let ret = cell || { ideas: [] };
    return ret.ideas || [];
  };

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
  }

  const onGenerateMatrix = () => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setIsExpanded(false);

    const uri =
      "/api/creative-matrix?rows=" +
      encodeURIComponent(rowsCSV) +
      "&columns=" +
      encodeURIComponent(columnsCSV) +
      "&prompt=" +
      encodeURIComponent(prompt) +
      "&idea_qualifiers=" +
      encodeURIComponent(ideaQualifiers) +
      "&num_ideas=" +
      numberOfIdeas;

    let ms = "";
    let isLoadingXhr = true;
    let output = [];
    try {
      fetchSSE(
        uri,
        { method: "GET", signal: ctrl.signal },
        {
          json: true,
          onErrorHandle: () => {
            abortLoad(ctrl);
          },
          onFinish: () => {
            setLoading(false);
          },
          onMessageHandle: (data) => {
            if (!isLoadingXhr) {
              console.log("is loading xhr", isLoadingXhr);
              return;
            }
            ms += data.data;
            ms = ms.trim().replace(/^[^{[]+/, "");
            if (ms.startsWith("{") || ms.startsWith("[")) {
              try {
                output = parse(ms || "[]");
              } catch (error) {
                console.log("error", error);
              }
              if (Array.isArray(output)) {
                setMatrix(output);
              } else {
                abortLoad(ctrl);
                message.warning(
                  "Model failed to respond rightly, please rewrite your message and try again",
                );
                console.log("response is not parseable into an array");
              }
            }
          },
        },
      );
    } catch (error) {
      console.log("error", error);
      setLoading(false);
      isLoadingXhr = false;
      abortLoad();
    }
  };

  const promptMenu = (
    <div>
      <h1>Creative Matrix</h1>

      <div className="user-input">
        <Select
          defaultValue={templates[0].name}
          onChange={onChangeTemplate}
          options={templates.map((t) => ({
            value: t.name,
            label: t.name,
          }))}
        ></Select>
      </div>

      <div className="user-input">
        <label>Prompt</label>
        <TextArea
          placeholder="Prompt for the intersection of row and column"
          value={prompt}
          onChange={onChangePrompt}
          disabled={isLoading}
        />
      </div>
      <div className="user-input">
        <label>Rows</label>
        <TextArea
          placeholder="Comma-separated list of values"
          value={rowsCSV}
          onChange={onChangeRowsCSV}
          disabled={isLoading}
        />
      </div>
      <div className="user-input">
        <label>Columns</label>

        <TextArea
          placeholder="Comma-separated list of values"
          value={columnsCSV}
          onChange={onChangeColumnsCSV}
          disabled={isLoading}
        />
      </div>
      <div className="user-input">
        Generate{" "}
        <Select
          defaultValue={"3"}
          onChange={handleSelectChange}
          disabled={isLoading}
          className="small"
          options={[
            { value: "1", label: "1 idea" },
            { value: "2", label: "2 ideas" },
            { value: "3", label: "3 ideas" },
            { value: "4", label: "4 ideas" },
            { value: "5", label: "5 ideas" },
          ]}
        ></Select>
        &nbsp; per combination.
      </div>
      <div className="user-input">
        <label>Each idea must be...</label>
        <Select
          style={{ width: "100%" }}
          mode="tags"
          placeholder="List of adjectives/qualifiers"
          onChange={onChangeIdeaQualifiers}
          disabled={isLoading}
          options={[
            { value: "utopian", label: "Utopian" },
            { value: "dystopian", label: "Dystopian" },
            {
              value: "inspired by science fiction",
              label: "Inspired by science fiction",
            },
            { value: "funny and bizarre", label: "Funny and bizarre" },
            {
              value: "written in the style of Shakespear",
              label: "Written in the style of Shakespear",
            },
          ]}
        />
      </div>
      <div className="user-input">
        <Button
          onClick={onGenerateMatrix}
          className="go-button"
          disabled={isLoading}
        >
          GENERATE MATRIX
        </Button>
      </div>
    </div>
  );

  const collapseItem = [
    {
      key: "1",
      label: isExpanded ? "Hide Prompt Panel" : "Show Prompt Panel",
      children: promptMenu,
    },
  ];

  return (
    <div id="canvas">
      <div className={`prompt-chat-container ${isExpanded ? "" : "collapsed"}`}>
        <Collapse
          className="prompt-chat-options-container"
          items={collapseItem}
          defaultActiveKey={["1"]}
          ghost={isExpanded}
          activeKey={isExpanded ? "1" : ""}
          onChange={onCollapsibleIconClick}
          expandIcon={() => <MenuFoldOutlined rotate={isExpanded ? 0 : 180} />}
        />
        <div className="chat-container-wrapper">
          <Disclaimer models={models} />
          <div className="prompt-chat-header">
            <h1 className="title-for-collapsed-panel">Creative Matrix</h1>
            {isLoading && (
              <div className="user-input">
                <Spin />
                <Button
                  type="secondary"
                  danger
                  onClick={abortLoad}
                  className="stop-button"
                >
                  STOP
                </Button>
              </div>
            )}
          </div>
          <div className="matrix-container">
            <div>
              <table className="matrix-table">
                <thead>
                  <tr>
                    <th></th>
                    {columns.map((columnValue, index) => {
                      return <th>{columnValue}</th>;
                    })}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((rowValue, rowIndex) => {
                    return (
                      <tr style={{ height: 50 }}>
                        <td
                          style={{
                            textAlign: "center",
                            width: "10%",
                          }}
                        >
                          <b>{rowValue}</b>
                        </td>
                        {columns.map((columnValue, columnIndex) => {
                          return (
                            <td
                              style={{
                                textAlign: "center",
                                border: "1px solid #e1e1e1",
                                width: 85 / columns.length + "%",
                              }}
                            >
                              <ul
                                style={{
                                  textAlign: "left",
                                  paddingLeft: 20,
                                }}
                              >
                                {getMatrixCellValues(rowIndex, columnIndex).map(
                                  (idea) => {
                                    return (
                                      <li
                                        key={"" + rowIndex + "-" + columnIndex}
                                        style={{
                                          marginBottom: 10,
                                          cursor: "auto",
                                        }}
                                      >
                                        <b>{idea.title}:</b> {idea.description}
                                      </li>
                                    );
                                  },
                                )}
                              </ul>
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreativeMatrix;
