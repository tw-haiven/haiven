// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Modal, Card, Button } from "antd";
import { RiDeleteBinLine, RiCheckboxMultipleBlankFill } from "react-icons/ri";
import { PinIcon, ClockIcon } from "lucide-react";
import { toast } from "react-toastify";

const Pinboard = ({ isModalVisible, onClose }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [pinnedMessages, setPinnedMessages] = useState([]);

  useEffect(() => {
    setIsMounted(true);
    if (typeof window !== "undefined") {
      const pinboardData = JSON.parse(window.localStorage.getItem("pinboard"));
      if (
        pinboardData &&
        typeof pinboardData === "object" &&
        !Array.isArray(pinboardData)
      ) {
        const pinboardArray = Object.keys(pinboardData).map((key) => ({
          timestamp: key,
          summary: pinboardData[key],
        }));
        setPinnedMessages(pinboardArray);
      }
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

  const pinboardTitle = () => {
    return (
      <div className="pinboard-title">
        <div style={{ display: "flex", alignItems: "center" }}>
          <PinIcon className="pin-icon" size={14} />
          Pinboard
        </div>
        <p className="saved-response">
          Access important messages you've pinned to the pinboard for quick
          reference.
        </p>
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
          className="pinboard-card"
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
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {pinnedMessage.summary}
            </ReactMarkdown>
          </div>
        </Card>
      ))}
    </Modal>
  );
};

export default Pinboard;
