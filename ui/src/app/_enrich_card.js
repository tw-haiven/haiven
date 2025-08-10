// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import Disclaimer from "../pages/_disclaimer";
import HorizontalPossibilityPanel from "../pages/_horizontal-possibility-panel";
import { Button, Input } from "antd";
import { fetchSSE } from "../app/_fetch_sse";
import { toast } from "react-toastify";
import { parse } from "best-effort-json-parser";
import { formattedUsage } from "../app/utils/tokenUtils";
import { aggregateTokenUsage } from "../app/utils/_aggregate_token_usage";
import { filterSSEEvents } from "../app/utils/_sse_event_filter";

/** ITERATION EXPERIMENT
 * (behind feature toggle, experimental implementation)
 *
 * Switch on with:
 * window.localStorage.setItem("toggles", '{ "cards_iteration": true }')
 * */
const EnrichCard = ({
  startLoad,
  abortLoad,
  loading,
  chatSessionIdCardBuilding,
  scenarios,
  setScenarios,
  selectedPromptConfiguration,
  setEnableGenerateMoreCards,
  setIsGenerating,
  setProgress,
  scenarioToJson,
  attachContextsToRequestBody,
  setTokenUsage,
  tokenUsage,
}) => {
  const [iterationPrompt, setIterationPrompt] = useState("");
  const submitIterationPrompt = (prompt) => {
    setIterationPrompt(prompt);
  };
  const buildRequestDataIterate = (prompt) => {
    // add IDs to the scenarios
    scenarios.forEach((scenario, i) => {
      if (scenario.id === undefined) scenario.id = i + 1;
    });
    let requestBody = {
      userinput: prompt,
      scenarios: JSON.stringify(
        scenarios
          .filter((scenario) => scenario.exclude !== true)
          .map(scenarioToJson),
      ),
      chatSessionId: chatSessionIdCardBuilding,
    };
    attachContextsToRequestBody(requestBody);
    return requestBody;
  };

  const iterateScenarios = (partiallyParsed) => {
    partiallyParsed.forEach((parsedScenario) => {
      const existingScenario = scenarios.find(
        (scenario) => scenario.id === parsedScenario.id,
      );
      if (existingScenario) {
        Object.assign(existingScenario, parsedScenario);
        console.log(JSON.stringify(existingScenario));
        // Remove any empty properties (sometimes happens with partial parsing)
        Object.keys(existingScenario).forEach(
          (key) =>
            existingScenario[key] === "" ||
            (existingScenario[key] === undefined &&
              delete existingScenario[key]),
        );
      }
    });
    setScenarios([...scenarios]);
  };

  const sendIteration = (prompt) => {
    setEnableGenerateMoreCards(false);
    const uri = "/api/prompt/iterate";

    let ms = "";
    let output = [];

    setIsGenerating(true);
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev; // avoid hitting 100 before done
        return prev + 10;
      });
    }, 500);

    fetchSSE(
      uri,
      {
        method: "POST",
        signal: startLoad(),
        body: JSON.stringify(buildRequestDataIterate(prompt)),
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad();
          clearInterval(interval);
          setProgress(100);
          setTimeout(() => {
            setIsGenerating(false);
            setProgress(0); // reset if you want
          }, 1000);
        },
        onFinish: () => {
          if (ms == "") {
            toast.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
          }
          abortLoad();
          clearInterval(interval);
          setProgress(100);
          setTimeout(() => {
            setIsGenerating(false);
            setProgress(0); // reset if you want
          }, 1000);
        },
        onMessageHandle: (data) => {
          // Handle token usage events (new format)
          if (data.type === "token_usage") {
            const usage = formattedUsage(data.data);
            setTokenUsage((prev) => aggregateTokenUsage(prev, usage));
            return;
          }

          // Use the SSE event filter utility to extract token usage events (old format)
          if (typeof data === "string") {
            const { text, events } = filterSSEEvents(data);
            events.forEach((event) => {
              if (event.type === "token_usage" && setTokenUsage) {
                const usage = formattedUsage(event.data);
                setTokenUsage((prev) => aggregateTokenUsage(prev, usage));
              }
            });
            ms += text;
          } else if (data.data) {
            ms += data.data;
            ms = ms.trim().replace(/^[^[]+/, "");
            if (ms.startsWith("[")) {
              try {
                output = parse(ms || "[]");
              } catch (error) {
                console.log("error", error);
              }
              if (Array.isArray(output)) {
                iterateScenarios(output);
              } else {
                abortLoad();
                if (ms.includes("Error code:")) {
                  toast.error(ms);
                } else {
                  toast.warning(
                    "Model failed to respond rightly, please rewrite your message and try again",
                  );
                }
              }
            }
          }
        },
      },
    );
  };

  return (
    <>
      {scenarios.length > 0 && (
        <div style={{ width: "88%", paddingLeft: "2em" }}>
          <h3>What else do you want to add to the cards?</h3>
          <Disclaimer message="Clicking 'Enrich Cards' will disable the 'Generate More Cards' button." />
          <HorizontalPossibilityPanel
            disable={loading}
            scenarioQueries={selectedPromptConfiguration.scenario_queries || []}
            onClick={submitIterationPrompt}
          />

          <div style={{ display: "flex", gap: "8px" }}>
            <Input
              value={iterationPrompt}
              onChange={(e, v) => {
                setIterationPrompt(e.target.value);
              }}
            />
            <Button
              style={{ marginBottom: "1px" }}
              disabled={loading}
              onClick={() => {
                setEnableGenerateMoreCards(false);
                sendIteration(iterationPrompt);
              }}
              className="go-button"
            >
              ENRICH CARDS
            </Button>
          </div>
        </div>
      )}
    </>
  );
};

export default EnrichCard;
