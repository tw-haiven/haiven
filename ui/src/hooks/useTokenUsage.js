// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useEffect } from "react";
import { getTokenUsage } from "../app/_local_store";

/**
 * Custom hook for managing token usage state
 * @returns {Object} Token usage data from localStorage
 */
export function useTokenUsage() {
  const [tokenUsage, setTokenUsage] = useState({});

  useEffect(() => {
    // Load initial token usage from localStorage
    setTokenUsage(getTokenUsage());
    
    // Optional: Listen for storage changes if needed across tabs
    const handleStorageChange = (e) => {
      if (e.key === 'tokenUsage') {
        setTokenUsage(getTokenUsage());
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Return both the data and a helper to check if we have token usage
  return {
    tokenUsage,
    hasTokenUsage: tokenUsage.input_tokens > 0 || tokenUsage.output_tokens > 0,
  };
} 