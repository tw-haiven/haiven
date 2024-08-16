// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { Alert, Input, Button, Spin, Select, Space, Popover } from "antd";
import { parse } from "best-effort-json-parser";
import {
  AiOutlineBorderInner,
  AiOutlinePicture,
  AiOutlineRocket,
} from "react-icons/ai";
import { fetchSSE } from "../app/_fetch_sse";
let ctrl;

const CreativeMatrix = () => {
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
  const [isLoading, setLoading] = useState(false);
  const [matrix, setMatrix] = useState([]);
  const [currentSSE, setCurrentSSE] = useState(null);
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
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
    setModelOutputFailed(false);
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

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
            try {
              output = parse(ms || "[]");
            } catch (error) {
              setModelOutputFailed(true);
              console.log("error", error);
            }
            setMatrix(output);
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

  return (
    <div id="canvas">
      <h1 style={{ marginTop: 0 }}>
        Creative Matrix &nbsp;&nbsp;
        <Select
          defaultValue={templates[0].name}
          style={{ width: 350 }}
          onChange={onChangeTemplate}
          options={templates.map((t) => ({ value: t.name, label: t.name }))}
        ></Select>
      </h1>

      <div style={{ marginTop: 20 }}>
        {/* DIMENSIONS */}
        <div id="dim-config">
          <div style={{ display: "inline-block", width: 100 }}>Prompt:</div>
          <Input
            placeholder="Prompt for the intersection of row and column"
            value={prompt}
            style={{ width: "95%" }}
            onChange={onChangePrompt}
            disabled={isLoading}
          />
          <br />
          <div style={{ display: "inline-block", width: 100, marginTop: 10 }}>
            Rows:
          </div>
          <Input
            placeholder="Comma-separated list of values"
            value={rowsCSV}
            style={{ width: "95%" }}
            onChange={onChangeRowsCSV}
            disabled={isLoading}
          />
          <br />
          <div style={{ display: "inline-block", width: 100, marginTop: 10 }}>
            Columns:
          </div>
          <Input
            placeholder="Comma-separated list of values"
            value={columnsCSV}
            style={{ width: "95%", marginBottom: 5 }}
            onChange={onChangeColumnsCSV}
            disabled={isLoading}
          />
          <br />
          Generate{" "}
          <Select
            defaultValue={"3"}
            onChange={handleSelectChange}
            style={{ width: 100 }}
            disabled={isLoading}
            options={[
              { value: "1", label: "1 idea" },
              { value: "2", label: "2 ideas" },
              { value: "3", label: "3 ideas" },
              { value: "4", label: "4 ideas" },
              { value: "5", label: "5 ideas" },
            ]}
          ></Select>
          &nbsp; per combination &nbsp; | &nbsp; Each idea must be &nbsp;
          {/* <Input placeholder="Comma-separated list of adjectives" value={ideaQualifiers} style={{width: 300 }} onChange={onChangeIdeaQualifiers} disabled={isLoading}/>&nbsp;&nbsp; */}
          <Select
            mode="tags"
            style={{
              width: 400,
            }}
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
          &nbsp;&nbsp;
          {!isLoading && (
            <Button
              type="primary"
              style={{ marginTop: 10 }}
              onClick={onGenerateMatrix}
            >
              Generate Matrix
            </Button>
          )}
          {isLoading && (
            <Button
              type="primary"
              style={{ marginTop: 10 }}
              danger
              onClick={abortLoad}
            >
              Stop
            </Button>
          )}
          &nbsp;
          {isLoading ? <Spin /> : <></>}
        </div>
        {modelOutputFailed && (
          <Space
            direction="vertical"
            style={{ width: "100%", marginTop: "5px" }}
          >
            <Alert
              message="Model failed to respond rightly"
              description="Please rewrite your message and try again"
              type="warning"
            />
          </Space>
        )}
        <br />
        <br />
        {/* MATRIX */}
        <div>
          <table style={{ width: "95%", borderCollapse: "collapse" }}>
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
                        background: "#fefefe",
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
                          <ul style={{ textAlign: "left", paddingLeft: 20 }}>
                            {getMatrixCellValues(rowIndex, columnIndex).map(
                              (idea) => {
                                return (
                                  <li
                                    key={"" + rowIndex + "-" + columnIndex}
                                    style={{ marginBottom: 10, cursor: "auto" }}
                                  >
                                    <Popover
                                      trigger={null}
                                      content={
                                        <>
                                          <a
                                            href={
                                              "/concepts?strategic_prompt=" +
                                              encodeURIComponent(
                                                prompt +
                                                  ": " +
                                                  idea.title +
                                                  ": " +
                                                  idea.description,
                                              )
                                            }
                                            target="_blank"
                                            style={{
                                              display: "block",
                                              marginBottom: 10,
                                            }}
                                          >
                                            <AiOutlineRocket /> Generate
                                            concepts for this idea
                                          </a>
                                          <a
                                            href={
                                              "/strategies?strategic_prompt=" +
                                              encodeURIComponent(
                                                prompt +
                                                  ": " +
                                                  idea.title +
                                                  ": " +
                                                  idea.description,
                                              )
                                            }
                                            target="_blank"
                                            style={{
                                              display: "block",
                                              marginBottom: 10,
                                            }}
                                          >
                                            <AiOutlineBorderInner /> Generate
                                            strategies for this idea
                                          </a>
                                          <a
                                            href={
                                              "/storyboard?prompt=" +
                                              encodeURIComponent(
                                                prompt +
                                                  ": " +
                                                  idea.title +
                                                  ": " +
                                                  idea.description,
                                              )
                                            }
                                            target="_blank"
                                          >
                                            <AiOutlinePicture /> Generate
                                            storyboard for this idea
                                          </a>
                                        </>
                                      }
                                    >
                                      <b>{idea.title}:</b> {idea.description}
                                    </Popover>
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
  );
};

export default CreativeMatrix;
