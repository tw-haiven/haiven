// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import { initialiseMenuCategoriesForSidebar } from "../app/_navigation_items";

import { RiChat2Line } from "react-icons/ri";

const Sidebar = ({ prompts }) => {
  const pathToKey = {
    "/scenarios": "scenarios",
    "/creative-matrix": "creative-matrix",
    "/threat-modelling": "threat-modelling",
    "/requirements": "requirements",
    "/story-validation": "story-validation",
    "/knowledge-chat": "knowledgeChat",
    "/": "dashboard",
  };
  const router = useRouter();
  const currentSelectedKey = pathToKey[router.pathname];

  const [menuItems, setMenuItems] = useState([]);

  useEffect(() => {
    const menuCategories = initialiseMenuCategoriesForSidebar();

    prompts.forEach((prompt) => {
      prompt.categories.forEach((category) => {
        const menuCategory =
          menuCategories[category] || menuCategories["other"];
        menuCategory.children.push({
          key: category + "-" + prompt.identifier,
          label: (
            <Link
              href={"/chat?prompt=" + prompt.identifier}
              className="submenu-entry"
            >
              {prompt.title}
            </Link>
          ),
        });
      });
    });

    const finalMenuItems = [];
    Object.keys(menuCategories).forEach((key) => {
      if (!menuCategories[key].children) {
        finalMenuItems.push(menuCategories[key]);
      } else if (menuCategories[key].children.length > 0) {
        menuCategories[key].children.sort((a, b) => {
          return a.label.props.children.localeCompare(b.label.props.children);
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
      style={{ paddingTop: 10 }}
      items={menuItems}
      defaultSelectedKeys={[currentSelectedKey]}
      defaultOpenKeys={["ideate", "analyse"]}
    ></Menu>
  );
};

export default Sidebar;
