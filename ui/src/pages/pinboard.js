// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Modal, Card, Button, Tooltip, Tabs } from "antd";
import {
  RiDeleteBinLine,
  RiCheckboxMultipleBlankFill,
  RiAddBoxLine,
  RiPushpinLine,
} from "react-icons/ri";
import { ClockIcon } from "lucide-react";
import { toast } from "react-toastify";
import {
  getPinboardData,
  getSortedContexts,
  deleteContextByTimestamp,
} from "../app/_local_store";
import MarkdownRenderer from "../app/_markdown_renderer";
import AddNewNote from "../app/_add_new_note";
import AddContext from "../app/_add_context";
import { isFeatureEnabled, FEATURES } from "../app/feature_toggle";
import { render } from "@testing-library/react";

const Pinboard = ({ isModalVisible, onClose }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [pinnedMessages, setPinnedMessages] = useState([]);
  const [savedUserContexts, setSavedUserContexts] = useState([]);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [isAddingContext, setIsAddingContext] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    if (typeof window !== "undefined") {
      setPinnedMessages(getPinboardData());
      setSavedUserContexts(getSortedContexts());
    }
  }, [
    typeof window !== "undefined"
      ? window.localStorage.getItem("pinboard")
      : null,
    typeof window !== "undefined"
      ? window.localStorage.getItem("context")
      : null,
  ]);

  if (!isMounted) return null;

  const scenarioToText = (scenario) => {
    return scenario.summary;
  };

  const onDelete = (index) => {
    const updatedPinnedMessages = [...pinnedMessages];
    const removedScenario = updatedPinnedMessages.splice(index, 1)[0];
    const pinboardData = JSON.parse(localStorage.getItem("pinboard"));
    delete pinboardData[removedScenario.timestamp];
    localStorage.setItem("pinboard", JSON.stringify(pinboardData));
    reloadPinnedMessages();
    toast.success("Content deleted successfully!");
  };

  const onCopyOne = async (index) => {
    try {
      await navigator.clipboard.writeText(
        scenarioToText(pinnedMessages[index]),
      );
      toast.success("Content copied successfully!");
    } catch (err) {
      toast.error("Failed to copy the content.");
    }
  };

  const addNoteButtonWithTooltip = () => {
    const tooltipText = "Add your own reusable text notes to the pinboard";
    return (
      <Tooltip title={tooltipText}>
        <Button
          type="link"
          className="copy-all"
          onClick={() => setIsAddingNote(true)}
        >
          <RiAddBoxLine fontSize="large" /> ADD NOTE
        </Button>
      </Tooltip>
    );
  };

  const addContextButtonWithTooltip = () => {
    const tooltipText =
      "Add your project context to be reused in your Haiven inputs. This will be included in the context dropdown.";
    return (
      <Tooltip title={tooltipText}>
        <Button
          type="link"
          className="copy-all"
          onClick={() => setIsAddingContext(true)}
        >
          <RiAddBoxLine fontSize="large" /> ADD CONTEXT
        </Button>
      </Tooltip>
    );
  };

  function formatDate(timestamp) {
    const date = new Date(parseInt(timestamp));
    const day = date.getDate();
    let suffix = "th";
    if (day % 10 === 1 && day !== 11) {
      suffix = "st";
    } else if (day % 10 === 2 && day !== 12) {
      suffix = "nd";
    } else if (day % 10 === 3 && day !== 13) {
      suffix = "rd";
    }
    const month = date.toLocaleString("en-US", { month: "long" });
    const year = date.getFullYear();
    return `${day}${suffix}, ${month} ${year}`;
  }
  const renderPinnedMessages = () => (
    <div className="pinboard-tab" data-testid="pin-and-notes-tab">
      {pinnedMessages.length === 0 && (
        <div className="empty-pinboard-tab">
          <p className="empty-state-message">
            Start pinning by clicking on the pin icon on the messages.
          </p>
        </div>
      )}
      {pinnedMessages.map((pinnedMessage, i) => (
        <Card
          hoverable
          key={i}
          className={`pinboard-card ${pinnedMessage.isUserDefined ? "user-defined" : ""}`}
          actions={[
            <div
              className="pinboard-card-action-items"
              style={{ backgroundColor: "#f9f9f9" }}
            >
              <div className="card-action">
                <ClockIcon size={16} className="clock-icon" />
                {formatDate(pinnedMessage.timestamp)}
              </div>
              <div className="card-action" key="actions">
                <Button
                  type="link"
                  onClick={() => onDelete(i)}
                  data-testid="delete"
                >
                  <RiDeleteBinLine style={{ fontSize: "large" }} />
                </Button>
                <Button
                  type="link"
                  onClick={() => onCopyOne(i)}
                  data-testid="copy"
                >
                  <RiCheckboxMultipleBlankFill style={{ fontSize: "large" }} />
                </Button>
              </div>
            </div>,
          ]}
        >
          <div className="pinboard-card-content">
            <MarkdownRenderer content={pinnedMessage.summary} />
          </div>
        </Card>
      ))}
    </div>
  );

  const deleteContext = (timestamp) => {
    deleteContextByTimestamp(timestamp);
    reloadUserSavedContexts();
    toast.success("Context deleted successfully!");
  };

  const contextAsText = (context) => {
    return "# " + context.title + "\n\n" + context.summary;
  };

  const copyContext = async (context) => {
    try {
      await navigator.clipboard.writeText(contextAsText(context));
      toast.success("Context copied successfully!");
    } catch (err) {
      toast.error("Failed to copy the context.");
    }
  };

  const renderUserSavedContexts = () => (
    <div className="pinboard-tab" data-testid="contexts-tab">
      {savedUserContexts.length === 0 && (
        <div className="empty-pinboard-tab">
          <p className="empty-state-message">
            Create context by clicking on the <i>Add context</i> button
          </p>
        </div>
      )}
      {savedUserContexts.map((context, i) => (
        <Card
          hoverable
          key={i}
          className={`pinboard-card ${context.isUserDefined ? "user-defined" : ""}`}
          actions={[
            <div
              className="pinboard-card-action-items"
              style={{ backgroundColor: "#f9f9f9" }}
            >
              <div className="card-action">
                <ClockIcon size={16} className="clock-icon" />
                {formatDate(context.timestamp)}
              </div>
              <div className="card-action" key="actions">
                <Button
                  type="link"
                  onClick={() => deleteContext(context.timestamp)}
                  data-testid="delete"
                >
                  <RiDeleteBinLine style={{ fontSize: "large" }} />
                </Button>
                <Button
                  type="link"
                  onClick={() => copyContext(context)}
                  data-testid="copy"
                >
                  <RiCheckboxMultipleBlankFill style={{ fontSize: "large" }} />
                </Button>
              </div>
            </div>,
          ]}
        >
          <div className="pinboard-card-content">
            <MarkdownRenderer content={contextAsText(context)} />
          </div>
        </Card>
      ))}
    </div>
  );

  const addNewNoteCallback = (newNote) => {
    const timestamp = Date.now().toString();
    const pinboardData = JSON.parse(localStorage.getItem("pinboard")) || {};
    pinboardData[timestamp] = { content: newNote, isUserDefined: true };
    localStorage.setItem("pinboard", JSON.stringify(pinboardData));

    setPinnedMessages(getPinboardData());
  };

  const reloadPinnedMessages = () => {
    setPinnedMessages(getPinboardData());
  };

  const reloadUserSavedContexts = () => {
    setSavedUserContexts(getSortedContexts());
  };

  const pinAndNotesTab = {
    key: "notes",
    label: (
      <div className="tab-title">
        <h3>Pins/Notes</h3>
      </div>
    ),
    children: renderPinnedMessages(),
  };

  const contextTab = {
    key: "context",
    label: (
      <div className="tab-title">
        <h3>Contexts</h3>
      </div>
    ),
    children: renderUserSavedContexts(),
  };

  const tabs = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI)
    ? [contextTab, pinAndNotesTab]
    : [pinAndNotesTab];

  const pinboardHeader = () => {
    return (
      <div className="pinboard-header">
        <div className="pinboard-title">
          <RiPushpinLine fontSize="large" />
          Pinboard
        </div>
        <p className="saved-response">
          Access content you've pinned to reuse in your Haiven inputs.
        </p>
        <div className="pinboard-actions">
          {isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI) &&
            addContextButtonWithTooltip()}
          {addNoteButtonWithTooltip()}
        </div>
      </div>
    );
  };

  return (
    <Modal
      title={pinboardHeader()}
      open={isModalVisible}
      onCancel={onClose}
      width={420}
      footer={null}
      className="pinboard-modal"
      mask={false}
    >
      <AddNewNote
        isAddingNote={isAddingNote}
        setIsAddingNote={setIsAddingNote}
        saveNewNote={addNewNoteCallback}
      />
      {isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI) && (
        <AddContext
          isAddingContext={isAddingContext}
          setIsAddingContext={setIsAddingContext}
          reloadContexts={reloadUserSavedContexts}
        />
      )}
      <Tabs defaultActiveKey="context" items={tabs}></Tabs>
    </Modal>
  );
};

export default Pinboard;
