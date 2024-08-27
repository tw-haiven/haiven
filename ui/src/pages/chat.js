// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import PromptChat from "../app/_prompt_chat";
import { getPrompts, getContextSnippets, getDocuments } from "../app/_boba_api";

const ChatPage = () => {
  const [promptId, setPromptId] = useState();

  const [prompts, setPrompts] = useState([]);
  const [contexts, setContexts] = useState([]);
  const [documents, setDocuments] = useState([]);

  const searchParams = useSearchParams();

  useEffect(() => {
    setPromptId(searchParams.get("prompt"));
  }, [searchParams]);

  useEffect(() => {
    getPrompts(setPrompts);
    getContextSnippets((data) => {
      const labelValuePairs = data.map((context) => {
        if (context.context === "base") {
          return {
            label: "none",
            value: "base",
          };
        } else {
          return {
            label: context.context,
            value: context.context,
          };
        }
      });
      setContexts(labelValuePairs);
    });
    getDocuments(setDocuments);
  }, []);

  // Using the "key" property to make sure the component resets when the prompt id changes
  return (
    <PromptChat
      promptId={promptId}
      key={promptId}
      prompts={prompts}
      contexts={contexts}
      documents={documents}
    />
  );
};

export default ChatPage;
