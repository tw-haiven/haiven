// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Card, Space, Flex, Tag } from "antd";

import { use, useEffect, useState } from "react";

import { getPrompts } from "../app/_boba_api";

export default function ChatDashboard() {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);

  const categoryColors = {
    analysis: "#f2617aff",
    coding: "#CC850A",
    testing: "#47a1ad",
    architecture: "#634F7D",
    ideation: "#6B9E78",
    other: "#666666ff",
  };

  const filter = (tag, checked) => {
    if (checked) {
      setSelectedCategories([...selectedCategories, tag]);
    } else {
      setSelectedCategories(
        selectedCategories.filter((category) => category !== tag),
      );
    }
  };

  useEffect(() => {
    getPrompts((data) => {
      setPrompts(data);
      setFilteredPrompts(data);

      const categories = [
        ...new Set(data.flatMap((prompt) => prompt.categories)),
      ];
      setAllCategories(categories);
    });
  }, []);

  useEffect(() => {
    setFilteredPrompts(
      prompts.filter((prompt) =>
        prompt.categories.some((category) =>
          selectedCategories.includes(category),
        ),
      ),
    );
  }, [selectedCategories]);

  return (
    <div className="dashboard">
      <h1>Chat center dashboard</h1>
      <p>These are all the prompts available in your current knowledge pack.</p>

      <p className="dashboard-filters">
        <b>Filter:</b>
        {allCategories.map((tag) => {
          return (
            <Tag.CheckableTag
              key={tag}
              checked={selectedCategories.includes(tag)}
              onChange={(checked) => filter(tag, checked)}
              color="gray"
              className="dashboard-filter-category"
            >
              {tag}
            </Tag.CheckableTag>
          );
        })}
      </p>

      <Space direction="horizontal" wrap>
        {filteredPrompts.map((prompt, index) => {
          return (
            <a
              href={"/chat?prompt=" + prompt.identifier}
              key={prompt.identifier + "-href"}
            >
              <Card
                key={prompt.identifier}
                title={prompt.title}
                extra={
                  <div className="tile-tags">
                    {prompt.categories.map((category) => {
                      return (
                        <Tag
                          color={
                            categoryColors[category] || categoryColors["other"]
                          }
                        >
                          {category}
                        </Tag>
                      );
                    })}
                  </div>
                }
                className="dashboard-tile scenario-card-content"
              >
                <div className="card-prop-name">Description</div>
                <div className="card-prop-value">
                  {prompt.help_prompt_description}
                </div>
                <div className="card-prop-name">Input needed</div>
                <div className="card-prop-value">{prompt.help_user_input}</div>
              </Card>
            </a>
          );
        })}
      </Space>
    </div>
  );
}
