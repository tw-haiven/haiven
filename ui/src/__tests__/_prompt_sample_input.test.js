// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import PromptSampleInput from "../app/_prompt_sample_input";

test("renders SampleInput component and opens modal on button click", () => {
  const sampleInput = "Prompt Example";
  render(<PromptSampleInput sampleInput={sampleInput} />);

  const button = screen.getByRole("button");
  expect(button).toBeInTheDocument();

  fireEvent.click(button);
  const modalTitle = screen.getByText(/Prompt Example/i);
  expect(modalTitle).toBeInTheDocument();
});
