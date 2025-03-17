// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import {
  toReadableText,
  scenarioToText,
  DynamicDataRenderer,
  renderValue,
} from "../app/_dynamic_data_renderer";

// Mock window.matchMedia for Ant Design components
window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };

describe("toReadableText", () => {
  it("converts camelCase to readable text", () => {
    expect(toReadableText("camelCaseText")).toBe("Camel Case Text");
  });

  it("converts snake_case to readable text", () => {
    expect(toReadableText("snake_case_text")).toBe("Snake case text");
  });

  it("handles single word", () => {
    expect(toReadableText("word")).toBe("Word");
  });

  it("handles mixed case_and_camel", () => {
    expect(toReadableText("mixed_case_andCamel")).toBe("Mixed case and Camel");
  });
});

describe("scenarioToText", () => {
  it("converts basic scenario to markdown text", () => {
    const scenario = {
      title: "Test Scenario",
      description: "This is a test description",
      status: "Active",
    };

    const result = scenarioToText(scenario, []);

    expect(result).toContain("## Test Scenario");
    expect(result).toContain("**Description:**\nThis is a test description");
    expect(result).toContain("**Status:**\nActive");
  });

  it("excludes specified keys", () => {
    const scenario = {
      title: "Test Scenario",
      description: "This is a test description",
      status: "Active",
      secretField: "Should be excluded",
    };

    const result = scenarioToText(scenario, ["secretField"]);

    expect(result).toContain("## Test Scenario");
    expect(result).toContain("**Description:**\nThis is a test description");
    expect(result).toContain("**Status:**\nActive");
    expect(result).not.toContain("secretField");
    expect(result).not.toContain("Should be excluded");
  });

  it("automatically excludes default keys", () => {
    const scenario = {
      title: "Test Scenario",
      hidden: true,
      exclude: ["something"],
      id: "123",
      description: "This is a test description",
    };

    const result = scenarioToText(scenario, []);

    expect(result).toContain("## Test Scenario");
    expect(result).toContain("**Description:**\nThis is a test description");
    expect(result).not.toContain("**Hidden:**");
    expect(result).not.toContain("**Exclude:**");
    expect(result).not.toContain("**Id:**");
  });

  it("handles array values", () => {
    const scenario = {
      title: "Test Scenario",
      tags: ["tag1", "tag2", "tag3"],
    };

    const result = scenarioToText(scenario, []);

    expect(result).toContain("## Test Scenario");
    expect(result).toContain("**Tags:**\n- tag1\n- tag2\n- tag3");
  });

  it("works when called with only the data parameter (as in Array.map)", () => {
    const scenario = {
      title: "Map Test Scenario",
      description: "This tests using the function in Array.map",
    };

    // This simulates how the function is called in _cards-list.js
    const result = [scenario].map(scenarioToText)[0];

    expect(result).toContain("## Map Test Scenario");
    expect(result).toContain(
      "**Description:**\nThis tests using the function in Array.map",
    );
  });

  it("processes nested scenarios", () => {
    const scenario = {
      title: "Parent Scenario",
      description: "Parent description",
      scenarios: [
        {
          title: "Child Scenario 1",
          description: "Child description 1",
        },
        {
          title: "Child Scenario 2",
          description: "Child description 2",
        },
      ],
    };

    const result = scenarioToText(scenario, []);

    expect(result).toContain("## Parent Scenario");
    expect(result).toContain("**Description:**\nParent description");
    expect(result).toContain("### Child Scenario 1");
    expect(result).toContain("### Child Scenario 2");
    expect(result).toContain("**Description:**\nChild description 1");
    expect(result).toContain("**Description:**\nChild description 2");
  });
});

describe("DynamicDataRenderer", () => {
  it("renders fine when no data is provided", () => {
    render(<DynamicDataRenderer data={null} />);
  });

  it("renders nothing when data is not an object", () => {
    render(<DynamicDataRenderer data="string data" />);
    expect(screen.queryByText("string data")).not.toBeInTheDocument();
  });

  it("renders object data with proper formatting", () => {
    const testData = {
      name: "Test Name",
      description: "Test Description",
    };

    render(<DynamicDataRenderer data={testData} />);

    expect(screen.getByText("Name:")).toBeInTheDocument();
    expect(screen.getByText("Test Name")).toBeInTheDocument();
    expect(screen.getByText("Description:")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });

  it("excludes specified keys", () => {
    const testData = {
      name: "Test Name",
      secretField: "Secret Value",
      description: "Test Description",
    };

    render(<DynamicDataRenderer data={testData} exclude={["secretField"]} />);

    expect(screen.getByText("Name:")).toBeInTheDocument();
    expect(screen.getByText("Description:")).toBeInTheDocument();
    expect(screen.queryByText("Secret Field:")).not.toBeInTheDocument();
    expect(screen.queryByText("Secret Value")).not.toBeInTheDocument();
  });

  it("skips titles when skipTitles is true", () => {
    const testData = {
      name: "Test Name",
      description: "Test Description",
    };

    render(<DynamicDataRenderer data={testData} skipTitles={true} />);

    expect(screen.queryByText("Name:")).not.toBeInTheDocument();
    expect(screen.getByText("Test Name")).toBeInTheDocument();
    expect(screen.queryByText("Description:")).not.toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });
});

describe("renderValue", () => {
  it("renders dash for null or undefined values", () => {
    render(<div>{renderValue(null)}</div>);
    expect(screen.getByText("-")).toBeInTheDocument();

    render(<div>{renderValue(undefined)}</div>);
    expect(screen.getAllByText("-").length).toBe(2);
  });

  it("renders dash for empty string", () => {
    render(<div>{renderValue("")}</div>);
    expect(screen.getAllByText("-").length).toBe(1);
  });

  it("renders primitive values", () => {
    render(<div>{renderValue("test string")}</div>);
    expect(screen.getByText("test string")).toBeInTheDocument();

    render(<div>{renderValue(42)}</div>);
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("renders array of primitives as list", () => {
    render(<div>{renderValue(["item1", "item2", "item3"])}</div>);

    expect(screen.getByText("item1")).toBeInTheDocument();
    expect(screen.getByText("item2")).toBeInTheDocument();
    expect(screen.getByText("item3")).toBeInTheDocument();
  });

  it("renders 'None' for empty arrays", () => {
    render(<div>{renderValue([])}</div>);
    expect(screen.getByText("None")).toBeInTheDocument();
  });

  it("renders dash for empty items in arrays", () => {
    render(<div>{renderValue(["item1", "", null])}</div>);

    expect(screen.getByText("item1")).toBeInTheDocument();
    expect(screen.getAllByText("-").length).toBe(2);
  });
});
