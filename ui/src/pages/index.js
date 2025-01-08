// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Card, Space, Tag } from "antd";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getPrompts, getWelcomeMessage } from "../app/_boba_api";
import { staticFeaturesForDashboard } from "../app/_navigation_items";
import WelcomePopup from "../app/_welcome_popup";
import { aiIdeas } from "../app/_ai_ideas";
import { RiLightbulbFlashLine, RiFocus2Line } from "react-icons/ri";
import { Position } from "reactflow";

export default function ChatDashboard() {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [welcomeConfig, setWelcomeConfig] = useState({});

  // !! If changed, also needs to be changed in CSS, for the filter selection colors
  const categoryColors = {
    ideate: "#6B9E78",
    research: "#003d4f",
    analysis: "#f2617aff",
    coding: "#CC850A",
    testing: "#47a1ad",
    architecture: "#634F7D",
    other: "#666666ff",
  };

  const categoryOrder = [
    "research",
    "ideate",
    "analysis",
    "coding",
    "testing",
    "architecture",
    "other",
  ];

  const filter = (tag, checked) => {
    const isSelected = selectedCategories.includes(tag);
    const isAllSelected = selectedCategories.length === allCategories.length;

    if (checked) {
      setSelectedCategories([...selectedCategories, tag]);
    } else if (isSelected && selectedCategories.length === 1) {
      setSelectedCategories(allCategories);
    } else if (!checked && isAllSelected) {
      setSelectedCategories([tag]);
    } else {
      setSelectedCategories(
        selectedCategories.filter((category) => category !== tag),
      );
    }
  };

  function sortCategoriesByOrder(categories) {
    categories.sort(
      (a, b) => categoryOrder.indexOf(a) - categoryOrder.indexOf(b),
    );
  }

  useEffect(() => {
    const typeToUrlMap = {
      chat: "/chat",
      cards: "/cards",
    };

    getWelcomeMessage((data) => {
      if (data) {
        setWelcomeConfig({
          title: data.title,
          message: data.content,
        });
      } else {
        setWelcomeConfig(null);
      }
    });

    getPrompts((data) => {
      data = data
        .filter((prompt) => prompt.show !== false)
        .map((prompt) => {
          const url = typeToUrlMap[prompt.type] || "/chat";
          prompt.link = `${url}?prompt=${prompt.identifier}`;
          return prompt;
        });
      // add the "static" features
      data = data.concat(staticFeaturesForDashboard());

      data.forEach((prompt) => {
        sortCategoriesByOrder(prompt.categories);
      });
      data.sort((a, b) => {
        for (
          let i = 0;
          i < Math.min(a.categories.length, b.categories.length);
          i++
        ) {
          const comparison =
            categoryOrder.indexOf(a.categories[i]) -
            categoryOrder.indexOf(b.categories[i]);
          if (comparison !== 0) {
            return comparison;
          }
        }
        return a.categories.length - b.categories.length;
      });

      setPrompts(data);
      setFilteredPrompts(data);

      const categories = [
        ...new Set(data.flatMap((prompt) => prompt.categories)),
      ];
      categories.push("other");

      sortCategoriesByOrder(categories);
      setAllCategories(categories);
      setSelectedCategories(categories);
    });
  }, []);

  useEffect(() => {
    if (selectedCategories.length === 0) {
      setFilteredPrompts(prompts);
      return;
    }

    setFilteredPrompts(
      prompts.filter((prompt) =>
        prompt.categories.some((category) =>
          selectedCategories.includes(category),
        ),
      ),
    );
  }, [selectedCategories]);

  return (
    <>
      <WelcomePopup welcomeConfig={welcomeConfig} />
      <div className="dashboard">
        <div className="headline">
          <h1>What would you like to do today?</h1>
          <div className="subline">
            Haiven is your intelligent AI assistant, here to assist you to
            kick-start your software delivery activities
          </div>
        </div>

        <div className="dashboard-sections">
          <div className="codified-practices-section">
            <h2>Start with a prompt from your knowledge pack</h2>
            <p className="dashboard-filters">
              <b>Filter by category:</b>
              {allCategories.map((tag) => (
                <Tag.CheckableTag
                  key={tag}
                  checked={selectedCategories.includes(tag)}
                  onChange={(checked) => filter(tag, checked)}
                  color="gray"
                  className={"dashboard-filter-category " + tag}
                >
                  {tag}
                </Tag.CheckableTag>
              ))}
            </p>
            <div className="dashboard-scenarios">
              <div className="dashboard-scenarios-title">
                <h3
                  style={{ position: "relative", left: "-20px", top: "10px" }}
                >
                  <RiFocus2Line
                    style={{ position: "relative", left: "-1px", top: "3px" }}
                  />{" "}
                  Codified Practices
                </h3>
                <p style={{ position: "relative", left: "-20px", top: "15px" }}>
                  Expert-validated prompts that codify Thoughtworks recommended
                  practices.
                </p>
              </div>
              <div
                className={`dashboard-cards-grid-container ${aiIdeas && aiIdeas.length > 0 ? "with-ai-ideas" : ""}`}
              >
                <div className="dashboard-cards-grid">
                  {filteredPrompts.map((prompt, index) => (
                    <Link
                      href={prompt.link || "#"}
                      key={prompt.identifier + "-href"}
                    >
                      <Card
                        hoverable
                        key={prompt.identifier}
                        title={prompt.title}
                        className="dashboard-tile scenario-card-content"
                        actions={prompt.categories.map((category) => (
                          <Tag
                            className="capitalize"
                            color={
                              categoryColors[category] ||
                              categoryColors["other"]
                            }
                          >
                            {category}
                          </Tag>
                        ))}
                      >
                        {prompt.help_prompt_description}
                      </Card>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {aiIdeas && aiIdeas.length > 0 && (
            <div className="ai-help-section">
              <div className="ai-help-section-title">
                <div className="border-line"></div>
                <h2 style={{ position: "relative", top: "6px", left: "-58px" }}>
                  <RiLightbulbFlashLine
                    style={{ position: "relative", top: "1px", left: "3px" }}
                  />
                  Or let AI help you to...
                </h2>
                <p
                  style={{ position: "relative", top: "-10px", left: "-25px" }}
                >
                  Quick actions to get AI assistance for common development
                  tasks.
                </p>
              </div>
              <div className="ai-help-ideas">
                <Space direction="horizontal" wrap>
                  {aiIdeas.map((idea) => (
                    <Link
                      href={`/knowledge-chat?idea=${idea.id}`}
                      key={idea.id}
                    >
                      <Card
                        hoverable
                        title={idea.title}
                        className="dashboard-tile ai-idea-card"
                      >
                        {idea.description}
                      </Card>
                    </Link>
                  ))}
                </Space>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
