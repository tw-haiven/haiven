// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu, MenuItem } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const { SubMenu } = Menu;

import {
  RiApps2AddLine,
  RiGridLine,
  RiKey2Fill,
  RiOrganizationChart,
  RiAedElectrodesLine,
  RiLightbulbLine,
  RiDashboardHorizontalLine,
} from "react-icons/ri";

const Sidebar = ({ selectedKey = "scenarios" }) => {
  const pathToKey = {
    "/scenarios": "scenarios",
    "/creative-matrix": "creative-matrix",
    "/threat-modelling": "threat-modelling",
    "/requirements": "requirements",
    "/story-validation": "story-validation",
  };
  const router = useRouter();
  const currentSelectedKey = pathToKey[router.pathname];

  const menuItems = [
    {
      key: "ideate",
      label: "Ideate",
      icon: <RiLightbulbLine style={{ fontSize: "large" }} />,
      children: [
        {
          key: "creative-matrix",
          label: <a href="/creative-matrix">Creative Matrix</a>,
          icon: <RiGridLine />,
        },
        {
          key: "scenarios",
          label: <a href="/scenarios">Scenario design</a>,
          icon: <RiAedElectrodesLine />,
        },
      ],
    },
    {
      key: "analyse",
      label: "Analyse",
      icon: <RiDashboardHorizontalLine style={{ fontSize: "large" }} />,
      children: [
        {
          key: "requirements",
          label: <a href="/requirements">Breakdown</a>,
          icon: <RiOrganizationChart />,
        },
        {
          key: "story-validation",
          label: <a href="/story-validation">Story validation</a>,
          icon: <RiApps2AddLine />,
        },
        {
          key: "threat-modelling",
          label: <a href="/threat-modelling">Threat modelling</a>,
          icon: <RiKey2Fill />,
        },
      ],
    },
  ];

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
