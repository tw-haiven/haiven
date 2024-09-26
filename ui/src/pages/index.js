// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Card, Space, Tag } from "antd";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getPrompts } from "../app/_boba_api";
import { staticFeaturesForDashboard } from "../app/_navigation_items";

export default function ChatDashboard() {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);

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
    getPrompts((data) => {
      data.forEach((prompt) => {
        prompt.type = "chat";
        prompt.link = "/chat?prompt=" + prompt.identifier;
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
    <div className="dashboard">
      <h1>What would you like to do today?</h1>
      <div className="subline">
        Haiven is your intelligent AI assistant, here to assist you to
        kick-start your software delivery activities
      </div>
      <h2>Start with a prompt from your knowledge pack</h2>

      <p className="dashboard-filters">
        <b>Filter by category:</b>
        {allCategories.map((tag) => {
          return (
            <Tag.CheckableTag
              key={tag}
              checked={selectedCategories.includes(tag)}
              onChange={(checked) => filter(tag, checked)}
              color="gray"
              className={"dashboard-filter-category " + tag}
            >
              {tag}
            </Tag.CheckableTag>
          );
        })}
      </p>

      <div className="dashboard-scenarios">
        <Space direction="horizontal" wrap>
          {filteredPrompts.map((prompt, index) => {
            return (
              <Link href={prompt.link || "#"} key={prompt.identifier + "-href"}>
                <Card
                  hoverable
                  key={prompt.identifier}
                  title={prompt.title}
                  className="dashboard-tile scenario-card-content"
                >
                  <div className="card-contents">
                    <div className="card-prop-value">
                      {prompt.help_prompt_description}
                    </div>
                  </div>
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
                </Card>
              </Link>
            );
          })}
        </Space>
      </div>
    </div>
  );
}
