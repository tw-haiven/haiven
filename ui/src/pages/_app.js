// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { Layout, ConfigProvider } from "antd";
import Head from "next/head";
import Header from "./_header";
import "../styles/globals.css";
import { useState } from "react";
import Sidebar from "./_sidebar";

export default function App({
  Component,
  pageProps: { session, ...pageProps },
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState();

  const useLayout = true;

  return (
    <>
      <ConfigProvider
        // https://ant.design/docs/react/customize-theme#api
        theme={{
          token: {
            // Seed Token
            borderRadius: 0,

            colorPrimary: "#003d4f",
            colorError: "#f2617aff",
            colorWarning: "#CC850A",
            colorSuccess: "#6B9E78",
            colorLink: "#f2617aff",

            fontFamilyCode: "Inter, Noto Sans SC, sans-serif",

            lineType: "none",
            motion: "false",
            // Alias Token
            colorBgContainer: "#edf1f3",
          },
          components: {
            Menu: {
              itemHeight: "30px",
            },
          },
        }}
      >
        <Head>
          <title>Haiven</title>
        </Head>
        {useLayout && (
          <Layout style={{ minHeight: "100vh" }}>
            <Layout.Header
              style={{
                position: "sticky",
                margin: 0,
                padding: 0,
                top: 0,
                zIndex: 1,
                width: "100%",
              }}
            >
              <Header />
            </Layout.Header>
            <Layout style={{ minHeight: "100vh" }}>
              <Layout.Sider
                theme="light"
                collapsible
                collapsed={collapsed}
                onCollapse={(value) => setCollapsed(value)}
                style={{ height: "100vh" }}
              >
                <Sidebar selectedKey={selectedKey} collapse={true} />
              </Layout.Sider>
              <Layout.Content style={{ margin: 0, background: "white" }}>
                <Component {...pageProps} />
              </Layout.Content>
            </Layout>
          </Layout>
        )}
        {!useLayout && <Component {...pageProps} />}
      </ConfigProvider>
    </>
  );
}
