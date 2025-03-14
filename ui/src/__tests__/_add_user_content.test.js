// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
import { vi } from "vitest";
import AddUserContent from "../app/_add_user_content";
import { toast } from "react-toastify";

vi.mock("react-toastify", () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe("AddUserContent", () => {
  const handleSubmit = vi.fn();
  const setIsOpen = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should show error toast if description is empty", () => {
    render(
      <AddUserContent
        isOpen={true}
        setIsOpen={setIsOpen}
        handleSubmit={handleSubmit}
      />,
    );

    fireEvent.change(screen.getByTestId("add-content-title"), {
      target: { value: "Test Title" },
    });

    fireEvent.click(screen.getByText("Save"));

    expect(toast.error).toHaveBeenCalledWith("Please enter some description");
  });

  it("should show error toast if title is empty", () => {
    render(
      <AddUserContent
        isOpen={true}
        setIsOpen={setIsOpen}
        handleSubmit={handleSubmit}
      />,
    );

    fireEvent.change(screen.getByTestId("add-content-description"), {
      target: { value: "Test Description" },
    });

    fireEvent.click(screen.getByText("Save"));

    expect(toast.error).toHaveBeenCalledWith("Please enter some title");
  });

  it("should call handleSubmit and show success toast if both title and description are provided", () => {
    render(
      <AddUserContent
        isOpen={true}
        setIsOpen={setIsOpen}
        handleSubmit={handleSubmit}
      />,
    );

    fireEvent.change(screen.getByTestId("add-content-title"), {
      target: { value: "Test Title" },
    });

    fireEvent.change(screen.getByTestId("add-content-description"), {
      target: { value: "Test Description" },
    });

    fireEvent.click(screen.getByText("Save"));

    expect(handleSubmit).toHaveBeenCalledWith("Test Title", "Test Description");
    expect(toast.success).toHaveBeenCalledWith("Content added successfully!");
  });
});
