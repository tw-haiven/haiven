// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { Popover } from "antd";

const PlotItem = ({ data }) => {
  const content = (
    <div className="scenario">
      <div className="scenario-card-content">
        <div className="card-prop stackable">
          <div className="card-prop-name">Horizon</div>
          <div className="card-prop-value">{data.horizon}</div>
        </div>
        <div className="card-prop stackable">
          <div className="card-prop-name">Plausibility</div>
          <div className="card-prop-value">{data.plausibility}</div>
        </div>
        <div className="card-prop stackable">
          <div className="card-prop-name">Probability</div>
          <div className="card-prop-value">{data.probability}</div>
        </div>
        <div className="scenario-summary">{data.summary}</div>
        <div className="card-prop">
          <div className="card-prop-name">Signals/Driving Forces</div>
          <div className="card-prop-value">
            {(data.signals || []).join(", ")}
          </div>
        </div>
        <div className="card-prop">
          <div className="card-prop-name">Threats</div>
          <div className="card-prop-value">
            {(data.threats || []).join(", ")}
          </div>
        </div>
        <div className="card-prop">
          <div className="card-prop-name">Opportunities</div>
          <div className="card-prop-value">
            {(data.opportunities || []).join(", ")}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <Popover content={content} title={data.title}>
      <div className="matrix-item">
        <span className="matrix-item-title">{data.title}</span>&nbsp;
        <span className="matrix-item-horizon">[horizon: {data.horizon}]</span>
      </div>
    </Popover>
  );
};

const findDataFor = (data, { probability, plausibility }) => {
  const result = (data || []).filter((d) => {
    return (
      (d.probability || "").includes(probability) &&
      (d.plausibility || "").includes(plausibility)
    );
  });
  return result;
};

const Plot = ({ scenarios }) => {
  let key = 0;
  const [initialRendered, setInitialRendered] = useState(false);

  return (
    <div id="boba-plot" className="boba-matrix">
      <table cellSpacing={0}>
        <tbody>
          <tr key="row 1">
            <td></td>
            <td style={{ height: 40 }}>low plausibility</td>
            <td style={{ height: 40 }}>medium plausibility</td>
            <td style={{ height: 40 }}>high plausibility</td>
          </tr>
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
                plausibility: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "high",
                plausibility: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "high",
                plausibility: "high",
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
                plausibility: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "medium",
                plausibility: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "medium",
                plausibility: "high",
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
                plausibility: "low",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "low",
                plausibility: "medium",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
            <td className="content">
              {findDataFor(scenarios, {
                probability: "low",
                plausibility: "high",
              }).map((d) => {
                return <PlotItem data={d} key={key++} />;
              })}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default Plot;
