import { useRouter } from "next/router";
import React, { useEffect, useRef, useState } from 'react';
import { Drawer, Card, Input, Select, Spin, Button, Radio, Space } from 'antd';
import ChatExploration from './_chat_exploration';
import parse from 'partial-json-parser';
const { Search } = Input;
import { AiOutlineBorderInner, AiOutlineGroup, AiOutlineTable, AiOutlineOneToOne, AiOutlineMenu, AiOutlineDelete, AiOutlinePicture, AiOutlineRocket, AiOutlineHeatMap, AiOutlineFormatPainter, AiOutlineEdit } from "react-icons/ai";

const SelectedItemsMenu = ({ selections, items, onClickTestStrategies }) => {
  return <div className="selected-items-menu">
    <span>
      {/* {selections.length} of {items.length} strategies selected: */}
    </span>&nbsp;
    <Space wrap>
      {/* <Button type="primary">Bookmark</Button> */}
      {/* {selections.length > 1 && <Button type="primary">Combine</Button>} */}
      {/* <Button type="primary" onClick={onClickTestStrategies}>Evaluate selected strategies</Button> */}
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

const SceneCardCover = ({ scenario }) => {
  
  const visualPromptRef = useRef(null);
  const [editMode, setEditMode] = useState(false);
  const [visualPromptOverride, setVisualPromptOverride] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const onCancel = () => {
    setEditMode(false);
  }

  const onSave = () => {
    setEditMode(false);
    setIsLoading(true);
    setVisualPromptOverride(visualPromptRef.current.innerText);
    console.log("setting prompt to", visualPromptRef.current.innerText);
  }

  let imageSrc = scenario.visual_prompt ? 
                      '/api/storyboard-img?prompt='+encodeURIComponent(visualPromptOverride || scenario.visual_prompt) : 
                      "/loadingicon.gif"

  return (
    <>
      {editMode && <div className="cover-visual-prompt">
        <b>Change the image prompt:</b>
        <div contentEditable ref={visualPromptRef} suppressContentEditableWarning={true}>{visualPromptOverride || scenario.visual_prompt}</div>
        <Space style={{marginTop: 5}}>
          <Button size="small" type="primary" onClick={onSave}>Done</Button>
          <Button size="small" onClick={onCancel}>Cancel</Button>
        </Space>
      </div>}
      {!editMode && <img src={imageSrc} onClick={() => setEditMode(true)} onLoad={() => setIsLoading(false)}/>}
      {!editMode && isLoading && <img src="/boba/loadingicon.gif" />}

    </>
  )
}

let ctrl;

const Home = () => {
  const [numOfScenarios, setNumOfScenarios] = useState('5');
  const [illustrationStyle, setIllustrationStyle] = useState('graphicart');
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
  
  function abortLoad(){
    ctrl && ctrl.abort();
    setLoading(false);
  }

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    setLoading(false);
  }

  function handleIllustrationStyleChange(value) {
    setIllustrationStyle(value);
    setLoading(false);
  }

  const onExplore = (id) => {
    setDrawerTitle("Explore strategy: " + scenarios.strategies[id].title)
    setChatContext({id: id, type: 'strategy', ...scenarios.strategies[id]})
    setDrawerOpen(true);
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
    console.log("submitting prompt");
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    // setPrompt(value);
    setSelections([]);

    const uri = '/api/create-storyboard?input=' + encodeURIComponent(prompt) + '&num_scenes=' + encodeURIComponent(numOfScenarios) + '&image_style=' + encodeURIComponent(illustrationStyle);

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
          // console.log("scenarios", scenarios);
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
  
  const toggleAnswers = () => {
    setAnswersVisible(!answersVisible);
  };

  const router = useRouter();
  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.prompt;
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
          <b style={{ fontSize: 20, display: 'inline-block' }}>Storyboarding</b>
          <br /><br />

          <div>
            Scenario and story description (multiple lines allowed):
          </div>
          <Input.TextArea autoSize={{minRows: 1}} placeholder="Describe the story or future scenario. You can break it into scenes and label each scene with a title, eg 'Scene 1: The beginning...'"
            value={prompt} onChange={(e,v)=> {setPrompt(e.target.value)}}
            onSubmit={onSubmitPrompt} style={{ width: '95%' }}
            disabled={isLoading}
          /><br/>
          <Button disabled={isLoading} type="primary" style={{marginTop: 5}} onClick={onSubmitPrompt}>Create storyboard</Button>
          &nbsp;&nbsp;
          Generate at least <Select defaultValue={'as many scenes as needed'} onChange={handleSelectChange} style={{ width: 220 }} disabled={isLoading}
            options={[
              { value: 'as many scenes as described in to the prompt', label: 'as many scenes as needed' },
              { value: '3', label: '3 scenes' },
              { value: '4', label: '4 scenes' },
              { value: '5', label: '5 scenes' },
              { value: '6', label: '6 scenes' },
              { value: '7', label: '7 scenes' },
              { value: '8', label: '8 scenes' },
              { value: '9', label: '9 scenes' },
              { value: '10', label: '10 scenes' },
            ]}>
          </Select>
          &nbsp;&nbsp;
          Illustration style: <Select defaultValue={'graphicart'} onChange={handleIllustrationStyleChange} style={{ width: 200 }} disabled={isLoading}
              options={[
                { value: 'sketch', label: <div><span className='config-icon'><AiOutlineEdit/></span> Hand-drawn sketch</div> },
                { value: 'graphicart', label: <div><span className='config-icon'><AiOutlineFormatPainter/></span> Graphic art</div> },
                { value: 'photorealistic', label: <div><span className='config-icon'><AiOutlinePicture/></span> Photo-realistic</div> }
              ]}>
            </Select>
          &nbsp;&nbsp;

          {isLoading ? <Spin /> : <></>}
          
          {isLoading && <Button type="primary" danger onClick={abortLoad} style={{marginLeft: 10}}>Stop</Button>}

          <br /><br />
          {selections.length > 0 && <SelectedItemsMenu selections={selections} items={scenarios} onClickTestStrategies={onClickTestStrategies} />}
        </div>
        {/* END PROMPT CENTER */}

        <div id="storyboard">
          {/* <Space align="baseline"> */}
          {scenarios?.map((scenario, i) => {
              return <Card key={i} className="scenario" cover={<SceneCardCover scenario={scenario}/>}
                actions={[
                <input key={'cb'+i} type="checkbox" className="select-scenario" onChange={onScenarioSelectChanged(i)} />,
                <Button type="link" key="explore" onClick={() => onExplore(i)}>Edit</Button>, 
                <Button type="text" key="explore">...</Button>, 
              ]}>
                <div className="card-prop stackable" style={{marginTop: -10}}>
                  <div className="card-prop-name" style={{fontSize: 'larger'}} contentEditable suppressContentEditableWarning={true}>{scenario.title}</div>
                  <div className="card-prop-value" contentEditable suppressContentEditableWarning={true}>{scenario.detail}</div>
                </div>
                
              </Card>
            })}
            {/* </Space> */}
        </div>

        <div className="scenarios-plot-container" style={{ display: displayMode == 'plot' ? 'block' : 'none' }}>
          {/* <ScenariosPlot scenarios={scenarios} visible={displayMode == 'plot'} /> */}
        </div>

      </div>
    </>
  );
};

export default Home;
