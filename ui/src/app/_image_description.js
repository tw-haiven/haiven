// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { Flex, message, Upload, Button, Spin } from "antd";
import { fetchSSE } from "./_fetch_sse";
import { RiImageAddLine } from "react-icons/ri";

let ctrl;

const DescribeImage = ({ onImageDescriptionChange }) => {
  const [image, setImage] = useState();
  const [descriptionLoading, setDescriptionLoading] = useState(false);
  const [fileList, setFileList] = useState([]);

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
    if (info.file.status === "uploading") {
      setImage(info.file.originFileObj);
      setFileList([{ ...info.file, status: "done" }]);
    }
  };

  return (
    <Flex gap="middle" wrap>
      <Upload
        name="file"
        className="image-uploader"
        beforeUpload={beforeUpload}
        onChange={handleChange}
        disabled={descriptionLoading}
        fileList={fileList}
      >
        <Button
          icon={
            <RiImageAddLine style={{ fontSize: "2em", color: "#666666ff" }} />
          }
          style={{
            backgroundColor: "#edf1f3",
            color: "#666666ff",
          }}
        >
          Click or drag to upload
        </Button>
      </Upload>

      {descriptionLoading && (
        <div style={{ marginBottom: "1em", marginTop: "-1em" }}>
          <Spin />
          <Button
            type="secondary"
            danger
            onClick={abortDescriptionLoad}
            className="stop-button"
          >
            STOP
          </Button>
        </div>
      )}
    </Flex>
  );
};
export default DescribeImage;
