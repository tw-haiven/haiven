// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import CardActions, { scenarioToText } from "./_card_actions";
import ScenariosPlotProbabilityImpact from "../pages/_plot_prob_impact";
import { RiStackLine, RiGridLine, RiFileCopyLine } from "react-icons/ri";
import ReactMarkdown from "react-markdown";
import { Card, Button, Input, Radio, message } from "antd";
const { TextArea } = Input;

const CardsList = ({
  scenarios,
  setScenarios,
  title,
  onExplore,
  stopLoadComponent,
  matrixMode: matrix,
  editable,
  selectable,
}) => {
  const [displayMode, setDisplayMode] = useState("grid");

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n\n"));
    message.success("Content copied successfully!");
  };

  const onScenarioDescriptionChanged = (e, i) => {
    const updatedScenarios = [...scenarios];
    updatedScenarios[i].summary = e.target.value;
    setScenarios(updatedScenarios);
  };

  const onScenarioSelectionChanged = (e, i) => {
    const scenarioElement = document.querySelectorAll(".scenario")[i];
    scenarioElement.classList.toggle("excluded");
    const updatedScenarios = [...scenarios];
    updatedScenarios[i].exclude = !e.target.checked;
    setScenarios(updatedScenarios);
  };

  const camelCaseToHumanReadable = (str) => {
    return str
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase());
  };

  const renderScenarioDetails = (scenario) => {
    return Object.keys(scenario).map((key) => {
      if (
        key === "title" ||
        key === "summary" ||
        key === "hidden" ||
        key === "exclude" ||
        key === "id"
      )
        return null;
      const value = scenario[key];
      return (
        <div key={key}>
          <strong>{camelCaseToHumanReadable(key)}:</strong>
          {Array.isArray(value) ? (
            <ul>
              {value.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          ) : (
            <span> {value}</span>
          )}
        </div>
      );
    });
  };

  return (
    <>
      <div className="prompt-chat-header">
        {title && <h1 className="title-for-collapsed-panel">{title}</h1>}
        {stopLoadComponent}
        {scenarios && scenarios.length > 0 && (
          <Button type="link" className="copy-all" onClick={onCopyAll}>
            <RiFileCopyLine fontSize="large" /> COPY ALL
          </Button>
        )}
        {scenarios && scenarios.length > 0 && matrix === true && (
          <div className="scenarios-actions">
            <Radio.Group
              className="display-mode-choice"
              onChange={onSelectDisplayMode}
              defaultValue="grid"
              size="small"
            >
              <Radio.Button value="grid">
                <RiStackLine /> CARD VIEW
              </Radio.Button>
              <Radio.Button value="plot">
                <RiGridLine /> MATRIX VIEW
              </Radio.Button>
            </Radio.Group>
          </div>
        )}
      </div>
      <div className={"scenarios-collection " + displayMode + "-display"}>
        <div className="cards-container with-display-mode">
          {scenarios.map((scenario, i) => {
            return (
              <Card title={scenario.title} key={i} className="scenario">
                <div className="scenario-card-content">
                  {editable === true ? (
                    <TextArea
                      value={scenario.summary}
                      onChange={(e) => {
                        onScenarioDescriptionChanged(e, i);
                      }}
                      rows={10}
                      data-testid={`scenario-summary-${i}`}
                    />
                  ) : (
                    <ReactMarkdown
                      className="scenario-summary"
                      data-testid={`scenario-summary-${i}`}
                    >
                      {scenario.summary}
                    </ReactMarkdown>
                  )}
                  {renderScenarioDetails(scenario)}
                </div>
                <CardActions
                  scenario={scenario}
                  onExploreHandler={onExplore}
                  onScenarioSelectionHandler={
                    selectable === true
                      ? (e) => {
                          onScenarioSelectionChanged(e, i);
                        }
                      : undefined
                  }
                />
              </Card>
            );
          })}
          {matrix === true && (
            <div
              className="scenarios-plot-container"
              style={{
                display: displayMode == "plot" ? "block" : "none",
              }}
            >
              <ScenariosPlotProbabilityImpact
                scenarios={scenarios}
                visible={displayMode == "plot"}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CardsList;
