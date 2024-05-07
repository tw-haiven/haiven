import { AiOutlineSend, AiOutlineStop } from 'react-icons/ai';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

import {Input, Space, Button, Affix} from 'antd';

const ctrls = {};
export default function ChatExploration({context}) {
  const item = context || {};
  const [isLoading, setLoading] = useState({});
  const [prompts, setPrompts] = useState({});
  const [outputs, setOutputs] = useState({}); //by id

  const abortLoad = () => {
    console.log('aborting', ctrls);
    Object.values(ctrls).forEach(ctrl => ctrls && ctrl.abort());
    ctrls[item.title] && ctrls[item.title].abort();
    setLoading({});
  }

  const onSend = () => {
    abortLoad();
    let contextParam = encodeURIComponent(item.summary)
    if(context.originalPrompt)
      contextParam = encodeURIComponent("Original prompt: " + context.originalPrompt + "\n\n") + contextParam;
    const uri = '/api/explore-'+item.type+'?input='+encodeURIComponent(prompts[item.title]) + '&context=' + contextParam;
    let ms = '';
    let isLoadingXhr = true;
    setLoading({...isLoading, [item.title]: true});
    let output = '';
    ctrls[item.title] = new AbortController();
    console.log('ctrls', ctrls);
    try {
      fetchEventSource(uri, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', },
        openWhenHidden: true,
        signal: ctrls[item.title].signal,
        onmessage: (event) => {
          if(!isLoadingXhr) {
            return;
          }
          if(event.data == '[DONE]') {
            isLoadingXhr = false;
            abortLoad();
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try { output = ms || ''; }
          catch (error) { console.log("error", error) };
          if(output.startsWith("1. ") || output.startsWith("- "))
            output = "\n" + output;
          setOutputs({...outputs, [item.title]: "**Boba:** " + output});
        },
        onerror: (error) => {
          console.log('error', error);
          setLoading({...isLoading, [item.title]: false});
          isLoadingXhr = false;
          abortLoad();
        }
      });
    } catch (error) {
      console.log('error', error);
      setLoading({...isLoading, [item.title]: false});
      isLoadingXhr = false;
      abortLoad();
    }
  }

  const setPrompt = (prompt) => {
    setPrompts({...prompts, [item.title]: prompt});
  }

  return <div className="chat-exploration">
    <div className="chat-log">
      <div className="chat-message"><b>Boba:</b> In this {item.type}, {item.summary} </div>
      <Space.Compact style={{ width: '100%' }}>
        <Input placeholder="What do you want to know?" 
              value={prompts[item.title]}
              onChange={(e,v) => setPrompts({...prompts, [item.title]: e.target.value})} onPressEnter={onSend} />
        <Button type="primary" onClick={onSend}><AiOutlineSend /></Button>
        {/* {isLoading[item.title] && <Button type="primary" danger onClick={abortLoad}><AiOutlineStop /></Button> } */}
      </Space.Compact>
      
      <div className="chat-message">
        {<div className="prompt-suggestions">
          <Space>
            <Button size='small' onClick={()=>setPrompt('Give me an example')}>Give me an example</Button>
            <Button size='small' onClick={()=>setPrompt('Can you be more specific?')}>Can you be more specific?</Button>
          </Space>
          {item.type === 'scenario' && <Button style={{marginTop: 4}} size='small' onClick={()=>setPrompt('Create a storyboard for this scenario')}>Create a storyboard for this scenario</Button>}
          {item.type === 'strategy' && <Button style={{marginTop: 4}} size='small' onClick={()=>setPrompt('Generate more strategies like this one')}>Generate more strategies like this one</Button>}
          {item.type === 'concept' && <Button style={{marginTop: 4}} size='small' onClick={()=>setPrompt('Give me some questions to explore this concept')}>Give me some questions to explore this concept</Button>}
          {item.type === 'concept' && <Button style={{marginTop: 4}} size='small' onClick={()=>setPrompt('Create a user journey for this concept')}>Create a user journey for this concept</Button>}
        </div>}
        <ReactMarkdown>{outputs[item.title]}</ReactMarkdown>
      </div>
    </div>
  </div>
}
