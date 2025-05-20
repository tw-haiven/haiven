// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import PromptChat from "../app/_prompt_chat";

const ChatPage = ({
  prompts,
  contexts,
  documents,
  models,
  featureToggleConfig,
}) => {
  const [promptId, setPromptId] = useState();

  const searchParams = useSearchParams();

  useEffect(() => {
    setPromptId(searchParams.get("prompt"));
  }, [searchParams]);

  // Using the "key" property to make sure the component resets when the prompt id changes
  return (
    <PromptChat
      promptId={promptId}
      key={promptId}
      prompts={prompts}
      contexts={contexts}
      documents={documents}
      models={models}
      featureToggleConfig={featureToggleConfig}
    />
  );
};

export default ChatPage;
