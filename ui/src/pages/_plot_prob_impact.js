// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { Popover } from "antd";

const PlotItem = ({ data }) => {
  const content = (
    <div className="scenario">
      <div className="scenario-card-content">
        <div className="card-prop stackable">
          <div className="card-prop-name">Probability</div>
          <div className="card-prop-value">{data.probability}</div>
        </div>
        <div className="card-prop stackable">
          <div className="card-prop-name">Impact</div>
          <div className="card-prop-value">{data.impact}</div>
        </div>
        <div className="scenario-summary">{data.summary}</div>
      </div>
    </div>
  );

  return (
    <Popover content={content} title={data.title}>
      <div className="matrix-item">
        <span className="matrix-item-title">{data.title}</span>&nbsp;
      </div>
    </Popover>
  );
};

const findDataFor = (data, { probability, impact }) => {
  const result = (data || []).filter((d) => {
    return (
      (d.probability?.toLowerCase() || "").includes(
        probability.toLowerCase(),
      ) && (d.impact?.toLowerCase() || "").includes(impact.toLowerCase())
    );
  });
  return result;
};

const PlotProbabilityImpact = ({ scenarios }) => {
  let key = 0;
  const [initialRendered, setInitialRendered] = useState(false);

  return (
    <div id="boba-plot" className="boba-matrix">
      <h2>Probability / Impact matrix</h2>
      <table cellSpacing={0}>
        <tbody>
          <tr key="row 2">
            <td
              style={{
                writingMode: "vertical-rl",
                textOrientation: "mixed",
                width: 40,
              }}
            >
              high probability
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "high",
                impact: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "high",
                impact: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "high",
                impact: "high",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
          </tr>
          <tr key="row 3">
            <td
              style={{
                writingMode: "vertical-rl",
                textOrientation: "mixed",
                width: 40,
              }}
            >
              medium probability
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "medium",
                impact: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "medium",
                impact: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "medium",
                impact: "high",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
          </tr>
          <tr key="row 4">
            <td
              style={{
                writingMode: "vertical-rl",
                textOrientation: "mixed",
                width: 40,
              }}
            >
              low probability
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "low",
                impact: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "low",
                impact: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "low",
                impact: "high",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
          </tr>
          <tr key="row 1">
            <td></td>
            <td style={{ height: 40 }}>low impact</td>
            <td style={{ height: 40 }}>medium impact</td>
            <td style={{ height: 40 }}>high impact</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default PlotProbabilityImpact;
