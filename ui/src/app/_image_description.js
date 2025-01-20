// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { message, Upload, Button, Modal, Input } from "antd";
import { fetchSSE } from "./_fetch_sse";
import { RiImageAddLine, RiDeleteBinLine, RiEdit2Line } from "react-icons/ri";
import useLoader from "../hooks/useLoader";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
const { TextArea } = Input;

const DescribeImage = ({ onImageDescriptionChange, imageDescription }) => {
  const [image, setImage] = useState();
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [fileList, setFileList] = useState([]);
  const [showImageDescriptionModal, setShowImageDescriptionModal] =
    useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedDescription, setEditedDescription] = useState("");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  const beforeUpload = (file) => {
    const isJpgOrPng = file.type === "image/jpeg" || file.type === "image/png";
    if (!isJpgOrPng) {
      message.error("You can only upload JPG/PNG file!");
      return false;
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error("Image must smaller than 2MB!");
      return false;
    }
    setFileList([file]);
    setImage(file);
    return false;
  };

  const handleRemove = (file) => {
    if (loading) {
      abortLoad();
    }

    setFileList([]);
    setImage(null);
    onImageDescriptionChange("");
    return true;
  };

  const uploadProps = {
    name: "file",
    className: "image-uploader",
    beforeUpload: beforeUpload,
    onRemove: handleRemove,
    disabled: false,
    fileList: fileList,
    maxCount: 1,
    showUploadList: {
      showRemoveIcon: true,
      removeIcon: (
        <RiDeleteBinLine
          style={{
            fontSize: "16px",
            color: "#666666ff",
            visibility: "visible",
            display: "inline-flex",
          }}
        />
      ),
      showPreviewIcon: false,
    },
    itemRender: (originNode, file) => {
      const truncateFilename = (filename, maxLength = 20) => {
        const extension = filename.split(".").pop();
        const name = filename.substring(0, filename.lastIndexOf("."));
        if (name.length <= maxLength) return filename;
        return `${name.substring(0, maxLength)}...${extension}`;
      };

      return (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "4px 0",
            width: "225px",
          }}
        >
          <span
            style={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              maxWidth: "180px",
              fontSize: "12px",
            }}
          >
            {truncateFilename(file.name)}
          </span>
          <Button
            type="text"
            icon={
              <RiDeleteBinLine
                style={{
                  fontSize: "12px",
                  color: "#666666ff",
                }}
              />
            }
            onClick={() => handleRemove(file)}
            style={{
              visibility: "visible",
              display: "inline-flex",
              alignItems: "center",
              padding: "0 8px",
              marginLeft: "8px",
            }}
          />
        </div>
      );
    },
  };

  const disableImageDescriptionLink = () => {
    return imageDescription == null || imageDescription === "";
  };

  const describeImage = async (image) => {
    const formData = new FormData();
    formData.append("file", image);
    formData.append("prompt", "Describe this technical diagram to me");

    let ms = "";
    onImageDescriptionChange(ms);

    fetchSSE(
      "/api/prompt/image",
      {
        method: "POST",
        credentials: "include",
        headers: {},
        body: formData,
        signal: startLoad(),
      },
      {
        onErrorHandle: () => {
          onImageDescriptionChange("Error loading image description");
          abortLoad();
        },
        onFinish: () => {
          abortLoad();
        },
        onMessageHandle: (data) => {
          try {
            ms += data;
            onImageDescriptionChange(ms);
          } catch (error) {
            console.error("Error processing response", error);
          }
        },
      },
    );
  };

  useEffect(() => {
    if (image) {
      describeImage(image);
    }
  }, [image]);

  const onCloseImageDescriptionModal = () => {
    if (isEditMode && hasUnsavedChanges) {
      setIsCloseConfirmationModalVisible(true);
    } else {
      setShowImageDescriptionModal(false);
      setIsEditMode(false);
    }
  };

  return (
    <div className="upload-image-menu">
      <Upload {...uploadProps}>
        <Button
          className="upload-button"
          icon={<RiImageAddLine />}
          style={{
            backgroundColor: "#edf1f3",
            color: "#666666ff",
          }}
        >
          <div className="upload-placeholder">
            Drop your image here, or <span className="upload-text">upload</span>
          </div>
        </Button>
      </Upload>

      <div className="upload-image-content">
        <div className="loading-image">
          <StopLoad />
        </div>

        {disableImageDescriptionLink() ? null : (
          <Button
            className="view-image-description-link"
            type="link"
            onClick={() => {
              setEditedDescription(imageDescription);
              setShowImageDescriptionModal(true);
              setIsEditMode(false);
              setHasUnsavedChanges(false);
            }}
          >
            View/Edit Description
          </Button>
        )}
      </div>

      <Modal
        className="prompt-preview-modal"
        title="View/Edit Image Description"
        open={showImageDescriptionModal}
        closable={true}
        onCancel={onCloseImageDescriptionModal}
        width={800}
      >
        <div className="prompt-preview-header">
          <p style={{ position: "relative", left: "3px" }}>
            This is the AI-generated description of your image. You can edit it
            if needed.
          </p>
          <div className="prompt-preview-actions">
            <Button
              style={{ position: "relative", left: "42px", bottom: "3px" }}
              className="prompt-preview-edit-btn"
              onClick={() => setIsEditMode(true)}
              disabled={isEditMode}
            >
              <RiEdit2Line style={{ fontSize: "large" }} /> EDIT
            </Button>
          </div>
        </div>
        {isEditMode ? (
          <textarea
            className="prompt-editor"
            value={editedDescription}
            onChange={(e) => {
              setEditedDescription(e.target.value);
              setHasUnsavedChanges(true);
            }}
          />
        ) : (
          <div className="prompt-preview-container">
            <ReactMarkdown
              className="prompt-preview"
              remarkPlugins={[[remarkGfm]]}
            >
              {imageDescription}
            </ReactMarkdown>
          </div>
        )}
        <div className="button-container">
          <Button
            className="prompt-preview-close-btn"
            onClick={onCloseImageDescriptionModal}
          >
            CLOSE
          </Button>
          {isEditMode && (
            <Button
              className="prompt-preview-start-chat-btn"
              disabled={!hasUnsavedChanges}
              onClick={() => {
                onImageDescriptionChange(editedDescription);
                setShowImageDescriptionModal(false);
                setIsEditMode(false);
                setHasUnsavedChanges(false);
              }}
            >
              SAVE
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
          You have unsaved edits in the description. By closing any unsaved
          changes will be lost.
        </p>

        <div className="confirmation-modal-footer">
          <Button
            className="confirmation-modal-close-btn"
            onClick={() => {
              setShowImageDescriptionModal(false);
              setIsCloseConfirmationModalVisible(false);
              setIsEditMode(false);
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
};
export default DescribeImage;
