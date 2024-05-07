import { useRouter } from "next/router";
import React, { useEffect, useState } from 'react';
import { Drawer, Card, Input, Select, Spin, Button, Radio, Space } from 'antd';
import ChatExploration from './_chat_exploration';
import {parse} from 'best-effort-json-parser';
const { Search } = Input;
import { AiOutlineBorderInner, AiOutlineGroup, AiOutlineTable, AiOutlineOneToOne, AiOutlineMenu, AiOutlineDelete } from "react-icons/ai";

const SelectedItemsMenu = ({ selections, items, onClickTestStrategies }) => {
  return <div className="selected-items-menu">
    <span>
      {selections.length} of {items.length} strategies selected:
    </span>&nbsp;
    <Space wrap>
      {/* <Button type="primary">Bookmark</Button> */}
      {/* {selections.length > 1 && <Button type="primary">Combine</Button>} */}
      <Button type="primary" onClick={onClickTestStrategies}>Evaluate selected strategies</Button>
    </Space>
  </div>;
}

const SelectSubPrompt = () => {
  return (
    <Select defaultValue="scenario">
      <Select.Option value="scenario">Future scenario</Select.Option>
      <Select.Option value="question">Answers question</Select.Option>
    </Select>
  );
}

let ctrl;

const Home = () => {
  const [numOfScenarios, setNumOfScenarios] = useState('3');
  const [numOfQuestions, setNumOfQuestions] = useState('3');
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [selections, setSelections] = useState([]);
  const [displayMode, setDisplayMode] = useState('grid');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState('Explore scenario');
  const [chatContext, setChatContext] = useState({});
  const [prompt, setPrompt] = useState('');
  const [subprompts, setSubprompts] = useState([]);
  const [answersVisible, setAnswersVisible] = useState(true);
  const [savedIdeas, setSavedIdeas] = useState([]);
  
  function abortLoad(){
    ctrl && ctrl.abort();
    setLoading(false);
  }

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    setLoading(false);
  }

  function handleSelectNumOfQuestionsChange(value) {
    setNumOfQuestions(value);
    setLoading(false);
  }

  const onExplore = (id) => {
    setDrawerTitle("Explore strategy: " + scenarios.strategies[id].title)
    setChatContext({id: id, originalPrompt: prompt, type: 'strategy', ...scenarios.strategies[id]})
    setDrawerOpen(true);
  }

  const onSave = async (id) => {
    const scenario = scenarios.strategies[id];
    const body = scenario;
    body.prompt = prompt;
    body.type = 'strategy';
    const resp = await fetch('/api/save-idea', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    const data = await resp.json();
    setSavedIdeas([...savedIdeas, id]);
    console.log("Saved idea", data);
  }

  const onClickTestStrategies = () => {
    const strategiesParams = selections.map((i) => {
      const strat = scenarios?.strategies[i];
      return "strategies=" + encodeURIComponent(JSON.stringify(strat))
    });
    const scenariosParams = subprompts.map((s) => "scenarios=" + encodeURIComponent(JSON.stringify({
      title: s.text
    })));
    console.log("strategiesParams", strategiesParams);
    console.log("scenariosParams", scenariosParams);
    const url = "/test-strategies?" + scenariosParams.join('&') + '&' + strategiesParams.join('&');
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
      if (event.target.checked && selections.indexOf(index) == -1)
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

    const scenarioSubpromptParams = subprompts.map((subprompt, i) => {
      return 'scenario_subprompts=' + encodeURIComponent(subprompt.text);
    });
    const uri = '/api/strategize?input=' + encodeURIComponent(value)
      + '&' + scenarioSubpromptParams.join('&')
      + '&num_strategies=' + encodeURIComponent(numOfScenarios)
      + '&num_questions=' + encodeURIComponent(numOfQuestions);

    console.log("uri", uri);

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
          if (!isLoadingXhr) {
            console.log("is loading xhr", isLoadingXhr);
            return;
          }
          if (event.data == '[DONE]') {
            setLoading(false);
            isLoadingXhr = false;
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try { output = parse(ms || '[]'); }
          catch (error) { console.log("error", error) };
          // if(!Array.isArray(output))
          //   output = [output]
          // console.log("setting output", output);
          setScenarios(output);
        },
        onerror: (error) => {
          console.log('error', error);
          setLoading(false);
          isLoadingXhr = false;
          ctrl.abort();
        }
      });
    } catch (error) {
      console.log('error', error);
      setLoading(false);
      isLoadingXhr = false;
      ctrl.abort();
    }
  }

  const deleteSubprompt = (index) => {
    return (event) => {
      console.log("delete subprompt #", index)
      let newSubprompts = subprompts.filter((s,i) => { 
        console.log("filter", i);
        return i != index;
      })
      console.log("new subprompts", newSubprompts);
      setSubprompts(newSubprompts);
    }
  }

  const onSubpromptChanged = (index) => {
    return (event) => {
      console.log("subprompt changed", index);
      const newSubprompts = [...subprompts];
      newSubprompts[index].text = event.target.value;
      setSubprompts(newSubprompts);
    }
  }

  const onAddSubprompt = () => {
    setSubprompts([...subprompts, { type: 'scenario', text: '' }])
  }

  const toggleAnswers = () => {
    setAnswersVisible(!answersVisible);
  };

  const router = useRouter();
  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
  let initialScenarios = params.scenarios;
  if(!Array.isArray(initialScenarios) && typeof initialScenarios === 'string') initialScenarios = [initialScenarios];
  const [initialLoadDone, setInitialLoad] = useState(false);

  useEffect(() => {
    if(!router.isReady) return;
    if(initialLoadDone) return;
    if(initialStrategicPrompt)
      setPrompt(initialStrategicPrompt);
    if(initialScenarios) {
      console.log("initialscenarios", initialScenarios)
      const initialSubprompts = initialScenarios.map((s) => {
        return { type: 'scenario', text: s }
      });
      setSubprompts(initialSubprompts);
    }
    setInitialLoad(true);
  })

  // console.log("scenarios", scenarios);

  return (

    <>
      <Drawer title={drawerTitle} mask={false} open={drawerOpen} onClose={()=>setDrawerOpen(false)}>
        <ChatExploration context={chatContext} />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: 'inline-block' }}>Strategies</b>
          &nbsp;
          <Radio.Group onChange={onSelectDisplayMode} defaultValue="grid" style={{ float: 'right' }}>
            <Radio.Button value="grid"><AiOutlineGroup style={{ display: 'inline-block', verticalAlign: 'middle', height: 14 }} /> Cards</Radio.Button>
            <Radio.Button value="list"><AiOutlineOneToOne style={{ display: 'inline-block', verticalAlign: 'middle', height: 14 }} /> Full Cards</Radio.Button>
            <Radio.Button value="stack"><AiOutlineMenu style={{ display: 'inline-block', verticalAlign: 'middle', height: 14 }} /> Stack</Radio.Button>
            <Radio.Button value="table"><AiOutlineTable style={{ display: 'inline-block', verticalAlign: 'middle', height: 14 }} /> Table</Radio.Button>
            <Radio.Button value="plot"><AiOutlineBorderInner style={{ display: 'inline-block', verticalAlign: 'middle', height: 14 }} /> Matrix</Radio.Button>
          </Radio.Group>

          <br /><br />

          <div style={{ display: 'inline' }}>
            <Select defaultValue={'scenario'} style={{ width: 180 }} disabled={true}
              options={[
                { value: 'scenario', label: 'Strategic prompt', disabled: true }
              ]}>
            </Select>
            <Search placeholder="enter a prompt and press enter to generate strategies"
              value={prompt} onChange={(e,v)=> {setPrompt(e.target.value)}}
              onSearch={onSubmitPrompt} style={{ width: 500, color: 'white', marginLeft: 10 }}
              disabled={isLoading} enterButton={
                <div>
                  <span>Go</span>
                </div>}
            />
          </div>

          &nbsp;
          Generate <Select defaultValue={'3'} onChange={handleSelectNumOfQuestionsChange} style={{ width: 150 }} disabled={isLoading}
            options={[
              { value: '3', label: '3 questions' },
              { value: '5', label: '5 questions' },
              { value: '10', label: '10 questions' },
            ]}>
          </Select>&nbsp; and &nbsp;
          <Select defaultValue={'3'} onChange={handleSelectChange} style={{ width: 150 }} disabled={isLoading}
            options={[
              { value: '1', label: '1 strategy' },
              { value: '3', label: '3 strategies' },
              { value: '5', label: '5 strategies' },
              { value: '10', label: '10 strategies' },
            ]}>
          </Select>
          &nbsp;&nbsp;

          {isLoading ? <Spin /> : <></>}<br />

          {subprompts.map((x,i) => {
            return (<div key={'subprompt-'+i} style={{ marginTop: 5 }}>
              <Select key={'select-'+x} defaultValue={'scenario'} value={x.type} onChange={handleSelectChange} style={{ width: 180 }} disabled={isLoading}
                options={[
                  { value: 'scenario', label: 'Future scenario' },
                  { value: 'question', label: 'Answers question' },
                ]}>
              </Select>
              <Input  key={'input-'+x} style={{ width: 500, marginLeft: 10 }} placeholder="enter a potential future scenario" value={x.text} onChange={onSubpromptChanged(i)} disabled={isLoading}/>&nbsp;
              <Button  key={'button-'+x} type="text" danger onClick={deleteSubprompt(i)} disabled={isLoading}><AiOutlineDelete style={{display: 'inline-block', verticalAlign: 'middle' }} /></Button>
            </div>)
          })}
          
          <Button style={{marginTop: 5, width: 180}} onClick={onAddSubprompt} disabled={isLoading}>Add subprompt</Button>

          {isLoading && <Button type="primary" danger onClick={abortLoad} style={{marginLeft: 10}}>Stop</Button>}

          <br /><br />
          {selections.length > 0 && <SelectedItemsMenu selections={selections} items={scenarios} onClickTestStrategies={onClickTestStrategies} />}
        </div>
        {/* END PROMPT CENTER */}

        {scenarios && scenarios.questions && 
          <div className={'scenarios-collection ' + displayMode + '-display'}>
            <Card key={-1} className="scenario" title={
              <>
                Questions&nbsp;
                <span className="toggle-answers">
                  <Button type="link" onClick={toggleAnswers}><small>toggle examples</small></Button>
                </span>
              </>
            } actions={[]}>
            {scenarios?.questions?.map((scenario, i) => {
              return <div key={i} className="card-prop stackable" style={{marginBottom: 20, width: 200}}>
                <div className="card-prop-value">
                  {i+1}. <b>{scenario.question}</b>
                  {answersVisible && scenario.answer && scenario.answer.length > 0 && <small>({scenario.answer})</small>}
                </div>
              </div>
            })}
            </Card>

          {scenarios?.strategies?.map((scenario, i) => {
            return <Card key={i} className="scenario" title={
              <>
                {scenario.title}
              </>
            } actions={[
              <input key={'cb'+i} type="checkbox" className="select-scenario" onChange={onScenarioSelectChanged(i)} />,
              <Button type="link" key="explore" onClick={() => onExplore(i)}>Explore</Button>, 
              <>
                {savedIdeas.includes(i) && <Button type="link" key="saved" onClick={() => onSave(i)} style={{padding: 0}}>Saved</Button>}
                {!savedIdeas.includes(i) && <Button type="link" key="save" onClick={() => onSave(i)} style={{padding: 0}}>Save</Button>}
              </>
            ]}>
              <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">Winning aspiration</div>
                <div className="card-prop-value">{scenario.winning_aspiration}</div>
              </div>
              <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">Problem diagnosis</div>
                <div className="card-prop-value">{scenario.problem_diagnosis}</div>
              </div>
              <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">Where to play</div>
                <div className="card-prop-value">{scenario.where_to_play}</div>
              </div>
              <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">How to win</div>
                <div className="card-prop-value">{scenario.how_to_win}</div>
              </div>
              {/* <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">Key capabilities needed</div>
                <div className="card-prop-value">{scenario.key_capabilities}</div>
              </div> */}
              <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">What would have to be true?</div>
                <div className="card-prop-value">{scenario.assumptions}</div>
              </div>
            </Card>
          })}
          </div>
        }

        <div className="scenarios-plot-container" style={{ display: displayMode == 'plot' ? 'block' : 'none' }}>
          {/* <ScenariosPlot scenarios={scenarios} visible={displayMode == 'plot'} /> */}
        </div>

      </div>
    </>
  );
};

export default Home;
