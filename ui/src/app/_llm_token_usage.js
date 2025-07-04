// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Tooltip } from "antd";
import { GiToken } from "react-icons/gi";
import { getTokenUsage } from "./_local_store";

// Helper to format tokens as human-readable k format
function formatTokens(num) {
  if (typeof num !== "number" || isNaN(num)) return "-";
  if (num < 1500) return "1k";
  return `${Math.round(num / 1000)}k`;
}

const LLMTokenUsage = ({}) => {
  const [tokenUsage, setTokenUsage] = useState({});
  const [showTokenUsage, setShowTokenUsage] = useState(false);

  useEffect(() => {
    setTokenUsage(getTokenUsage());
  }, [tokenUsage.input_tokens, tokenUsage.output_tokens]);

  return (
    <Tooltip
      open={showTokenUsage}
      title={
        <div>
          <p>Input Tokens: {formatTokens(tokenUsage.input_tokens)}</p>
          <p>Output Tokens: {formatTokens(tokenUsage.output_tokens)}</p>
        </div>
      }
    >
      <span className="token-usage-icon">
        <GiToken
          fontSize="large"
          onMouseOver={() => setShowTokenUsage(true)}
          onMouseOut={() => setShowTokenUsage(false)}
        />
      </span>
    </Tooltip>
  );
};

export default LLMTokenUsage; 