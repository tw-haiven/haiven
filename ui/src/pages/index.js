// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Card, ConfigProvider, Tag, Tabs, Tooltip } from "antd";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  getPrompts,
  getDisclaimerAndGuidelines,
  getInspirations,
} from "../app/_boba_api";
import { staticFeaturesForDashboard } from "../app/_navigation_items";
import DisclaimerPopup from "../app/_disclaimer_popup";
import { RiBookShelfLine } from "react-icons/ri";
import { MdLightbulb } from "react-icons/md";
import ReactMarkdown from "react-markdown";

export default function ChatDashboard() {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [disclaimerConfig, setDisclaimerConfig] = useState({});
  const [inspirations, setInspirations] = useState([]);

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

    getDisclaimerAndGuidelines((data) => {
      if (data) {
        setDisclaimerConfig({
          title: data.title,
          message: data.content,
        });
      } else {
        setDisclaimerConfig(null);
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

    getInspirations((data) => {
      setInspirations(data);
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
      <DisclaimerPopup disclaimerConfig={disclaimerConfig} />
      <ConfigProvider
        theme={{
          components: {
            Tabs: {
              itemSelectedColor: "white",
              inkBarColor: "#003d4f",
            },
          },
        }}
      >
        <div className="dashboard">
          <div className="dashboard-sections">
            <div className="headline">
              <h1>What would you like to do today?</h1>
              <div className="subline">
                Haiven is your intelligent AI assistant, here to assist you to
                kick-start your software delivery activities
              </div>
            </div>
            <Tabs
              defaultActiveKey="codified"
              items={[
                {
                  key: "codified",
                  label: (
                    <div className="tab-title">
                      <h3>
                        <RiBookShelfLine
                          style={{ position: "relative", top: "3px" }}
                        />{" "}
                        Codified Practices
                      </h3>
                    </div>
                  ),
                  children: (
                    <div className="codified-practices-section">
                      <div className="section-description">
                        <p>
                          These are carefully prepared prompts from your Haiven
                          knowledge pack that codify recommended practices. Use
                          these in particular when the default results and
                          "common wisdom" of AI models does not align enough
                          with your ways of working.
                        </p>
                      </div>
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
                      <div className={`dashboard-cards-grid-container`}>
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
                                <ReactMarkdown>
                                  {prompt.help_prompt_description}
                                </ReactMarkdown>
                              </Card>
                            </Link>
                          ))}
                        </div>
                      </div>
                    </div>
                  ),
                },
                {
                  key: "inspirations",
                  label: (
                    <div className="tab-title">
                      <h3>
                        <MdLightbulb
                          style={{ position: "relative", top: "3px" }}
                        />{" "}
                        Inspirations
                      </h3>
                    </div>
                  ),
                  children: (
                    <div className="inspirations-section">
                      <div className="section-description">
                        <p>
                          More ideas for how you can use AI to help you with
                          your software delivery activities. Other than the
                          codified practices prompts, these are very simple
                          prompt starters, responses will be what AI models know
                          without any additional guidance about a practice.
                          Results with these simple prompts will not be as good
                          as with the codified practices.
                        </p>
                      </div>
                      <div className={`dashboard-cards-grid-container`}>
                        <div className="dashboard-cards-grid">
                          {inspirations.map((inspiration, index) => (
                            <Link
                              href={`/knowledge-chat?inspiration=${inspiration.id}`}
                              key={`inspiration-${index}`}
                            >
                              <Tooltip title="Click to use this inspiration">
                                <Card
                                  hoverable
                                  key={`inspiration-card-${index}`}
                                  title={inspiration.title}
                                  className="dashboard-tile scenario-card-content"
                                  style={{ backgroundColor: "#f5f5f5" }}
                                >
                                  {inspiration.prompt_template.substring(
                                    0,
                                    200,
                                  )}
                                  ...
                                </Card>
                              </Tooltip>
                            </Link>
                          ))}
                        </div>
                      </div>
                    </div>
                  ),
                },
              ].filter(Boolean)}
            />
          </div>
        </div>
      </ConfigProvider>
    </>
  );
}
