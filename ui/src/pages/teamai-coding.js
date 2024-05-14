import React, { useEffect, useState, useRef } from "react";
import { Helmet } from "react-helmet";
const GradioApp = () => (
  <gradio-app src="http://localhost:8080/coding"></gradio-app>
);

const Home = () => {
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

        <GradioApp></GradioApp>
      </div>
    </>
  );
};
export default Home;
