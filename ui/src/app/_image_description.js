// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { Upload, Button, Modal, Input } from "antd";
import { fetchSSE } from "./_fetch_sse";
import { RiImageAddLine, RiDeleteBinLine, RiEdit2Line } from "react-icons/ri";
import useLoader from "../hooks/useLoader";
import { toast } from "react-toastify";
import MarkdownRenderer from "./_markdown_renderer";
const { TextArea } = Input;

const DescribeImage = ({ onImageDescriptionChange, imageDescription }) => {
  const [image, setImage] = useState();
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [showImageDescriptionModal, setShowImageDescriptionModal] =
    useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedDescription, setEditedDescription] = useState("");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  const beforeUpload = (file) => {
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      toast.error("Image must be smaller than 2MB!");
      handleRemove(file);
      return false;
    }
    setImage(file);
    return true;
  };

  const handleRemove = (file) => {
    if (loading) {
      abortLoad();
    }

    setImage(null);
    onImageDescriptionChange("");
    return true;
  };

  const uploadProps = {
    name: "file",
    className: "image-uploader",
    beforeUpload: beforeUpload,
    onRemove: handleRemove,
    maxCount: 1,
    accept: "image/png, image/jpeg",
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
            Drop your image (less than 2MB) here, or
            <span className="upload-text">upload</span>
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
        className="view-or-edit-details-modal"
        title="View/Edit Image Description"
        open={showImageDescriptionModal}
        closable={true}
        onCancel={onCloseImageDescriptionModal}
      >
        <div className="metadata-header">
          <p>
            This is the AI-generated description of your image. You can edit it
            if needed.
          </p>
          <div className="actions">
            <Button
              className="edit-action-link"
              onClick={() => setIsEditMode(true)}
              disabled={isEditMode}
            >
              <RiEdit2Line /> EDIT
            </Button>
          </div>
        </div>
        {isEditMode ? (
          <textarea
            className="content-editor"
            value={editedDescription}
            onChange={(e) => {
              setEditedDescription(e.target.value);
              setHasUnsavedChanges(true);
            }}
          />
        ) : (
          <MarkdownRenderer
            content={imageDescription}
            className="content-viewer"
          />
        )}
        <div className="modal-footer">
          <Button
            className="close-modal-link"
            onClick={onCloseImageDescriptionModal}
          >
            CLOSE
          </Button>
          {isEditMode && (
            <Button
              className="proceed-to-action-link"
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
