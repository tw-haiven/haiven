// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

export const frameRuleContent = (ruleData, ide = "") => {
  if (ide === "cursor") {
    // For Cursor, use MDC format with proper metadata
    const metadata = {
      description:
        ruleData.metadata?.description ||
        ruleData.metadata?.title ||
        ruleData.id,
      globs: ruleData.metadata?.globs || [],
      alwaysApply: ruleData.metadata?.alwaysApply || false,
    };

    let mdcContent = "---\n";
    mdcContent += `description: ${metadata.description}\n`;
    if (metadata.globs.length > 0) {
      mdcContent += `globs:\n${metadata.globs.map((glob) => `  - ${glob}`).join("\n")}\n`;
    }
    mdcContent += `alwaysApply: ${metadata.alwaysApply}\n`;
    mdcContent += "---\n\n";
    mdcContent += ruleData.content || "";

    return mdcContent;
  } else {
    // For other IDEs, use the original format
    let textContent = `TITLE:\n\n${ruleData.metadata?.title || ruleData.id}`;

    if (ruleData.metadata?.description) {
      textContent += `\n\nDESCRIPTION:\n\n${ruleData.metadata.description}`;
    }

    if (ruleData.metadata?.version) {
      textContent += `\n\nVERSION:\n\n${ruleData.metadata.version}`;
    }

    textContent += `\n\n\n\n\n\n\nRULE CONTENT:\n\n${ruleData.content || ""}`;
    return textContent;
  }
};

const ruleToDownload = (ruleData, ide = "") => {
  return {
    filename: getFileName(ruleData, ide),
    content: frameRuleContent(ruleData, ide),
  };
};

export const fetchRuleContent = async (rule, ide = "") => {
  const response = await fetch(`/api/rules?rule_id=${rule.id}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "text/plain",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch rule data");
  }

  const content = await response.text();
  return {
    filename: getFileName(rule, ide),
    content: frameRuleContent({ ...rule, content }, ide),
  };
};

export const fetchAllRulesContents = async (ide = "") => {
  const response = await fetch(`/api/download-rules?ide=${ide}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch rules data");
  }

  const rulesDataArray = await response.json();
  const rulesContents = rulesDataArray.map((ruleData) => {
    return ruleToDownload(ruleData, ide);
  });
  return rulesContents;
};

export const getFileName = (rule, ide = "") => {
  // Get the base filename without extension
  const baseFilename = rule.filename || rule.id;
  const filenameWithoutExt = baseFilename.replace(/\.[^/.]+$/, "");

  if (ide === "cursor") {
    // For Cursor, use .mdc extension
    return `${filenameWithoutExt}.mdc`;
  } else {
    // For other IDEs, use .md extension
    return `${filenameWithoutExt}.md`;
  }
};

