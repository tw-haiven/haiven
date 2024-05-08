import React, { useState } from "react";
import {
  Drawer,
  Card,
  Input,
  Select,
  Spin,
  Checkbox,
  Button,
  Radio,
  Space,
} from "antd";
import CompanyDashboard from "./_company-dashboard";
import { parse } from "best-effort-json-parser";
const { Search } = Input;

const Signals = ({ setSelectedKey }) => {
  let [company, setCompany] = useState({});
  const [isLoading, setLoading] = useState(false);

  function handleSelectChange(value) {
    setLoading(false);
  }

  const onSubmitPrompt = (value, event) => {
    setLoading(true);

    const uri = "/api/analyze-company?input=" + encodeURIComponent(value);

    const ctrl = new AbortController();
    let ms = "";
    let isLoadingXhr = true;
    let output = [];
    try {
      fetchEventSource(uri, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        openWhenHidden: true,
        signal: ctrl.signal,
        onmessage: (event) => {
          if (!isLoadingXhr) {
            console.log("is loading xhr", isLoadingXhr);
            return;
          }
          if (event.data == "[DONE]") {
            setLoading(false);
            isLoadingXhr = false;
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try {
            output = parse(ms || "[]");
          } catch (error) {
            console.log("error", error);
          }
          console.log("company", output);
          setCompany(output);
        },
      });
    } catch (error) {
      setLoading(false);
      isLoadingXhr = false;
      console.log("error", error);
    }
  };

  return (
    <>
      {/* <Radio.Group onChange={() => {}} defaultValue="grid" style={{marginLeft: 10, position: 'absolute', top: 15, right: 15}}>
        <Radio.Button value="grid"><AiOutlineShop style={{display: 'inline-block', verticalAlign: 'middle', height: 14}}/> Business Snapshot</Radio.Button>
        <Radio.Button value="list"><AiOutlineAim style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Organization vision &amp; priorities</Radio.Button>
        <Radio.Button value="stack"><AiOutlineExperiment style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Domain</Radio.Button>
        <Radio.Button value="stack"><AiOutlineCluster style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Competitors</Radio.Button>
      </Radio.Group> */}
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: "inline-block" }}>Companies</b>
          <br />
          <br />
          Analysis Type{" "}
          <Select
            defaultValue={"company"}
            onChange={handleSelectChange}
            style={{ width: 200 }}
            disabled={isLoading}
            options={[
              { value: "company", label: "Company Brief" },
              { value: "domain", label: "Domain Analysis" },
              { value: "competitor", label: "Competitor Analysis" },
              { value: "industry", label: "Industry/Trends Analysis" },
              { value: "industry", label: "Full/Combined Analysis" },
            ]}
          ></Select>
          &nbsp;&nbsp;&nbsp;
          <span style={{ marginTop: 7, display: "inline-block" }}>
            Analysis prompt:
          </span>
          &nbsp;
          <Search
            placeholder="enter company name and press enter to analyze"
            onSearch={onSubmitPrompt}
            style={{ width: 500, color: "white" }}
            disabled={isLoading}
            enterButton={
              <div>
                <span>Go</span>
              </div>
            }
          />
          &nbsp;
          {isLoading ? <Spin /> : <></>}
        </div>

        <CompanyDashboard company={company} />
      </div>
    </>
  );
};

export default Signals;
