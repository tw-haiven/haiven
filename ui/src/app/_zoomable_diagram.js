// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useRef, useState } from "react";
import { select } from "d3-selection";
import { zoom, zoomIdentity } from "d3-zoom";
import { RiAddLargeLine, RiSubtractLine, RiRefreshLine } from "react-icons/ri";

const ZoomableDiagram = ({ svgContent }) => {
  const svgContainerRef = useRef(null);
  const zoomBehaviorRef = useRef(null);
  const [diagramContent, setDiagramContent] = useState(svgContent);

  // Update state when svgContent changes
  useEffect(() => {
    if (svgContent) {
      setDiagramContent(svgContent);
    }
  }, [svgContent]);

  // Initialize zoom functionality
  useEffect(() => {
    if (!diagramContent || !svgContainerRef.current) return;

    // Apply zoom behavior after a short delay to ensure SVG is rendered
    const timer = setTimeout(() => {
      try {
        const container = svgContainerRef.current;
        if (!container) return;

        const svg = select(container.querySelector("svg"));
        if (!svg.node()) {
          console.error("No SVG element found");
          return;
        }

        // Make SVG responsive
        svg
          .attr("width", "100%")
          .attr("height", "100%")
          .style("max-height", "100%")
          .style("display", "block");

        // Ensure viewBox is set for proper scaling
        if (!svg.attr("viewBox")) {
          const svgNode = svg.node();
          const bbox = svgNode.getBBox
            ? svgNode.getBBox()
            : { width: 800, height: 800 };
          svg.attr("viewBox", `0 0 ${bbox.width} ${bbox.height}`);
        }

        const g = svg.select("g");
        if (!g.node()) {
          console.error("No group element found in SVG");
          return;
        }

        const zoomBehavior = zoom()
          .scaleExtent([0.1, 10])
          .on("zoom", (event) => {
            g.attr("transform", event.transform);
          });

        svg.call(zoomBehavior);
        zoomBehaviorRef.current = { svg, zoomBehavior };
      } catch (error) {
        console.error("Error setting up zoom behavior:", error);
      }
    }, 200);

    return () => {
      clearTimeout(timer);
      zoomBehaviorRef.current = null;
    };
  }, [diagramContent]);

  const handleZoomIn = () => {
    if (!zoomBehaviorRef.current) return;
    const { svg, zoomBehavior } = zoomBehaviorRef.current;
    svg.transition().duration(300).call(zoomBehavior.scaleBy, 1.5);
  };

  const handleZoomOut = () => {
    if (!zoomBehaviorRef.current) return;
    const { svg, zoomBehavior } = zoomBehaviorRef.current;
    svg.transition().duration(300).call(zoomBehavior.scaleBy, 0.75);
  };

  const handleReset = () => {
    if (!zoomBehaviorRef.current) return;
    const { svg, zoomBehavior } = zoomBehaviorRef.current;
    svg.transition().duration(300).call(zoomBehavior.transform, zoomIdentity);
  };

  return (
    <div className="zoomable-diagram">
      <div
        ref={svgContainerRef}
        dangerouslySetInnerHTML={{ __html: diagramContent }}
        className="zoomable-diagram-svg-container"
      />

      <div className="zoom-controls">
        <button onClick={handleZoomIn} title="Zoom In">
          <RiAddLargeLine />
        </button>
        <button onClick={handleZoomOut} title="Zoom Out">
          <RiSubtractLine />
        </button>
        <button onClick={handleReset} title="Reset View">
          <RiRefreshLine />
        </button>
      </div>
    </div>
  );
};

export default ZoomableDiagram;
