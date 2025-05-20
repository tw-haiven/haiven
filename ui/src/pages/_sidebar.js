// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import { RiGlobalLine } from "react-icons/ri";
import { initialiseMenuCategoriesForSidebar } from "../app/_navigation_items";
import { FEATURES } from "../app/feature_toggle";

const Sidebar = ({ prompts, featureToggleConfig }) => {
  const pathToKey = {
    "/scenarios": "scenarios",
    "/creative-matrix": "creative-matrix",
    "/knowledge-chat": "knowledgeChat",
    "/": "dashboard",
  };
  const router = useRouter();
  const currentSelectedKey = pathToKey[router.pathname];

  const [menuItems, setMenuItems] = useState([]);

  const typeToUrlMap = {
    chat: "/chat",
    cards: "/cards",
  };

  useEffect(() => {
    const menuCategories = initialiseMenuCategoriesForSidebar(
      featureToggleConfig[FEATURES.FEATURE_DELIVERY_MANAGEMENT] === true,
    );

    prompts
      .filter((prompt) => prompt.show !== false)
      .filter((prompt) => {
        if (prompt.categories.includes("deliveryManagement")) {
          return (
            featureToggleConfig[FEATURES.FEATURE_DELIVERY_MANAGEMENT] === true
          );
        }
        return true;
      })
      .forEach((prompt) => {
        const url = typeToUrlMap[prompt.type] || "/chat";
        prompt.categories.forEach((category) => {
          const menuCategory =
            menuCategories[category] || menuCategories["other"];
          // Skip if this is a group or divider type category
          if (menuCategory.type === "divider" || menuCategory.type === "group")
            return;

          menuCategory.children.push({
            key: category + "-" + prompt.identifier,
            label: (
              <Link
                href={`${url}?prompt=${prompt.identifier}`}
                className="submenu-entry"
              >
                {prompt.grounded && (
                  <RiGlobalLine
                    style={{
                      marginTop: "-2px",
                      marginRight: "4px",
                      fontSize: "0.8rem",
                      verticalAlign: "middle",
                    }}
                  />
                )}
                {prompt.title}
              </Link>
            ),
          });
        });
      });

    const finalMenuItems = [];
    Object.keys(menuCategories).forEach((key) => {
      // Handle divider or group type categories
      if (
        menuCategories[key].type === "divider" ||
        menuCategories[key].type === "group"
      ) {
        finalMenuItems.push(menuCategories[key]);
      } else if (!menuCategories[key].children) {
        finalMenuItems.push(menuCategories[key]);
      } else if (menuCategories[key].children.length > 0) {
        menuCategories[key].children.sort((a, b) => {
          const aText = Array.isArray(a.label.props.children)
            ? a.label.props.children[a.label.props.children.length - 1]
            : a.label.props.children;
          const bText = Array.isArray(b.label.props.children)
            ? b.label.props.children[b.label.props.children.length - 1]
            : b.label.props.children;
          return aText.localeCompare(bText);
        });
        finalMenuItems.push(menuCategories[key]);
      }
    });

    setMenuItems(finalMenuItems);
  }, [prompts]);

  return (
    <Menu
      theme="light"
      mode="inline"
      className="sidebar"
      items={menuItems}
      defaultSelectedKeys={[currentSelectedKey]}
    ></Menu>
  );
};

export default Sidebar;
