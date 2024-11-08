// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import Disclaimer from "../pages/_disclaimer";
import CardActions, { scenarioToText } from "./_card_actions";
import ScenariosPlotProbabilityImpact from "../pages/_plot_prob_impact";
import { RiStackLine, RiGridLine, RiFileCopyLine } from "react-icons/ri";

import { Card, Button, Radio, message } from "antd";
const CardsList = ({
  scenarios,
  models,
  title,
  matrixMode: matrix,
  onExplore,
  stopLoadComponent,
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

  return (
    <div className="chat-container-wrapper">
      <Disclaimer models={models} />
      <div className="prompt-chat-header">
        <h1 className="title-for-collapsed-panel">{title}</h1>
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
                  {scenario.category && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Category</div>
                      <div className="card-prop-value">{scenario.category}</div>
                    </div>
                  )}
                  <div className="card-prop-name">Description</div>
                  <div className="scenario-summary">{scenario.summary}</div>
                  {scenario.probability && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Probability</div>
                      <div className="card-prop-value">
                        {scenario.probability}
                      </div>
                    </div>
                  )}
                  {scenario.impact && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Potential impact</div>
                      <div className="card-prop-value">{scenario.impact}</div>
                    </div>
                  )}
                </div>
                <CardActions scenario={scenario} onExploreHandler={onExplore} />
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
    </div>
  );
};

export default CardsList;
