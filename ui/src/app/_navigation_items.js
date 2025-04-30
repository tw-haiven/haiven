// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import Link from "next/link";
import {
  RiFlaskLine,
  RiLightbulbLine,
  RiCodeBoxLine,
  RiBookReadLine,
  RiChat2Line,
  RiChatQuoteLine,
  RiCompasses2Line,
  RiBook2Line,
  RiDashboardHorizontalLine,
} from "react-icons/ri";
import { isFeatureEnabled, FEATURES } from "./feature_toggle";

// Keeping the implementation of menu items for the "static" features in one place
// Will usually be enhanced by the dynamically loaded prompts afterwards

export const initialiseMenuCategoriesForSidebar = () => {
  const categories = {
    dashboard: {
      key: "dashboard",
      label: <Link href="/">Dashboard</Link>,
      icon: <RiDashboardHorizontalLine style={{ fontSize: "large" }} />,
    },
    knowledgeChat: {
      key: "knowledgeChat",
      label: <Link href="/knowledge-chat">Chat with Haiven</Link>,
      icon: <RiChatQuoteLine style={{ fontSize: "large" }} />,
    },
    research: {
      key: "research",
      label: "Research",
      icon: <RiBook2Line style={{ fontSize: "large" }} />,
      children: [],
    },
    ideate: {
      key: "ideate",
      label: "Ideate",
      icon: <RiLightbulbLine style={{ fontSize: "large" }} />,
      children: [
        {
          key: "creative-matrix",
          label: <Link href="/creative-matrix">Creative Matrix</Link>,
        },
        {
          key: "scenarios",
          label: <Link href="/scenarios">Scenario Design</Link>,
        },
      ],
    },
    analysis: {
      key: "analyse",
      label: "Analyse",
      icon: <RiBookReadLine style={{ fontSize: "large" }} />,
      children: [],
    },
    coding: {
      key: "coding",
      label: "Coding",
      icon: <RiCodeBoxLine style={{ fontSize: "large" }} />,
      children: [],
    },
    testing: {
      key: "testing",
      label: "Testing",
      icon: <RiFlaskLine style={{ fontSize: "large" }} />,
      children: [],
    },
    architecture: {
      key: "architecture",
      label: "Architecture",
      icon: <RiCompasses2Line style={{ fontSize: "large" }} />,
      children: [],
    },
    other: {
      key: "other",
      label: "Other",
      icon: <RiChat2Line style={{ fontSize: "large" }} />,
      children: [],
    },
  };

  if (isFeatureEnabled(FEATURES.FEATURE_DELIVERY_MANAGEMENT)) {
    categories.deliveryManagement = {
      key: "deliveryManagement",
      label: "Delivery Management",
      icon: <RiDashboardHorizontalLine style={{ fontSize: "large" }} />,
      children: [],
    };
  }

  return categories;
};

export const staticFeaturesForDashboard = () => {
  return [
    {
      identifier: "boba-creative-matrix",
      title: "Creative Matrix",
      help_prompt_description:
        'Create a "Creative Matrix" to generate new ideas across dimensions that you can define yourself.',
      categories: ["ideate"],
      type: "static",
      link: "/creative-matrix",
    },
    {
      identifier: "boba-scenarios",
      title: "Scenario Design",
      help_prompt_description:
        "Brainstorm a range of scenarios for your product domain based on criteria like time horizon, realism, and optimism.",
      categories: ["ideate"],
      type: "static",
      link: "/scenarios",
    },
  ];
};
