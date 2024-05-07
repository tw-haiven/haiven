import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from "next/router";
import { Drawer, Card, Input, Select, Spin, Checkbox, Button, Radio, Space } from 'antd';
import ScenariosPlot from './_plot';
import ChatExploration from './_chat_exploration';
import {parse} from 'best-effort-json-parser';
// import parse from 'partial-json-parser';
const { Search } = Input;
import { AiOutlineBorderInner, AiOutlineGroup, AiOutlineTable, AiOutlineOneToOne, AiOutlineMenu } from "react-icons/ai";

const SelectedItemsMenu = ({selections, items, onClickBrainstormStrategies, onClickCreateStoryboard}) => {
  return <div className="selected-items-menu">
    <span>
      {selections.length} of {items.length} scenarios selected: 
    </span>&nbsp;
    <Space wrap>
      <Button type="primary" onClick={onClickBrainstormStrategies}>Brainstorm strategies and questions</Button>
      {selections.length == 1 && <Button type="primary" onClick={onClickCreateStoryboard}>Create a storyboard for this scenario</Button>}
      </Space>
  </div>;
}

let ctrl;

const Home = () => {
  const [numOfScenarios, setNumOfScenarios] = useState('5');
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [selections, setSelections] = useState([])
  const [displayMode, setDisplayMode] = useState('grid')
  const [prompt, setPrompt] = useState('');
  const [timeHorizon, setTimeHorizon] = useState('5 years');
  const [optimism, setOptimism] = useState('optimistic');
  const [realism, setRealism] = useState('scifi');
  const [strangeness, setStrangeness] = useState('neutral');
  const [voice, setVoice] = useState('serious');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState('Explore scenario');
  const [chatContext, setChatContext] = useState({});
  const router = useRouter();

  function abortLoad(){
    ctrl && ctrl.abort();
    setLoading(false);
  }

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    setLoading(false);
  }

  function handleSelectTimeHorizonChange(value) {
    setTimeHorizon(value);
    setLoading(false);
  }

  function handleSelectOptimismChange(value) {
    setOptimism(value);
    setLoading(false);
  }

  function handleSelectRealismChange(value) {
    setRealism(value);
    setLoading(false);
  }

  const onExplore = (id) => {
    setDrawerTitle("Explore scenario: " + scenarios[id].title)
    setChatContext({id: id, originalPrompt: prompt, type: 'scenario', ...scenarios[id]})
    setDrawerOpen(true);
  }

  const onClickBrainstormStrategies = () => {
    const scenariosParams = selections.map((selectedIndex) => {
      // console.log("i", selectedIndex);
      const scenario = scenarios[selectedIndex];
      // console.log("s", scenario);
      return "scenarios=" + encodeURIComponent(scenario.title+": "+scenario.summary)
    });
    const url = "/strategies?strategic_prompt="+encodeURIComponent(prompt)+"&"+scenariosParams.join('&');
    window.open(url, '_blank', 'noreferrer');
  }

  const onClickCreateStoryboard = () => {
    const scenario = scenarios[selections[0]];
    const url = "/storyboard?prompt=" + encodeURIComponent(scenario.title+": "+scenario.summary)
    window.open(url, '_blank', 'noreferrer');
  }

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
    if(event.target.checked)
      setDisplayMode('list');
    else
      setDisplayMode('grid');
  }

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  }

  const onScenarioSelectChanged = (index) => {
    return (event) => {
      console.log("event for " + index, event);
      console.log((event.target.checked ? "selected" : "deselected") + " scenario", scenarios[index]);
      if(event.target.checked && selections.indexOf(index) == -1)
        setSelections([...selections, index]);
      else
        setSelections(selections.filter(s => s != index))
    }
  }

  const onSubmitPrompt = (value, event) => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setPrompt(value);
    setSelections([]);

    const uri = '/api/make-questions?input='+encodeURIComponent(value)
              +'&num_questions=' + numOfScenarios;

    let ms = '';
    let isLoadingXhr = true;
    let output = [];
    try {
      fetchEventSource(uri, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', },
        openWhenHidden: true,
        signal: ctrl.signal,
        onmessage: (event) => {
          if(!isLoadingXhr) {
            console.log("is loading xhr", isLoadingXhr);
            return;
          }
          if(event.data == '[DONE]') {
            setLoading(false);
            isLoadingXhr = false;
            abortLoad();
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try { output = parse(ms || '[]'); }
          catch (error) { console.log("error", error) };
          setScenarios(output);
        },
        onerror: (error) => {
          console.log('error', error);
          setLoading(false);
          isLoadingXhr = false;
          abortLoad();
        }
      });
    } catch (error) {
      console.log('error', error);
      setLoading(false);
      isLoadingXhr = false;
      abortLoad();
    }
  }

  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
  const promptRef = useRef();
  const [initialLoadDone, setInitialLoad] = useState(false);

  useEffect(() => {
    if(!initialStrategicPrompt) return;
    if(!router.isReady) return;
    if(initialLoadDone) return;
    setPrompt(initialStrategicPrompt);
    setInitialLoad(true);
  })

  return (
    <>
      <Drawer title={drawerTitle} mask={false} open={drawerOpen} onClose={()=>setDrawerOpen(false)}>
        <ChatExploration context={chatContext} />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <b style={{fontSize: 20, display: 'inline-block'}}>Scenarios</b>
          &nbsp;
          <Radio.Group onChange={onSelectDisplayMode} defaultValue="grid" value={displayMode} style={{float: 'right'}}>
            <Radio.Button value="grid"><AiOutlineGroup style={{display: 'inline-block', verticalAlign: 'middle', height: 14}}/> Cards</Radio.Button>
            <Radio.Button value="list"><AiOutlineOneToOne style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Full Cards</Radio.Button>
            <Radio.Button value="stack"><AiOutlineMenu style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Stack</Radio.Button>
            <Radio.Button value="table"><AiOutlineTable style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Table</Radio.Button>
            <Radio.Button value="plot"><AiOutlineBorderInner style={{display: 'inline-block', verticalAlign: 'middle', height: 14}} /> Matrix</Radio.Button>
          </Radio.Group>
          <br /><br />
          Your question:&nbsp;
          <Search ref={promptRef} placeholder="eg How might we...?" className="fs-unmask"
            onSearch={onSubmitPrompt} style={{ width: 500, color: 'white' }}
            disabled={isLoading} value={prompt} onChange={(e,v)=> {setPrompt(e.target.value)}} enterButton={
              <div>
                <span>Go</span>
              </div>}
          />
          &nbsp;
          Generate <Select defaultValue={'5'} onChange={handleSelectChange} style={{ width: 150 }} disabled={isLoading}
            options={[
              { value: '5', label: '5 questions' },
              { value: '10', label: '10 questions' },
              { value: '15', label: '15 questions' },
            ]}>
          </Select>
          &nbsp;
          {isLoading ? <Spin /> : <></>}
          
          {isLoading && <Button type="primary" danger onClick={abortLoad}>Stop</Button>}

          <br/><br />
          {selections.length > 0 && <SelectedItemsMenu selections={selections} items={scenarios} onClickBrainstormStrategies={onClickBrainstormStrategies} onClickCreateStoryboard={onClickCreateStoryboard}/>}
        </div>
        
        <div className={'scenarios-collection ' + displayMode + '-display'}>
          {scenarios.map((scenario, i) => {
            return <Card key={i} className="scenario" title={
              <>
                {scenario.persona_name}
              </>
            }>
              <div className="scenario-card-content">
                {scenario.questions && scenario.questions.map((q, i) => {
                  return <>
                    <div key={i} className="scenario-question">
                      <Checkbox onChange={onScenarioSelectChanged(i)} checked={selections.indexOf(i) != -1}>
                        {q}
                      </Checkbox>
                    </div>
                  </>
                })}
              </div>
            </Card>
          })}
        </div>

        <div className="scenarios-plot-container" style={{display: displayMode == 'plot' ? 'block' : 'none'}}>
          <ScenariosPlot scenarios={scenarios} visible={displayMode == 'plot'}/>
        </div>
        
      </div>
    </>
  );
};

export default Home;