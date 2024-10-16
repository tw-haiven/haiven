// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Modal, Card, Button, message } from "antd";
import { RiDeleteBinLine, RiCheckboxMultipleBlankFill } from "react-icons/ri";
import { PinIcon, ClockIcon } from "lucide-react";

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
    message.success("Scenario deleted successfully!");
  };

  const onCopyOne = async (index) => {
    try {
      await navigator.clipboard.writeText(
        scenarioToText(pinnedMessages[index]),
      );
      message.success("Scenario copied to clipboard!");
    } catch (err) {
      message.error("Failed to copy the scenario to clipboard.");
    }
  };

  const pinboardTitle = () => {
    return (
      <div className="pinboard-title">
        <div style={{ display: "flex", alignItems: "center" }}>
          <PinIcon className="pin-icon" size={14} />
          Pinboard
        </div>
        <p style={{ fontSize: "12px" }}>Your saved response</p>
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
      style={{
        position: "fixed",
        right: 0,
        top: "67px",
        bottom: 0,
        height: "95vh",
        overflow: "auto",
      }}
      mask={false}
    >
      <div className="cards-container with-display-mode">
        {pinnedMessages.map((pinnedMessage, i) => (
          <Card
            hoverable
            key={i}
            className="scenario"
            actions={[
              <div className="pinboard-card-action-items">
                <div className="date">
                  <ClockIcon size={16} className="clock-icon" />
                  {formatDate(pinnedMessage.timestamp)}
                </div>
                <div style={{ display: "flex" }} key="actions">
                  <Button type="link" onClick={() => onDelete(i)}>
                    <RiDeleteBinLine style={{ fontSize: "large" }} />
                  </Button>
                  <Button type="link" onClick={() => onCopyOne(i)}>
                    <RiCheckboxMultipleBlankFill
                      style={{ fontSize: "large" }}
                    />
                  </Button>
                </div>
              </div>,
            ]}
          >
            <div className="scenario-card-content">
              <div className="scenario-summary">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {pinnedMessage.summary}
                </ReactMarkdown>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </Modal>
  );
};

export default Pinboard;
