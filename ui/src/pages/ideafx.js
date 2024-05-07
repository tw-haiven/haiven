import { Row, Col, Input, Button } from "antd";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Ideafx() {
  const [agentResponse, setAgentResponse] = useState("");
  const [userInput, setUserInput] = useState("");

  const run = async () => {
    const stream = await fetch(`/api/ideafx?input=${encodeURIComponent(userInput)}`);
    const reader = stream.body.getReader();
    let result = '';
    while(true) {
      const { done, value } = await reader.read();
      if(done) break;
      result += new TextDecoder("utf-8").decode(value);
      setAgentResponse(result);
    }
  }

  return (
    <div style={{paddingLeft: 10, paddingRight: 10}}>
      <h1>Idea FX</h1>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <p><Input.TextArea rows={8} autoSize onChange={e => setUserInput(e.target.value)} value={userInput}/></p>
          <Button type="primary" onClick={run}>Run</Button>
        </Col>
        <Col span={12}>
          <ReactMarkdown>{agentResponse}</ReactMarkdown>
        </Col>
      </Row>
      <Row>
      </Row>
    </div>
  );
}
