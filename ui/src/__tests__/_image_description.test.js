// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, fireEvent, waitFor, screen } from "@testing-library/react";
import DescribeImage from "../app/_image_description";
import { fetchSSE } from "../app/_fetch_sse";
import { useState } from "react";

vi.mock("../app/_fetch_sse");

describe("DescribeImage Component", () => {
  it("should load and displays the image description when an image is uploaded", async () => {
    const imageText = "Mocked image description";
    const file = new File([imageText], "test-image.png", { type: "image/png" });

    fetchSSE.mockImplementation((url, options, eventHandlers) => {
      expect(url).toBe("/api/prompt/image");
      expect(options).toMatchObject({
        method: "POST",
        credentials: "include",
      });
      const formData = options.body;
      expect(formData.get("prompt")).toBe(
        "Describe this technical diagram to me",
      );
      expect(formData.get("file")).toBe(file);

      eventHandlers.onMessageHandle(imageText);
      eventHandlers.onFinish();
    });

    const TestComponent = () => {
      const [imageDescription, setImageDescription] = useState("");
      return (
        <DescribeImage
          onImageDescriptionChange={setImageDescription}
          imageDescription={imageDescription}
        />
      );
    };
    const { getByText, getByRole, queryByText } = render(<TestComponent />);

    const input = getByRole("button", {
      name: /upload/i,
    }).parentNode.querySelector("input");
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() =>
      expect(queryByText("View/Edit Description")).not.toBeNull(),
    );
    fireEvent.click(getByText("View/Edit Description"));

    await waitFor(() =>
      expect(getByText("Mocked image description")).toBeInTheDocument(),
    );
  });
});
