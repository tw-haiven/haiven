import React, { useState } from "react";
import { Popover } from "antd";

const EvalResults = ({ strategies, scenarios, dimensions, results }) => {
  let key = 0;
  const [initialRendered, setInitialRendered] = useState(false);

  const findResultFor = ({ scenario, strategy }) => {
    // console.log("find results for scenario", scenario);
    // console.log("find results for strategy", strategy);
    return results.find((result) => {
      return result.scenario == scenario && result.strategy == strategy;
    });
  };

  const titleFor = (x) => {
    return x.split(":")[0].trim();
  };

  const columnWidth = `${100 / ((scenarios || []).length + 1)}%`;

  return (
    <div id="eval-results" className="eval-results-matrix">
      <table cellSpacing={0} style={{ marginRight: 10 }}>
        <tbody>
          <tr key="header-row">
            <td></td>
            {scenarios?.map((scenario, i) => {
              return (
                <td
                  key={key++}
                  className="scenario-header"
                  style={{ textAlign: "center" }}
                >
                  Scenario {i + 1}: {titleFor(scenario)}
                </td>
              );
            })}
          </tr>
          {strategies?.map((strategy, i) => {
            return (
              <tr key={key++}>
                <td className="strategy-header" style={{ width: "10%" }}>
                  Strategy {i + 1}: {titleFor(strategy)}
                </td>
                {scenarios.map((scenario) => {
                  const result = findResultFor({ strategy, scenario });
                  const scoreSum = result?.results?.dimensions?.reduce(
                    (sum, dimension) => sum + (dimension.score || 0),
                    0,
                  );
                  const denominator = result?.results?.dimensions?.filter(
                    (dim) => dim.score != undefined,
                  ).length;
                  const scoreAvg = scoreSum / denominator;
                  // console.log("result", result);
                  return (
                    <td
                      className="eval-result"
                      style={{ width: columnWidth }}
                      key={key++}
                    >
                      <div style={{ textAlign: "center", fontWeight: "bold" }}>
                        {denominator &&
                          parseFloat(scoreAvg.toFixed(1)).toString()}
                      </div>
                      {result?.results?.dimensions &&
                        result?.results?.dimensions.map((dimension, d) => {
                          const tooltip = (
                            <div style={{ width: 300 }}>
                              {dimension.rationale}
                            </div>
                          );
                          return (
                            <Popover
                              content={tooltip}
                              title={
                                dimension.name + " score: " + dimension.score
                              }
                            >
                              <div style={{ cursor: "pointer" }}>
                                {dimension.name}: {dimension.score}
                              </div>
                            </Popover>
                          );
                        })}
                      {!result?.results?.dimensions &&
                        dimensions?.map((dimension, d) => {
                          return <div>{titleFor(dimension)} score</div>;
                        })}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default EvalResults;
