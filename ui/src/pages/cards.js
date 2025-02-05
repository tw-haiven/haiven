// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import CardsChat from "./_cards-chat";

const CardsPage = ({ prompts, contexts, models, featureToggleConfig }) => {
  const [promptId, setPromptId] = useState();

  const searchParams = useSearchParams();

  useEffect(() => {
    setPromptId(searchParams.get("prompt"));
  }, [searchParams]);

  // Using the "key" property to make sure the component resets when the prompt id changes
  return (
    <CardsChat
      promptId={promptId}
      key={promptId}
      contexts={contexts}
      models={models}
      prompts={prompts}
      featureToggleConfig={featureToggleConfig}
    />
  );
};

export default CardsPage;