export const generateReadmeContent = (ide) => {
  const readmeTemplates = {
    cursor: `# Haiven Rules for Cursor

This package contains AI coding rules optimized for Cursor IDE using the proper MDC format.

## Installation

1. Create a \`.cursor/rules\` directory in your project root (if it doesn't exist)
2. Copy the \`.mdc\` files to the \`.cursor/rules\` directory
3. Restart Cursor IDE
4. The rules will be automatically applied to your AI coding sessions

## Usage

These rules provide system-level instructions to Cursor's Agent and Inline Edit features. They are written in MDC format with proper metadata for:
- **Always**: Rules that are always included in model context
- **Auto Attached**: Rules included when files matching glob patterns are referenced
- **Agent Requested**: Rules available to AI, which decides whether to include them
- **Manual**: Rules only included when explicitly mentioned using @ruleName

## Files

- Each \`.mdc\` file contains a specific rule in MDC format
- Rules include proper metadata (description, globs, alwaysApply)
- Rules are optimized for Cursor's AI features

## Rule Types

- **Always**: Always included in model context
- **Auto Attached**: Included when files matching glob patterns are referenced
- **Agent Requested**: Available to AI, which decides whether to include them
- **Manual**: Only included when explicitly mentioned using @ruleName

## Support

For questions or issues, please refer to the Haiven documentation or Cursor's rules documentation: https://docs.cursor.com/en/context/rules
`,

    copilot: `# Haiven Rules for GitHub Copilot

This package contains AI coding rules optimized for GitHub Copilot in VS Code.

## Installation

1. Create a \`.github\` directory in your project root (if it doesn't exist)
2. Copy the \`copilot-instructions.md\` file to the \`.github\` directory
3. Ensure GitHub Copilot is enabled in VS Code
4. The rules will be automatically applied to your coding sessions

## Usage

These rules provide repository-level custom instructions for GitHub Copilot. They are used by:
- **Copilot Chat**: For conversational AI assistance
- **Code Review**: For automated pull request reviews
- **Code Suggestions**: For inline code completions

## Files

- \`copilot-instructions.md\` - Main instructions file for GitHub Copilot
- Each rule is formatted as markdown for optimal AI understanding
- Rules include proper metadata and version information

## Enabling Custom Instructions

### In VS Code:
1. Open Settings (Command+, on Mac / Ctrl+, on Windows/Linux)
2. Search for "instruction file"
3. Ensure "Code Generation: Use Instruction Files" is checked

### Verification:
- Look for the \`.github/copilot-instructions.md\` file in the References list when using Copilot Chat
- The file will be highlighted when Copilot uses your custom instructions

## Support

For questions or issues, please refer to the Haiven documentation or GitHub's Copilot documentation: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
`,

    "amazon-q": `# Haiven Rules for Amazon Q Developer

This package contains AI coding rules optimized for Amazon Q Developer using the official rules format.

## Installation

1. Create a \`.amazonq/rules\` directory in your project root (if it doesn't exist)
2. Copy the \`.md\` rule files to the \`.amazonq/rules\` directory
3. Ensure Amazon Q Developer is enabled in your IDE or CLI
4. The rules will be automatically applied to your coding sessions

## Usage

These rules provide structured guidance for Amazon Q Developer following the official format:
- **Purpose**: Clear explanation of why the rule exists
- **Instructions**: Specific directives with identifiers for Amazon Q Developer
- **Priority**: Critical/High/Medium/Low priority levels
- **Error Handling**: Fallback strategies and exception handling

## Files

- Each \`.md\` file contains a specific rule in Amazon Q Developer format
- Rules include proper metadata, priority levels, and error handling
- Rules can be organized in subdirectories for better structure
- Rules are automatically loaded and applied by Amazon Q Developer

## Rule Structure

Each rule follows the Amazon Q Developer format:
\`\`\`markdown
# Rule Name
## Purpose
Clear statement of why this rule exists

## Instructions
- Specific directive for Amazon Q Developer (ID: UNIQUE_ID)
- Additional instructions with their own identifiers
- Conditions under which instructions apply

## Priority
[Critical/High/Medium/Low]

## Error Handling
- How Amazon Q Developer should behave when exceptions occur
- Fallback strategies when primary instructions can't be followed
\`\`\`

## Support

For questions or issues, please refer to the Haiven documentation or Amazon Q Developer documentation: https://aws.amazon.com/blogs/devops/mastering-amazon-q-developer-with-rules/
`,

    others: `# Haiven Rules - Generic Format

This package contains AI coding rules in a generic format that can be used with various AI coding assistants.

## Installation

1. Copy the rule files to your preferred location
2. Configure your AI coding assistant to use these rules
3. The rules will be automatically applied to your coding sessions

## Usage

These rules will help guide AI assistants to follow best practices and coding standards.

## Files

- Each .md file contains a specific rule
- Rules are formatted for optimal AI understanding
- Version information is included in each rule

## Support

For questions or issues, please refer to the Haiven documentation.
`,
  };

  return readmeTemplates[ide] || readmeTemplates.cursor;
};
