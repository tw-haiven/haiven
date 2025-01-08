// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import PromptChat from "../app/_prompt_chat";
import { aiIdeas } from "../app/_ai_ideas";
import { Space, Card } from "antd";
import Link from "next/link";

const KnowledgeChatPage = ({ prompts, documents, models }) => {
  const [promptId, setPromptId] = useState();
  const [initialPrompt, setInitialPrompt] = useState("");
  const [showIdeas, setShowIdeas] = useState(true);

  const searchParams = useSearchParams();

  useEffect(() => {
    const ideaId = searchParams.get("idea");
    setPromptId(searchParams.get("prompt"));

    if (ideaId) {
      const idea = aiIdeas.find((idea) => idea.id === ideaId);
      if (idea) {
        setInitialPrompt(idea.prompt);
        setShowIdeas(false);
      }
    }
  }, [searchParams]);

  const quickActionsComponent =
    aiIdeas && aiIdeas.length > 0 ? (
      <Space direction="horizontal" wrap>
        {aiIdeas.map((idea) => (
          <Link href={`/knowledge-chat?idea=${idea.id}`} key={idea.id}>
            <Card
              hoverable
              title={idea.title}
              className="dashboard-tile ai-idea-card"
            >
              {idea.description}
            </Card>
          </Link>
        ))}
      </Space>
    ) : null;

  return (
    <PromptChat
      promptId={promptId}
      key={promptId}
      prompts={prompts}
      documents={documents}
      models={models}
      showTextSnippets={false}
      showImageDescription={true}
      pageTitle="Chat with Haiven"
      pageIntro="Ask anything! You can also upload a document and ask questions about its content."
      headerTooltip={false}
      inputTooltip={false}
      initialPrompt={initialPrompt}
      quickActions={showIdeas ? quickActionsComponent : null}
    />
  );
};

export default KnowledgeChatPage;
