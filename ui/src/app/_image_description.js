// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { LoadingOutlined, PlusOutlined } from "@ant-design/icons";
import { Flex, message, Upload } from "antd";
import { fetchSSE } from "./_fetch_sse";

const DescribeImage = ({ onImageDescriptionChange }) => {
  const [loading, setLoading] = useState(false);
  const [previewImageDataUrl, setPreviewImageDataUrl] = useState();
  const [image, setImage] = useState();

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

  const describeImage = async (image) => {
    const formData = new FormData();
    formData.append("file", image);
    formData.append("prompt", "Describe this technical diagram to me");

    let ms = "";

    fetchSSE(
      "/api/prompt/image",
      {
        method: "POST",
        credentials: "include",
        headers: {},
        body: formData,
      },
      {
        onErrorHandle: () => {
          onImageDescriptionChange("Error loading image description");
        },
        onFinish: () => {},
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
      setLoading(false);
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
      {loading ? <LoadingOutlined /> : <PlusOutlined />}
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
    </Flex>
  );
};
export default DescribeImage;
