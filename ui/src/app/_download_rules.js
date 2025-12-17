// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { RiDownload2Line } from "react-icons/ri";
import { Dropdown, message } from "antd";
import JSZip from "jszip";
import { generateReadmeContent, getFileName } from "./utils/rulesDownloadUtils";

const DownloadRules = ({ rules }) => {
  const handleRuleDownload = async (ruleId = null, ide = null) => {
    try {
      if (ruleId && ide) {
        // Individual rule download - create zip with rule file and README
        const response = await fetch(`/api/rules?rule_id=${ruleId}`, {
          method: "GET",
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch rule: ${response.statusText}`);
        }

        const content = await response.text();
        const rule = rules.find((r) => r.id === ruleId);
        if (!rule) {
          message.error("Rule not found");
          return;
        }

        const formattedContent = formatRuleContent({ ...rule, content }, ide);
        const filename = getFileName(rule, ide);

        // Create a zip file for individual rule
        const zip = new JSZip();
        const folderName = `${ide}-rule-${ruleId}`;
        const ruleFolder = zip.folder(folderName);

        // Add the rule file
        ruleFolder.file(filename, formattedContent);

        // Add README file
        const readmeContent = generateReadmeContent(ide);
        ruleFolder.file("README.md", readmeContent);

        // Generate and download zip
        const zipContent = await zip.generateAsync({ type: "blob" });
        downloadFile(zipContent, `${folderName}.zip`);
        message.success("Rule downloaded successfully");
      } else if (ide) {
        // All rules download
        const zip = new JSZip();
        const folderName = `${ide}-rules`;
        const allRulesFolder = zip.folder(folderName);

        if (ide === "copilot") {
          // For GitHub Copilot, create a single combined file
          const ruleContents = await Promise.all(
            rules.map(async (rule) => {
              const response = await fetch(`/api/rules?rule_id=${rule.id}`, {
                method: "GET",
                credentials: "include",
              });
              if (!response.ok) {
                throw new Error(
                  `Failed to fetch rule ${rule.id}: ${response.statusText}`,
                );
              }
              const content = await response.text();
              return `## ${rule.metadata?.title || rule.id}\n\n${content}`;
            }),
          );
          const combinedContent = ruleContents.join("\n\n---\n\n");
          allRulesFolder.file("copilot-instructions.md", combinedContent);
        } else {
          // For other IDEs, create individual rule files
          await Promise.all(
            rules.map(async (rule) => {
              const response = await fetch(`/api/rules?rule_id=${rule.id}`, {
                method: "GET",
                credentials: "include",
              });
              if (!response.ok) {
                throw new Error(
                  `Failed to fetch rule ${rule.id}: ${response.statusText}`,
                );
              }
              const content = await response.text();
              const formattedContent = formatRuleContent(
                { ...rule, content },
                ide,
              );
              const filename = getFileName(rule, ide);
              allRulesFolder.file(filename, formattedContent);
            }),
          );
        }

        // Add README file
        const readmeContent = generateReadmeContent(ide);
        allRulesFolder.file("README.md", readmeContent);

        // Generate and download zip
        const content = await zip.generateAsync({ type: "blob" });
        downloadFile(content, `${folderName}.zip`);
        message.success("Your file has been downloaded successfully");
      }
    } catch (error) {
      console.error("Error downloading rules:", error);
      message.error("Failed to download rules. Please try again.");
    }
  };

  const formatRuleContent = (rule, ide) => {
    const content = rule.content;
    const metadata = rule.metadata || {};
    const title = metadata.title || rule.id;

    if (ide === "cursor") {
      return formatForCursor(content, metadata, rule.id);
    } else if (ide === "copilot") {
      return content; // Plain content for GitHub Copilot
    } else if (ide === "amazon-q") {
      return formatForAmazonQ(content, metadata, title);
    } else {
      return `# ${title}\n\n${content}`;
    }
  };

  const formatForCursor = (content, metadata, ruleId) => {
    const description = metadata.description || metadata.title || ruleId;
    let mdcContent = `---\ndescription: ${description}\n`;

    if (metadata.globs && metadata.globs.length > 0) {
      mdcContent += "globs:\n";
      mdcContent += metadata.globs.map((glob) => `  - ${glob}`).join("\n");
      mdcContent += "\n";
    }

    mdcContent += `alwaysApply: ${metadata.alwaysApply || false}\n---\n\n${content}`;
    return mdcContent;
  };

  const formatForAmazonQ = (content, metadata, title) => {
    const description =
      metadata.description ||
      "Define coding standards and best practices for this rule.";
    const priority = metadata.priority || "Medium";

    return `# ${title}

## Purpose
${description}

## Instructions
- ${content}

## Priority
${priority}

## Error Handling
- If this rule cannot be applied, follow standard coding practices
- If unclear about implementation, ask for clarification`;
  };

  const downloadFile = (content, filename) => {
    // Check if content is already a Blob (for zip files) or needs to be converted
    const blob =
      content instanceof Blob
        ? content
        : new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getMenuItems = () => {
    if (!rules || rules.length === 0) return [];

    const items = [
      {
        key: "all-rules",
        label: "All Rules",
        children: [
          {
            key: "all-cursor",
            label: "Cursor",
            onClick: () => handleRuleDownload(null, "cursor"),
          },
          {
            key: "all-copilot",
            label: "GitHub Copilot",
            onClick: () => handleRuleDownload(null, "copilot"),
          },
          {
            key: "all-amazon-q",
            label: "Amazon Q",
            onClick: () => handleRuleDownload(null, "amazon-q"),
          },
          {
            key: "all-others",
            label: "Others",
            onClick: () => handleRuleDownload(null, "others"),
          },
        ],
      },
      {
        type: "divider",
      },
    ];

    // Add individual rules
    rules.forEach((rule) => {
      items.push({
        key: rule.id,
        label: rule.id,
        children: [
          {
            key: `${rule.id}-cursor`,
            label: "Cursor",
            onClick: () => handleRuleDownload(rule.id, "cursor"),
          },
          {
            key: `${rule.id}-copilot`,
            label: "GitHub Copilot",
            onClick: () => handleRuleDownload(rule.id, "copilot"),
          },
          {
            key: `${rule.id}-amazon-q`,
            label: "Amazon Q",
            onClick: () => handleRuleDownload(rule.id, "amazon-q"),
          },
          {
            key: `${rule.id}-others`,
            label: "Others",
            onClick: () => handleRuleDownload(rule.id, "others"),
          },
        ],
      });
    });

    return items;
  };

  if (!rules || rules.length === 0) {
    return null;
  }

  return (
    <div>
      <Dropdown
        menu={{ items: getMenuItems() }}
        trigger={["click"]}
        placement="bottomRight"
      >
        <button
          className="download-prompt-button"
          data-testid="download-rules-button"
        >
          <span>Download rules</span>
          <RiDownload2Line />
        </button>
      </Dropdown>
    </div>
  );
};

export default DownloadRules;
