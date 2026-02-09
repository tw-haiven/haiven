// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Collapse } from "antd";
import MarkdownRenderer from "../app/_markdown_renderer";
import DownloadPrompt from "../app/_download_prompt";
import DownloadPromptCategory from "../app/_download_prompt_category";
import DownloadRules from "../app/_download_rules";
import PromptOverviewPreview from "../app/_prompt_overview_preview";
import { buildPromptCategories } from "../app/utils/promptGroupingUtils";

const KnowledgePackPage = ({
  contexts,
  documents,
  prompts,
  rules,
  featureToggleConfig,
}) => {
  const [renderedSnippets, setRenderedSnippets] = useState();
  const [renderedDocuments, setRenderedDocuments] = useState();
  const [renderedPrompts, setRenderedPrompts] = useState();

  const buildTextSnippetsOverview = () => {
    const renderContexts = [];

    contexts.forEach((context) => {
      if (context.snippets && Object.keys(context.snippets).length > 0) {
        const snippetsInContext = Object.keys(context.snippets).map(
          (key, snippetIndex) => {
            return (
              <div key={context.context + "-" + snippetIndex}>
                <h4 className="snippet-title">{key}</h4>
                <div className="snippet" size="small">
                  <MarkdownRenderer content={context.snippets[key]} />
                </div>
              </div>
            );
          },
        );
        renderContexts.push({
          key: context.context,
          label: "Domain context: " + context.context,
          children: snippetsInContext,
        });
      }
    });

    setRenderedSnippets(renderContexts);
  };

  const buildDocumentsOverview = () => {
    const renderContexts = [];

    documents.forEach((document) => {
      if (document.key) {
        const doc = (
          <div key={document.key + "-section"}>
            <div className="snippet" size="small">
              <ReactMarkdown>{document.source}</ReactMarkdown>
              {document.description}
            </div>
          </div>
        );

        renderContexts.push({
          key: document.key + "-description",
          label: "Document: " + document.title,
          children: [doc],
        });
      }
    });

    setRenderedDocuments(renderContexts);
  };

  const buildPromptsOverview = () => {
    const categoryItems = buildPromptCategories(prompts, featureToggleConfig);

    const promptItems = categoryItems.map((category) => {
      const categoryLabel = (
        <div className="knowledge-overview-header">
          <span>{category.label}</span>
          <DownloadPromptCategory
            category={category.key}
            label={category.label}
          />
        </div>
      );

      const promptEntries = category.prompts.map((prompt) => (
        <div
          className="snippet"
          key={`${category.key}-${prompt.identifier}`}
        >
          <div className="knowledge-overview-header">
            <h4 className="snippet-title">{prompt.title}</h4>
            <div className="advanced-prompting">
              <PromptOverviewPreview prompt={prompt} />
              <DownloadPrompt prompt={prompt} />
            </div>
          </div>
          {prompt.help_prompt_description && (
            <ReactMarkdown>{prompt.help_prompt_description}</ReactMarkdown>
          )}
        </div>
      ));

      return {
        key: category.key,
        label: categoryLabel,
        children: promptEntries,
      };
    });

    setRenderedPrompts(promptItems);
  };

  useEffect(() => {
    buildTextSnippetsOverview();
    buildDocumentsOverview();
    buildPromptsOverview();
  }, [contexts, documents, prompts, featureToggleConfig]);

  return (
    <div id="canvas">
      <div className={"knowledge-overview"}>
        <div className="knowledge-overview-header">
          <h1>Your knowledge</h1>
          <div className="download-buttons">
            <DownloadRules rules={rules} />
          </div>
        </div>
        <p>
          This page shows an overview of the knowledge you currently have in
          your knowledge pack.
        </p>
        <div className="knowledge-columns-container">
          <div className="knowledge-list">
            <h2>Contexts</h2>
            <p>
              You can pull these descriptions into your prompts when you chose a
              context. This way, you don't have to repeat to the AI over and
              over again what the domain or technical context is. Which of the
              descriptions get pulled in depends on the definition of the
              prompt.
            </p>
            <Collapse accordion items={renderedSnippets}></Collapse>
          </div>
          <div className="knowledge-list">
            <h2>Documents</h2>
            <p>
              You can include these documents as context while you are chatting,
              and you can also ask them questions directly in the "Chat with
              documents" section.
            </p>
            <Collapse accordion items={renderedDocuments}></Collapse>
          </div>
          <div className="knowledge-list">
            <h2>Prompts</h2>
            <p>
              Browse the prompts available in your knowledge pack. Each
              category includes preview and download actions for individual
              prompts, plus a download option for the whole category.
            </p>
            <Collapse accordion items={renderedPrompts}></Collapse>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgePackPage;
