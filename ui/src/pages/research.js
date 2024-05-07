import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from "next/router";
import { Drawer, Card, Input, Spin, Button, Space } from 'antd';
import ChatExploration from './_article_exploration';
const { Search } = Input;

let ctrl;

const SelectedItemsMenu = ({selections, items, onClickBrainstormStrategies}) => {
  return <div className="selected-items-menu">
    <span>
      {selections.length} of {items.length} articles selected: 
    </span>&nbsp;
    <Space wrap>
      <Button type="primary" onClick={onClickBrainstormStrategies}>Read these articles to answer the research query</Button>
      </Space>
  </div>;
}

const Research = () => {

  const [numOfScenarios, setNumOfScenarios] = useState('3');
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [selections, setSelections] = useState([])
  const [displayMode, setDisplayMode] = useState('grid')
  const [prompt, setPrompt] = useState('');
  const [timeHorizon, setTimeHorizon] = useState('10 years');
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
    setDrawerTitle("Explore article: " + scenarios[id].title)
    setChatContext({id: id, type: 'article', ...scenarios[id]})
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

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
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

  const onSubmitPrompt = async (value, event) => {
    // abortLoad();
    // ctrl = new AbortController();
    // setLoading(true);
    // setPrompt(value);
    // setSelections([]);

    const uri = '/api/research?prompt='+encodeURIComponent(value);
    console.log("fetching", uri);
    // const response = await fetch(uri);
    // const results = await response.json();
    // // waits until the request completes...
    // setScenarios(results.search_results);
    // setLoading(false);
    // console.log("results", results);

    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setPrompt(value);
    setSelections([]);

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
          console.log("got data", data);
          try { 
            output = data; 
          }
          catch (error) { 
            console.log("error", error) 
          };
          console.log("got output", output);
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
        <ChatExploration context={chatContext} type="article" />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <img src="/boba/cbicon.png" style={{ height: 25, display: 'inline-block', verticalAlign: 'top' }} /> 
          &nbsp;&nbsp;<b style={{fontSize: 20, display: 'inline-block'}}>Research: Signals</b>
          <br/><br/>
          <Space>
            <span>Research query:&nbsp;</span>
            <Search ref={promptRef} placeholder="enter a research question or prompt"
              onSearch={onSubmitPrompt} style={{ width: 700, color: 'white' }}
              disabled={isLoading} value={prompt} onChange={(e,v)=> {setPrompt(e.target.value)}} enterButton={
                <div>
                  <span>Go</span>
                </div>}
            />
          </Space>
          
          &nbsp;&nbsp;
            
          {isLoading && <Button type="primary" danger onClick={abortLoad}>Stop</Button>}

          &nbsp;
          {isLoading ? <Spin /> : <></>}
          
          <br/><br />
          {selections.length > 0 && <SelectedItemsMenu selections={selections} items={scenarios} onClickBrainstormStrategies={onClickBrainstormStrategies}/>}
        </div>
        
        <div className={'scenarios-collection ' + displayMode + '-display'}>
          {scenarios.map((scenario, i) => {
            if(!scenario.answer || scenario.answer.includes("don't know"))
              return <></>;
            return <Card key={i} className="scenario" title={
              <>
                <a target="_blank" style={{color: 'black'}} href={scenario.link}>Article: {scenario.title}</a>
              </>
            } actions={[
              // <input key={'cb'+i} type="checkbox" className="select-scenario" onChange={onScenarioSelectChanged(i)} />,
              <Button type="link" key="read"><a style={{color: '#1677ff'}} target="_blank" href={scenario.link}>Source</a></Button>, 
              <Button type="link" key="explore" onClick={() => onExplore(i)}>Explore</Button>, 
              <Button type="text" key="explore">...</Button>, 
              ]}>
              <div className="scenario-card-content" style={{overflow: 'auto'}}>
                  <div>
                    <b>{scenario.date && scenario.date+':'}</b> {scenario.answer? scenario.answer : scenario.snippet}
                  </div><br/>
                  <div><b>Source:</b> <a target="_blank" href={scenario.link}>{scenario.link}</a></div>
              </div>
            </Card>
          })}
        </div>
      
      </div>
    </>
  );
};

export default Research;
