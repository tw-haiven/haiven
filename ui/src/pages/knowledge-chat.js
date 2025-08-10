// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import PromptChat from "../app/_prompt_chat";
import { getInspirationById } from "../app/_boba_api";

const KnowledgeChatPage = ({
  prompts,
  documents,
  models,
  featureToggleConfig,
}) => {
  const [promptId, setPromptId] = useState();
  const [initialInput, setInitialInput] = useState("");
  const searchParams = useSearchParams();

  useEffect(() => {
    setPromptId(searchParams.get("prompt"));

    const inspirationId = searchParams.get("inspiration");
    if (inspirationId) {
      getInspirationById(inspirationId, (inspiration) => {
        setInitialInput(inspiration.prompt_template);
      }).catch((error) => console.error("Error loading inspiration:", error));
    }
  }, [searchParams]);

  // Using the "key" property to make sure the component resets when the prompt id changes
  return (
    <PromptChat
      promptId={promptId}
      initialInput={initialInput}
      prompts={prompts}
      documents={documents}
      models={models}
      showTextSnippets={false}
      showImageDescription={true}
      pageTitle="Chat with Haiven"
      pageIntro="Ask anything! You can also upload a document and ask questions about its content."
      headerTooltip={false}
      inputTooltip={false}
      featureToggleConfig={featureToggleConfig}
    />
  );
};

export default KnowledgeChatPage;
