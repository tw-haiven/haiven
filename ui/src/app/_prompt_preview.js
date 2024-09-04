// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Modal, Button } from "antd";
import { RiClipboardLine } from "react-icons/ri";
import * as Diff from "diff";
import { getRenderedPrompt } from "./_boba_api";

/*
 * buildRenderPromptRequest: function that returns an object with
      - userinput
      - promptid
      - document
*/
export default function PromptPreview({ buildRenderPromptRequest }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [promptWithDiffHighlights, setPromptWithDiffHighlights] = useState("");
  const [promptData, setPromptData] = useState({});

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const logDiff = (diff) => {
    let text = part.added
      ? "XX"
      : part.removed
        ? "'" + part.value + "'"
        : "'" + part.value + "'";
    if (text !== "") {
      console.log(text);
    }
  };

  const formatPromptForPreview = (promptData) => {
    if (promptData && promptData.renderedPrompt) {
      const diff = Diff.diffWordsWithSpace(
        promptData.renderedPrompt,
        promptData.template,
      );
      // logDiff(diff);

      const snippets = [];

      const marker = "~"; // using strikethrough marker to mark the diff, based on assumption that it won't show up in prompt markdown

      diff.forEach((part) => {
        if (part.value && part.value !== "") {
          if (part.added) {
            // a diff in the template, do nothing
          } else if (part.removed) {
            // a diff in the rendered prompt, highlight
            let boldedLines =
              marker +
              part.value.replace(/\n/g, marker + "\n" + marker) +
              marker;
            boldedLines = boldedLines.replace(
              new RegExp(" " + marker, "g"),
              marker,
            );
            boldedLines = boldedLines.replace(
              new RegExp(marker + marker, "g"),
              "",
            );
            snippets.push(boldedLines);
          } else {
            // Text that's the same in both
            snippets.push(part.value);
          }
        }
      });
      let processedPrompt = snippets.join("");
      processedPrompt = processedPrompt.replace(
        new RegExp(marker + marker, "g"),
        "",
      );
      processedPrompt = processedPrompt.replace(
        new RegExp(marker + "\n" + marker, "g"),
        "",
      );
      // setPromptWithDiffHighlights(processedPrompt);

      // Switch off the highlighted diff for now, it's too error-prone
      setPromptWithDiffHighlights(promptData.renderedPrompt);
    }
  };

  const onRenderPrompt = () => {
    const requestData = buildRenderPromptRequest();
    getRenderedPrompt(requestData, (response) => {
      setPromptData({
        renderedPrompt: response.prompt,
        template: response.template,
      });
      setIsModalOpen(true);
    });
  };

  const highlightDiffs = (props) => {
    const { node, ...rest } = props;
    return <span className="prompt-preview-diff-highlight" {...rest} />;
  };

  useEffect(() => {
    formatPromptForPreview(promptData);
  }, [promptData]);

  const handleCopy = () => {
    navigator.clipboard.writeText(promptData.renderedPrompt);
  };

  return (
    <>
      <Button
        className="prompt-preview-btn"
        type="link"
        onClick={onRenderPrompt}
      >
        Preview prompt
      </Button>

      <Modal
        title="Prompt preview"
        open={isModalOpen}
        onOk={closeModal}
        onCancel={closeModal}
        width={800}
        okButtonProps={{
          style: { display: "none" },
        }}
        cancelButtonProps={{
          style: { display: "none" },
        }}
      >
        <p>
          This is the text that will be sent to the AI model. It includes your
          input and any contexts you selected.{" "}
          {/* <span className="prompt-preview-diff-highlight">
            Your input, and any contexts you selected, are highlighted
          </span> */}
          .
        </p>

        <Button className="prompt-preview-copy-btn" onClick={handleCopy}>
          <RiClipboardLine
            style={{
              fontSize: "large",
            }}
          />{" "}
          COPY
        </Button>

        <ReactMarkdown
          className="prompt-preview"
          remarkPlugins={[[remarkGfm]]}
          components={{
            del(props) {
              return highlightDiffs(props);
            },
          }}
        >
          {promptWithDiffHighlights}
        </ReactMarkdown>
      </Modal>
    </>
  );
}
