// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import CardActions from "./_card_actions";
import ScenariosPlotProbabilityImpact from "../pages/_plot_prob_impact";
import {
  RiStackLine,
  RiGridLine,
  RiFileCopyLine,
  RiCloseFill,
} from "react-icons/ri";
import { Card, Button, Input, Radio, Tooltip, Progress } from "antd";
import { toast } from "react-toastify";
import { DynamicDataRenderer, scenarioToText } from "./_dynamic_data_renderer";
import MarkdownRenderer from "./_markdown_renderer";
const { TextArea } = Input;

const CardsList = ({
  progress,
  isGenerating,
  scenarios,
  setScenarios,
  onExplore,
  stopLoadComponent,
  matrixMode: matrix,
  editable,
  onDelete,
  listIndex,
  featureToggleConfig,
}) => {
  const [displayMode, setDisplayMode] = useState("grid");

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n\n"));
    toast.success("Content copied successfully!");
  };

  const onScenarioDescriptionChanged = (e, i) => {
    const updatedScenarios = [...scenarios];
    updatedScenarios[i].summary = e.target.value;
    setScenarios(updatedScenarios);
  };

  const renderScenarioDetails = (scenario) => {
    return (
      <DynamicDataRenderer
        data={scenario}
        exclude={["summary"]}
        className="scenario-summary"
      />
    );
  };

  return (
    <>
      <div className="prompt-chat-header">
        {stopLoadComponent && stopLoadComponent}
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
          {scenarios.map((scenario, scenarioIndex) => {
            if (scenario.scenarios) {
              return (
                <div className="scenario-section" key={scenarioIndex}>
                  <div className="scenario-section-header">
                    <h3>{scenario.title}</h3>
                    <Tooltip
                      title="Remove"
                      key="chat"
                      style={{ float: "right", display: "inline" }}
                    >
                      <Button
                        type="link"
                        onClick={() => onDelete({ section: scenarioIndex })}
                        className="delete-button"
                        name="Remove section"
                      >
                        <RiCloseFill fontSize="large" />
                      </Button>
                    </Tooltip>
                  </div>
                  <CardsList
                    scenarios={scenario.scenarios}
                    onExplore={onExplore}
                    onDelete={onDelete}
                    listIndex={scenarioIndex}
                  />
                </div>
              );
            } else {
              return (
                <Card
                  title={scenario.title}
                  key={
                    listIndex >= 0
                      ? listIndex + "-" + scenarioIndex
                      : scenarioIndex
                  }
                  className="scenario"
                  extra={
                    onDelete && (
                      <Tooltip title="Remove" key="chat">
                        <Button
                          type="link"
                          onClick={() =>
                            onDelete({
                              card: scenarioIndex,
                              section: listIndex,
                            })
                          }
                          className="delete-button"
                          name="Remove"
                        >
                          <RiCloseFill fontSize="large" />
                        </Button>
                      </Tooltip>
                    )
                  }
                >
                  <div className="scenario-card-content">
                    {editable === true ? (
                      <TextArea
                        value={scenario.summary}
                        onChange={(e) => {
                          onScenarioDescriptionChanged(e, scenarioIndex);
                        }}
                        autoSize={{ minRows: 3, maxRows: 8 }}
                        data-testid={`scenario-summary-${scenarioIndex}`}
                      />
                    ) : (
                      <MarkdownRenderer
                        content={scenario.summary}
                        className="scenario-summary"
                        datatestid={`scenario-summary-${scenarioIndex}`}
                      />
                    )}
                    {renderScenarioDetails(scenario)}
                  </div>
                  <CardActions
                    progress={progress}
                    isGenerating={isGenerating}
                    featureToggleConfig={featureToggleConfig}
                    scenario={scenario}
                    onExploreHandler={onExplore}
                    selfReview={
                      scenario["self-review"] ? scenario["self-review"] : null
                    }
                  />
                </Card>
              );
            }
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
