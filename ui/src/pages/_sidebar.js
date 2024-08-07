// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Menu } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
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
    "/playbook": "playbook",
    "/scenarios": "scenarios",
    "/strategies": "strategies",
    "/concepts": "concepts",
    "/creative-matrix": "creative-matrix",
    "/storyboard": "storyboard",
    "/test-strategies": "tests",
    "/signals": "company-research",
    "/saved-ideas": "saved-ideas",
    "/chat": "chat",
    "/threat-modelling": "threat-modelling",
    "/requirements": "requirements",
    "/story-validation": "story-validation",
  };
  const router = useRouter();
  const currentSelectedKey = pathToKey[router.pathname];
  // TODO: Does this have to change for the "warnKey" and "errorKey" errors to go away?
  // https://ant.design/components/menu#Notes-for-developers
  return (
    <Menu
      theme="light"
      mode="inline"
      className="sidebar"
      style={{ paddingTop: 10 }}
      defaultSelectedKeys={[currentSelectedKey]}
      defaultOpenKeys={[/*'research',*/ "ideate", "analyse"]}
    >
      {/* <SubMenu key="research"
        icon={<AiOutlineDotChart style={{fontSize: 'large'}}/>}
        title="Research"
        >
        <Menu.Item key="customer-research">
          <Link href="/research">
            <AiOutlineDotChart /> Research Signals
          </Link>
        </Menu.Item>
        <Menu.Item key="company-research">
          <Link href="/signals">
            <AiOutlineShop /> Company Research
          </Link>
        </Menu.Item>
      </SubMenu> */}

      <SubMenu
        key="ideate"
        icon={<RiLightbulbLine style={{ fontSize: "large" }} />}
        title="Ideate"
      >
        {
          /* <Menu.Item key="saved-ideas">
          <Link href="/saved-ideas">
            <AiOutlineStar /> Saved Ideas
          </Link>
        </Menu.Item>*/
          <Menu.Item key="creative-matrix">
            <Link href="/creative-matrix">
              <RiGridLine /> Creative Matrix
            </Link>
          </Menu.Item>
        }
        <Menu.Item key="scenarios">
          <Link href="/scenarios">
            <RiAedElectrodesLine /> Scenario design
          </Link>
        </Menu.Item>
        {/* <Menu.Item key="concepts">
          <Link href="/concepts">
            <AiOutlineRocket /> Concept design
          </Link>
        </Menu.Item>
        <Menu.Item key="strategies">
          <Link href="/strategies">
            <AiOutlineBorderInner /> Strategy design
          </Link>
        </Menu.Item>
        <Menu.Item key="tests">
          <Link href="/storyboard">
            <AiOutlinePicture /> Storyboarding
          </Link>
        </Menu.Item> */}
      </SubMenu>

      <SubMenu
        key="analyse"
        icon={<RiDashboardHorizontalLine style={{ fontSize: "large" }} />}
        title="Analyse"
      >
        <Menu.Item key="requirements">
          <Link href="/requirements">
            <RiOrganizationChart /> Breakdown
          </Link>
        </Menu.Item>
        <Menu.Item key="story-validation">
          <Link href="/story-validation">
            <RiApps2AddLine /> Find gaps
          </Link>
        </Menu.Item>
        <Menu.Item key="threat-modelling">
          <Link href="/threat-modelling">
            <RiKey2Fill /> Threat Modelling
          </Link>
        </Menu.Item>
        {/* <Menu.Item key="chat">
          <Link href="/chat">
            <AiOutlineWechat /> Chat
          </Link>
        </Menu.Item> */}
      </SubMenu>
    </Menu>
  );
};

export default Sidebar;
