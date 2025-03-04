// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Modal, Card, Button, Tooltip } from "antd";
import {
  RiDeleteBinLine,
  RiCheckboxMultipleBlankFill,
  RiAddBoxLine,
  RiPushpinLine,
} from "react-icons/ri";
import { ClockIcon } from "lucide-react";
import { toast } from "react-toastify";
import { getPinboardData } from "../app/_local_store";
import MarkdownRenderer from "../app/_markdown_renderer";
import AddNewNoteModal from "../app/_add_new_note_modal";

const Pinboard = ({ isModalVisible, onClose }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [pinnedMessages, setPinnedMessages] = useState([]);
  const [isAddingNote, setIsAddingNote] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    if (typeof window !== "undefined") {
      setPinnedMessages(getPinboardData());
    }
  }, [
    typeof window !== "undefined"
      ? window.localStorage.getItem("pinboard")
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
    setPinnedMessages(updatedPinnedMessages);
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

  const pinboardTitle = () => {
    return (
      <div className="pinboard-title">
        <div style={{ display: "flex", alignItems: "center" }}>
          <RiPushpinLine fontSize="large" />
          Pinboard
        </div>
        <p className="saved-response">
          Access content you've pinned to reuse in your Haiven inputs.
        </p>
        {addNoteButtonWithTooltip()}
      </div>
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
    <>
      {pinnedMessages.length === 0 && (
        <div className="empty-pinboard">
          <p className="empty-state-message">
            Start pinning by clicking on the pin
          </p>
          <p className="empty-state-instruction">icon on the messages</p>
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
                <Button type="link" onClick={() => onDelete(i)}>
                  <RiDeleteBinLine style={{ fontSize: "large" }} />
                </Button>
                <Button type="link" onClick={() => onCopyOne(i)}>
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
    </>
  );

  const addNewNoteCallback = (newNote) => {
    const timestamp = Date.now().toString();
    const pinboardData = JSON.parse(localStorage.getItem("pinboard")) || {};
    pinboardData[timestamp] = { content: newNote, isUserDefined: true };
    localStorage.setItem("pinboard", JSON.stringify(pinboardData));

    setPinnedMessages([
      { timestamp, summary: newNote, isUserDefined: true },
      ...pinnedMessages,
    ]);
  };

  return (
    <Modal
      title={pinboardTitle()}
      open={isModalVisible}
      onCancel={onClose}
      width={420}
      footer={null}
      className="pinboard-modal"
      mask={false}
    >
      <AddNewNoteModal
        isAddingNote={isAddingNote}
        setIsAddingNote={setIsAddingNote}
        callBack={addNewNoteCallback}
      />
      {renderPinnedMessages()}
    </Modal>
  );
};

export default Pinboard;
