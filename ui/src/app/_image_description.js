// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { Flex, message, Upload, Button, Spin } from "antd";
import { fetchSSE } from "./_fetch_sse";
import { RiImageAddLine } from "react-icons/ri";
import useLoader from "../hooks/useLoader";

const DescribeImage = ({ onImageDescriptionChange }) => {
  const [image, setImage] = useState();
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
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
    <Flex gap="middle" wrap>
      <Upload
        name="file"
        className="image-uploader"
        beforeUpload={beforeUpload}
        onChange={handleChange}
        disabled={loading}
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

      <StopLoad />
    </Flex>
  );
};
export default DescribeImage;
