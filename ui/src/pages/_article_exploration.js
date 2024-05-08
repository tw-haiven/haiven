import { AiOutlineSend } from "react-icons/ai";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { Input, Space, Button, Affix } from "antd";

export default function ChatExploration({ context }) {
  const item = context || {};
  // console.log("context", context);
  let ctrl;
  const [isLoading, setLoading] = useState(false);
  const [prompts, setPrompts] = useState({});
  const [outputs, setOutputs] = useState({}); //by id

  const abortLoad = () => {
    ctrl && ctrl.abort();
    setLoading(false);
  };

  const onSend = () => {
    const uri =
      "/api/explore-" +
      item.type +
      "?input=" +
      encodeURIComponent(prompts[item.title]);
    console.log("stringified", JSON.stringify(item));

    let ms = "";
    let isLoadingXhr = true;
    setLoading(true);
    let output = "";
    ctrl = new AbortController();
    try {
      fetchEventSource(uri, {
        method: "POST",
        body: JSON.stringify(context),
        headers: { "Content-Type": "application/json" },
        openWhenHidden: true,
        signal: ctrl.signal,
        onmessage: (event) => {
          if (!isLoadingXhr) {
            return;
          }
          if (event.data == "[DONE]") {
            setLoading(false);
            isLoadingXhr = false;
            abortLoad();
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try {
            output = ms || "";
          } catch (error) {
            console.log("error", error);
          }
          setOutputs({ ...outputs, [item.title]: "**Boba:** " + output });
        },
        onerror: (error) => {
          console.log("error", error);
          setLoading(false);
          isLoadingXhr = false;
          abortLoad();
        },
      });
    } catch (error) {
      console.log("error", error);
      setLoading(false);
      isLoadingXhr = false;
      abortLoad();
    }
  };

  const setPrompt = (prompt) => {
    setPrompts({ ...prompts, [item.title]: prompt });
  };

  function extractDomainName(url) {
    const regex = /^https?:\/\/(?:www\.)?([^:/?#]+)(?:[/:?#]|$)/i;
    const match = (url || "").match(regex);

    return match && match[1];
  }

  return (
    <div className="chat-exploration">
      <div className="chat-log">
        <div className="chat-message">
          Source: <a href={item.link}>{extractDomainName(item.link)}</a>
        </div>
        <div className="chat-message">
          <b>Boba:</b> Based on this {item.type}, {item.answer}{" "}
        </div>
        <Space.Compact style={{ width: "100%" }}>
          <Input
            placeholder="What do you want to know?"
            value={prompts[item.title]}
            onChange={(e, v) =>
              setPrompts({ ...prompts, [item.title]: e.target.value })
            }
            onPressEnter={onSend}
          />
          <Button type="primary" onClick={onSend}>
            <AiOutlineSend />
          </Button>
        </Space.Compact>

        <div className="chat-message">
          {!outputs[item.title] && (
            <div className="prompt-suggestions">
              <Space>
                <Button
                  size="small"
                  onClick={() => setPrompt("Summarize this article")}
                >
                  Summarize this article
                </Button>
                <Button
                  size="small"
                  onClick={() => setPrompt("List the main points")}
                >
                  List the main points
                </Button>
              </Space>
            </div>
          )}
          <ReactMarkdown>{outputs[item.title]}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
