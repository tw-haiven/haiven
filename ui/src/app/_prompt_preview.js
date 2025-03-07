// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import { useState, useEffect } from "react";
import { Modal, Button } from "antd";
import { RiClipboardLine, RiEdit2Line } from "react-icons/ri";
import * as Diff from "diff";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "react-toastify";
import { getRenderedPrompt } from "./_boba_api";
import PromptSampleInput from "./_prompt_sample_input";
import ConfirmClose from "./_confirm_close";

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
    toast.success("Content copied successfully!");
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
        className="view-or-edit-details-modal"
        title={disableEdit ? "View Prompt" : "View/Edit Prompt"}
        open={isPromptPreviewModalVisible}
        onCancel={onClosePromptPreviewModal}
      >
        <div className="metadata-header">
          <p>
            This is the text that will be sent to the AI model. It includes your
            input and any contexts you selected.
          </p>

          <div className="actions">
            {!disableEdit && (
              <Button
                className="edit-action-link"
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
            <Button className="copy-action-link" onClick={handleCopy}>
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
            className="content-editor"
            defaultValue={prompt}
            onChange={(e) => {
              setPrompt(e.target.value);
              setAnyUnsavedChanges(true);
            }}
          ></textarea>
        ) : (
          <ReactMarkdown
            className="content-viewer"
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
        <div className="modal-footer">
          <Button
            className="close-modal-link"
            onClick={onClosePromptPreviewModal}
          >
            CLOSE
          </Button>
          {onEditMode && !disableEdit && (
            <Button
              className="proceed-to-action-link"
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
      <ConfirmClose
        isVisible={isCloseConfirmationModalVisible}
        onForceClose={() => {
          setPromptPreviewModalVisible(false);
          setIsCloseConfirmationModalVisible(false);
        }}
        onReturnBack={() => {
          setIsCloseConfirmationModalVisible(false);
        }}
      />
    </div>
  );
}
