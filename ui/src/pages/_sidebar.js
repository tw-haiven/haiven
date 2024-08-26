// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import { getPrompts } from "../app/_boba_api";

import {
  RiFlaskLine,
  RiLightbulbLine,
  RiCodeBoxLine,
  RiBookReadLine,
  RiChat2Line,
  RiCompasses2Line,
  RiTable2,
} from "react-icons/ri";

const Sidebar = () => {
  const pathToKey = {
    "/scenarios": "scenarios",
    "/creative-matrix": "creative-matrix",
    "/threat-modelling": "threat-modelling",
    "/requirements": "requirements",
    "/story-validation": "story-validation",
  };
  const router = useRouter();
  const currentSelectedKey = pathToKey[router.pathname];

  const [prompts, setPrompts] = useState([]);
  const [menuItems, setMenuItems] = useState([]);

  useEffect(() => {
    getPrompts(setPrompts);
  }, []);

  useEffect(() => {
    const menuCategories = {
      ideate: {
        key: "ideate",
        label: "Ideate",
        icon: <RiLightbulbLine style={{ fontSize: "large" }} />,
        children: [
          {
            key: "creative-matrix",
            label: <Link href="/creative-matrix">Creative Matrix</Link>,
            icon: <RiTable2 />,
          },
          {
            key: "scenarios",
            label: <Link href="/scenarios">Scenario design</Link>,
            icon: <RiTable2 />,
          },
        ],
      },
      analysis: {
        key: "analyse",
        label: "Analyse",
        icon: <RiBookReadLine style={{ fontSize: "large" }} />,
        children: [
          {
            key: "requirements",
            label: <Link href="/requirements">Breakdown</Link>,
            icon: <RiTable2 />,
          },
          {
            key: "story-validation",
            label: <Link href="/story-validation">Story validation</Link>,
            icon: <RiTable2 />,
          },
        ],
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
        children: [
          {
            key: "threat-modelling",
            label: (
              <Link href="/threat-modelling">Threat modelling: STRIDE</Link>
            ),
            icon: <RiTable2 />,
          },
        ],
      },
      other: {
        key: "other",
        label: "Other",
        icon: <RiChat2Line style={{ fontSize: "large" }} />,
        children: [],
      },
    };

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
          icon: <RiChat2Line />,
        });
      });
    });

    const finalMenuItems = [];
    Object.keys(menuCategories).forEach((key) => {
      if (menuCategories[key].children.length > 0) {
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
