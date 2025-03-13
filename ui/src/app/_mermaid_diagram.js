// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState, useCallback } from "react";
import mermaid from "mermaid";

const MermaidDiagram = ({ chart, config = {} }) => {
  const [svgContent, setSvgContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Generate a unique ID for this diagram instance
  const uniqueId = React.useMemo(
    () => `mermaid-${Math.random().toString(36).substring(2, 11)}`,
    [],
  );

  const renderDiagram = useCallback(async () => {
    if (!chart) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "neutral",
        securityLevel: "antiscript",
        ...config,
        suppressErrors: true, // Deprecated option?
        suppressErrorRendering: true, // Prevent Mermaid from inserting error messages into the DOM
      });

      await mermaid
        .render(uniqueId, chart)
        .then((result) => {
          if (result && result.svg) {
            setSvgContent(result.svg);
          }
        })
        .catch((error) => {
          setErrorMessage("Error in diagram syntax");
        });
    } catch (error) {
      console.error("Error initialising Mermaid", error);
    } finally {
      setIsLoading(false);
    }
  }, [chart, config, uniqueId]);

  // Effect to trigger diagram rendering when dependencies change
  useEffect(() => {
    renderDiagram();
  }, [renderDiagram]);

  // Effect to handle binding functions after SVG is in the DOM
  useEffect(() => {
    // Skip if no SVG content or if there's an error
    if (!svgContent || errorMessage) return;

    // Use a timeout to ensure the DOM has been updated
    const timer = setTimeout(() => {
      const element = document.getElementById(uniqueId);
      if (element && typeof mermaid.bindFunctions === "function") {
        try {
          mermaid.bindFunctions(element);
        } catch (err) {
          console.error("Error binding functions to Mermaid diagram:", err);
        }
      }
    }, 0);

    return () => clearTimeout(timer);
  }, [svgContent, uniqueId, errorMessage]);

  if (isLoading && !svgContent) {
    return (
      <div className="mermaid-diagram-container">
        <div className="mermaid-diagram loading">Rendering diagram...</div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="mermaid-diagram-container">
        <div
          className="mermaid-diagram error"
          style={{
            color: "red",
            padding: "1rem",
            border: "1px solid red",
            borderRadius: "4px",
          }}
        >
          {errorMessage}
        </div>
      </div>
    );
  }

  return (
    <div className="mermaid-diagram-container">
      {svgContent ? (
        <div
          id={uniqueId}
          className="mermaid-diagram"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      ) : (
        <div className="mermaid-diagram empty">No diagram content</div>
      )}
    </div>
  );
};

export default MermaidDiagram;
