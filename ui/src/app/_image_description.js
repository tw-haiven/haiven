// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { LoadingOutlined, PlusOutlined } from "@ant-design/icons";
import { Flex, message, Upload, Button, Spin } from "antd";
import { fetchSSE } from "./_fetch_sse";

let ctrl;

const DescribeImage = ({ onImageDescriptionChange }) => {
  const [previewImageDataUrl, setPreviewImageDataUrl] = useState();
  const [image, setImage] = useState();
  const [descriptionLoading, setDescriptionLoading] = useState(false);

  const getBase64 = (img, callback) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => callback(reader.result));
    reader.readAsDataURL(img);
  };

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

  function abortDescriptionLoad() {
    ctrl && ctrl.abort("User aborted");
    setDescriptionLoading(false);
  }

  const describeImage = async (image) => {
    const formData = new FormData();
    formData.append("file", image);
    formData.append("prompt", "Describe this technical diagram to me");

    setDescriptionLoading(true);
    ctrl = new AbortController();

    let ms = "";
    onImageDescriptionChange(ms);

    fetchSSE(
      "/api/prompt/image",
      {
        method: "POST",
        credentials: "include",
        headers: {},
        body: formData,
        signal: ctrl.signal,
      },
      {
        onErrorHandle: () => {
          onImageDescriptionChange("Error loading image description");
          abortDescriptionLoad(false);
        },
        onFinish: () => {
          setDescriptionLoading(false);
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
    getBase64(info.file.originFileObj, (url) => {
      setPreviewImageDataUrl(url);
    });
    setImage(info.file.originFileObj);
  };

  const uploadButton = (
    <button
      style={{
        border: 0,
        background: "none",
      }}
      type="button"
    >
      <PlusOutlined />
      <div
        style={{
          marginTop: 8,
        }}
      >
        Upload
      </div>
    </button>
  );

  return (
    <Flex gap="middle" wrap>
      <Upload
        name="image"
        listType="picture-card"
        className="image-uploader"
        showUploadList={false}
        beforeUpload={beforeUpload}
        onChange={handleChange}
        disabled={descriptionLoading}
      >
        {previewImageDataUrl ? (
          <img
            src={previewImageDataUrl}
            alt="Preview of the image uploaded as input for the chat conversation"
            style={{
              width: "100%",
            }}
          />
        ) : (
          uploadButton
        )}
      </Upload>
      {descriptionLoading && (
        <>
          <Spin />
          <Button type="primary" danger onClick={abortDescriptionLoad}>
            Stop
          </Button>
        </>
      )}
    </Flex>
  );
};
export default DescribeImage;
