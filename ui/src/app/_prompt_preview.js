// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import { useState, useEffect } from "react";
import { Modal, Button } from "antd";
import { RiClipboardLine, RiEdit2Line } from "react-icons/ri";
import * as Diff from "diff";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getRenderedPrompt } from "./_boba_api";
import PromptSampleInput from "./_prompt_sample_input";

export default function PromptPreview({
  renderPromptRequest,
  startNewChat = () => {},
  setUsePromptId = () => {},
  disableEdit = false,
  sampleInput = "",
}) {
  const [isPromptPreviewModalVisible, setPromptPreviewModalVisible] =
    useState(false);
  const [prompt, setPrompt] = useState("");
  const [promptData, setPromptData] = useState({});
  const [onEditMode, setOnEditMode] = useState(false);
  const [anyUnsavedChanges, setAnyUnsavedChanges] = useState(false);
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  useEffect(() => {
    setPrompt(promptData.renderedPrompt);

    if (isPromptPreviewModalVisible) {
      setAnyUnsavedChanges(false);
    }
  }, [promptData, isPromptPreviewModalVisible]);

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
      setPrompt(promptData.renderedPrompt);
    }
  };

  const onRenderPrompt = () => {
    const requestData = renderPromptRequest();
    console.log("requestData", requestData);
    getRenderedPrompt(requestData, (response) => {
      setPromptData({
        renderedPrompt: response.prompt,
        template: response.template,
      });
      setPromptPreviewModalVisible(true);
      setOnEditMode(false);
    });
  };

  const highlightDiffs = (props) => {
    const { node, ...rest } = props;
    return <span className="prompt-preview-diff-highlight" {...rest} />;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt || promptData.renderedPrompt);
  };

  const onClosePromptPreviewModal = () => {
    if (onEditMode && anyUnsavedChanges) {
      setIsCloseConfirmationModalVisible(true);
    } else {
      setPromptPreviewModalVisible(false);
    }
  };

  return (
    <div className="prompt-preview-container">
      <PromptSampleInput sampleInput={sampleInput} />

      <Button
        className="prompt-preview-btn"
        type="link"
        onClick={onRenderPrompt}
      >
        {disableEdit ? "View Prompt" : "View/Edit Prompt"}
      </Button>

      <Modal
        className="prompt-preview-modal"
        title={disableEdit ? "View Prompt" : "View/Edit Prompt"}
        open={isPromptPreviewModalVisible}
        onCancel={onClosePromptPreviewModal}
        width={800}
      >
        <div className="prompt-preview-header">
          <p>
            This is the text that will be sent to the AI model. It includes your
            input and any contexts you selected.
          </p>

          <div className="prompt-preview-actions">
            {!disableEdit && (
              <Button
                className="prompt-preview-edit-btn"
                onClick={() => setOnEditMode(true)}
                disabled={onEditMode}
              >
                <RiEdit2Line
                  style={{
                    fontSize: "large",
                  }}
                />{" "}
                EDIT
              </Button>
            )}
            <Button className="prompt-preview-copy-btn" onClick={handleCopy}>
              <RiClipboardLine
                style={{
                  fontSize: "large",
                }}
              />{" "}
              COPY
            </Button>
          </div>
        </div>
        {onEditMode ? (
          <textarea
            className="prompt-editor"
            defaultValue={prompt}
            onChange={(e) => {
              setPrompt(e.target.value);
              setAnyUnsavedChanges(true);
            }}
          ></textarea>
        ) : (
          <ReactMarkdown
            className="prompt-preview"
            remarkPlugins={[[remarkGfm]]}
            components={{
              del(props) {
                return highlightDiffs(props);
              },
            }}
          >
            {prompt}
          </ReactMarkdown>
        )}
        <div className="button-container">
          <Button
            className="prompt-preview-close-btn"
            onClick={onClosePromptPreviewModal}
          >
            CLOSE
          </Button>
          {onEditMode && !disableEdit && (
            <Button
              className="prompt-preview-start-chat-btn"
              disabled={!anyUnsavedChanges}
              onClick={() => {
                setUsePromptId(false);
                startNewChat(prompt);
                setPromptPreviewModalVisible(false);
              }}
            >
              START CHAT
            </Button>
          )}
        </div>
      </Modal>
      <Modal
        className="close-confirmation-modal"
        title="Are you sure you want to close?"
        open={isCloseConfirmationModalVisible}
        closable={false}
      >
        <p>
          You have unsaved edits in the prompt. By closing any unsaved changes
          will be lost.
        </p>

        <div className="confirmation-modal-footer">
          <Button
            className="confirmation-modal-close-btn"
            onClick={() => {
              setPromptPreviewModalVisible(false);
              setIsCloseConfirmationModalVisible(false);
            }}
          >
            CLOSE ANYWAY
          </Button>
          <Button
            className="confirmation-modal-cancel-btn"
            onClick={() => {
              setIsCloseConfirmationModalVisible(false);
            }}
          >
            GO BACK
          </Button>
        </div>
      </Modal>
    </div>
  );
}
