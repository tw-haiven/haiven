// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";

import {
  RiApps2AddLine,
  RiGridLine,
  RiKey2Fill,
  RiOrganizationChart,
  RiAedElectrodesLine,
  RiLightbulbLine,
  RiDashboardHorizontalLine,
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

  const menuItems = [
    {
      key: "ideate",
      label: "Ideate",
      icon: <RiLightbulbLine style={{ fontSize: "large" }} />,
      children: [
        {
          key: "creative-matrix",
          label: <Link href="/creative-matrix">Creative Matrix</Link>,
          icon: <RiGridLine />,
        },
        {
          key: "scenarios",
          label: <Link href="/scenarios">Scenario design</Link>,
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
          label: <Link href="/requirements">Breakdown</Link>,
          icon: <RiOrganizationChart />,
        },
        {
          key: "story-validation",
          label: <Link href="/story-validation">Story validation</Link>,
          icon: <RiApps2AddLine />,
        },
        {
          key: "threat-modelling",
          label: <Link href="/threat-modelling">Threat modelling</Link>,
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
