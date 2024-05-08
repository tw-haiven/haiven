import { Button, Col, Input, Row, Select } from "antd";
import { use, useState } from "react";
import { AiOutlineDelete } from "react-icons/ai";
export default function Quorum() {
  const [prompt, setPrompt] = useState("");
  const [personas, setPersonas] = useState([
    {
      name: "Blue Hat",
      prompt:
        "You are a thoughtful facilitator. Your role is to manage the thinking process and guide the discussion. Set the agenda, summarize discussions, or direct the conversation towards specific goals.",
    },
    {
      name: "Green Hat",
      prompt:
        "You are a creative innovator. Your role is to think creatively, generate ideas, and explore alternatives. Offer fresh perspectives, suggest creative solutions, or propose unconventional approaches.",
    },
    {
      name: "Red Hat",
      prompt:
        "You are an intuitive feeler. Your role is to express emotions, intuitions, and gut reactions. Share your feelings and instincts about the situation or ask others about their emotional responses.",
    },
    {
      name: "Yellow Hat",
      prompt:
        "You are an optimistic visionary. Your role is to explore possibilities, benefits, and opportunities. Highlight positive aspects, propose solutions, or envision positive outcomes.",
    },
    {
      name: "Black Hat",
      prompt:
        "You are a critical analyzer. Your role is to identify potential risks, weaknesses, and flaws. Present arguments or raise concerns based on logical reasoning and critical thinking.",
    },
    {
      name: "White Hat",
      prompt:
        "You are a the neutral observer. Your role is to focus on facts and information. Share relevant data or ask questions to gather more information about the topic at hand.",
    },
  ]);

  const addPersona = () => {
    setPersonas([
      ...personas,
      {
        name: `Persona ${personas.length + 1}`,
        prompt: `Persona ${personas.length + 1} prompt`,
      },
    ]);
  };

  const deletePersona = (index) => {
    if (personas.length === 1) return;
    setPersonas(personas.filter((persona, i) => i !== index));
  };

  const generatePrompt = () => {};

  return (
    <div id="canvas" style={{ paddingRight: 10 }}>
      <h1 style={{ marginTop: 0 }}>
        Quorum&nbsp;&nbsp;
        <Select defaultValue="1" onChange={() => {}}>
          <Select.Option value="1">Template: 6 Thinking Hats</Select.Option>
          <Select.Option value="2">Template: 4 Lenses</Select.Option>
        </Select>
      </h1>
      <b>Prompt</b>
      <Input placeholder="Enter a prompt for the personas" value={prompt} />
      <br />
      <br />
      <b>Personas</b>&nbsp;&nbsp;
      <Button size="small" onClick={addPersona}>
        Add Persona
      </Button>
      <br />
      <br />
      <Row gutter={[16, 16]}>
        {personas.map((persona, index) => {
          return (
            <Col key={index} span={4}>
              Persona {index + 1}
              <Button
                size="small"
                style={{ float: "right" }}
                onClick={() => deletePersona(index)}
              >
                <AiOutlineDelete />
              </Button>
              <Input
                key={index}
                value={persona.name}
                style={{ marginBottom: 5 }}
              />
              <Input.TextArea key={index} value={persona.prompt} rows={8} />
            </Col>
          );
        })}
      </Row>
      <br />
      <Row>
        <Col span={24}>
          <b>Facilitation model</b>&nbsp;&nbsp;
          <Select defaultValue="1" onChange={() => {}}>
            <Select.Option value="1">
              Initial Ideas (blue, white, green blue)
            </Select.Option>
            <Select.Option value="2">
              Choosing between alternatives (blue, white, yellow, black, red,
              blue)
            </Select.Option>
          </Select>
        </Col>
        <Col span={24}>
          <Input.TextArea rows={1} autoSize style={{ marginTop: 10 }} />
        </Col>
      </Row>
    </div>
  );
}
