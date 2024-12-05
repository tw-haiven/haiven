// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { message, Upload, Button, Modal, Input } from "antd";
import { fetchSSE } from "./_fetch_sse";
import { RiImageAddLine } from "react-icons/ri";
import useLoader from "../hooks/useLoader";
const { TextArea } = Input;

const DescribeImage = ({ onImageDescriptionChange, imageDescription }) => {
  const [image, setImage] = useState();
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [fileList, setFileList] = useState([]);
  const [showImageDescriptionModal, setShowImageDescriptionModal] = useState(false);

  const beforeUpload = async (file) => {
    const isJpgOrPng = file.type === "image/jpeg" || file.type === "image/png";
    if (!isJpgOrPng) {
      message.error("You can only upload JPG/PNG file!");
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error("Image must smaller than 2MB!");
    }

    return isJpgOrPng && isLt2M;
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

  const handleChange = (info) => {
    if (info.file.status === "uploading") {
      setImage(info.file.originFileObj);
      setFileList([{ ...info.file, status: "done" }]);
    }
  };

  return (
    <div class="upload-image-menu">
      <Upload
        name="file"
        className="image-uploader"
        beforeUpload={beforeUpload}
        onChange={handleChange}
        disabled={loading}
        fileList={fileList}
      >
        <Button
          className="upload-button"
          icon={
            <RiImageAddLine/>
          }
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

        {disableImageDescriptionLink() ?
          null :
          (
            <Button
              className="view-image-description-link"
              type="link"
              onClick={() => setShowImageDescriptionModal(true)}
            >
              View Image Description
            </Button>
          )}
      </div>

      <Modal
        className="image-description-modal"
        title="View image description"
        open={showImageDescriptionModal}
        closable={true}
        onCancel={() => setShowImageDescriptionModal(false)}
      >
        <TextArea value={imageDescription}/>
      </Modal>
    </div>
  );
};
export default DescribeImage;
