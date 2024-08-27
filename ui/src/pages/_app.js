// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { useEffect, useState } from "react";
import { Layout, ConfigProvider } from "antd";
import Head from "next/head";
import Header from "./_header";
import "../styles/globals.css";
import Sidebar from "./_sidebar";

import { getPrompts, getContextSnippets, getDocuments } from "../app/_boba_api";

export default function App({
  Component,
  pageProps: { session, ...pageProps },
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState();

  const [prompts, setPrompts] = useState([]);
  const [contexts, setContexts] = useState([]);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    getPrompts(setPrompts);
    getContextSnippets((data) => {
      const labelValuePairs = data.map((context) => {
        const contextCopy = { ...context };
        if (context.context === "base") {
          contextCopy.label = "none";
          contextCopy.value = "base";

          return contextCopy;
        } else {
          contextCopy.label = context.context;
          contextCopy.value = context.context;

          return contextCopy;
        }
      });
      setContexts(labelValuePairs);
    });
    getDocuments(setDocuments);
  }, []);

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
              width={250}
            >
              <Sidebar
                selectedKey={selectedKey}
                collapse={true}
                prompts={prompts}
              />
            </Layout.Sider>
            <Layout.Content style={{ margin: 0, background: "white" }}>
              <Component
                {...pageProps}
                prompts={prompts}
                contexts={contexts}
                documents={documents}
              />
            </Layout.Content>
          </Layout>
        </Layout>
      </ConfigProvider>
    </>
  );
}
