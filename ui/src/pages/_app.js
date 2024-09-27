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

  const colorlightgray = "#edf1f3";
  const colormediumgray = "#d9dfe1ff";

  const colorflamingo = "#f2617aff";
  const colordarkblue = "#003d4f";
  const colorsapphire = "#47a1ad";
  const coloramethystpurple = "#634F7D";
  const colorjadegreen = "#6B9E78";
  const colorturmericyellow = "#CC850A";
  const colordarkgray = "#666666ff";

  useEffect(() => {
    getPrompts(setPrompts);
    getContextSnippets((data) => {
      const labelValuePairs = data.map((context) => {
        const contextCopy = { ...context };
        if (context.context === "base") {
          contextCopy.label = "None";
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
    getDocuments((data) => {
      const updatedDocuments = [{ label: "None", value: "base" }, ...data];
      setDocuments(updatedDocuments);
    });
  }, []);

  return (
    <>
      <ConfigProvider
        // https://ant.design/docs/react/customize-theme#api
        theme={{
          token: {
            // Seed Token
            borderRadius: 0,

            colorPrimary: colordarkblue,
            colorError: colorflamingo,
            colorWarning: colorturmericyellow,
            colorSuccess: colorjadegreen,
            colorLink: colorflamingo,

            fontFamilyCode: "Inter, Noto Sans SC, sans-serif",

            lineType: "none",
            motion: "false",
            // Alias Token
            colorBgContainer: colorlightgray,
          },
          components: {
            Menu: {
              itemHeight: "30px",
            },
            Button: {
              defaultBg: colorflamingo,
              defaultColor: "white",
            },
            Tabs: {
              itemColor: colorsapphire,
              inkBarColor: colorsapphire,
              itemActiveColor: colorsapphire,
              itemSelectedColor: colorsapphire,
              lineType: "solid",
            },
          },
        }}
      >
        <Head>
          <title>Haiven</title>
          <meta property="og:image" content="/boba/logohun.jpg" />
          <meta
            property="og:image:url"
            content="https://team-ai-owd2wjctzq-uc.a.run.app/boba/logohun.jpg"
          />
          <meta property="og:title" content="Haiven team assistant" />
          <meta
            property="og:description"
            content="Haiven is your intelligent AI assistant, here to assist you to kick-start your software delivery activities"
          />
          <meta property="og:image:alt" content="haiven" />
          <meta property="og:type" content="website" />
          <meta property="og:image:width" content="1200" />
          <meta property="og:image:height" content="630" />
        </Head>
        <div className="social-preview">
          <img
            className="social-preview-image"
            src="/boba/logohun.jpg"
            alt="haiven"
          />
        </div>
        <Layout
          style={{ height: "100vh", display: "flex", flexDirection: "column" }}
        >
          <Layout.Header
            style={{
              position: "fixed",
              height: "65px",
              padding: 0,
              top: 0,
              zIndex: 20,
              width: "100%",
            }}
          >
            <Header />
          </Layout.Header>
          <Layout style={{ marginTop: "64px", flex: 1, overflow: "hidden" }}>
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
            <Layout.Content style={{ overflow: "auto", background: "white" }}>
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
