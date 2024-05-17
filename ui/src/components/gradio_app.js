import { Helmet } from "react-helmet";
import React, { useEffect } from "react";

const getBaseUrl = () => {
  const parsedUrl = new URL(window.location.href);
  return `${parsedUrl.protocol}//${parsedUrl.hostname}${parsedUrl.port ? `:${parsedUrl.port}` : ""}`;
};

const GradioApp = ({ pagePath }) => {
  useEffect(() => {
    const gradioAppElement = document.querySelector("gradio-app");
    if (gradioAppElement) {
      gradioAppElement.addEventListener("done", () => {
        gradioAppElement.className = "light";
      });
    }
  }, []);

  if (typeof window !== "undefined") {
    let base_url = getBaseUrl() + pagePath;
    return (
      <>
        <div class="teamai-embed">
          <Helmet>
            <script
              type="module"
              src="https://gradio.s3-us-west-2.amazonaws.com/4.31.0/gradio.js"
            ></script>
          </Helmet>
          <Helmet
            style={[
              {
                cssText: `
                   .teamai-embed .main {padding:0px !important;}
                   .teamai-embed .header {display:none !important;}
        `,
              },
            ]}
          />
          <gradio-app src={base_url} class="light"></gradio-app>;
        </div>
      </>
    );
  }
  return <div />;
};

export default GradioApp;
