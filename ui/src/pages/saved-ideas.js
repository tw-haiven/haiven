import { Badge, Button, Card, Space, Tag, Input } from "antd";
import { useEffect, useState } from "react";
import { AiOutlineDelete, AiOutlineStar } from "react-icons/ai"
import useSWR from 'swr';

const fetcher = async (uri) => {
  const response = await fetch(uri);
  return response.json();
};

const SavedIdeas = () => {
  const [ideas, setIdeas]  = useState([]);
  const [filteredIdeas, setFilteredIdeas]  = useState([]);
  const { data, error } = useSWR('/api/saved-ideas', fetcher);
  useEffect(() => {
    console.log("data", data);
    setIdeas(data);
    setFilteredIdeas(data);
  }, [data]);

  if (error) return <div>oops... {error.message}</div>;
  if (data === undefined) return <div>Loading...</div>;
  
  const deleteIdea = async (id) => {
    const idea = ideas[id];
    const response = await fetch('/api/delete-idea', {
      method: 'POST',
      body: JSON.stringify(idea),
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    setIdeas(data);
    setFilteredIdeas(data);
    console.log("data", data);
  };

  const onSearch = (e) => {
    const v = e.target.value;
    if(v.trim() === '') {
      setFilteredIdeas(ideas);
    }
    else {
      const matchingIdeas = ideas.filter(obj => Object.values(obj).some(val => val.includes(v)));
      setFilteredIdeas(matchingIdeas);
    }
  }

  return <div id="canvas">
    <h1 style={{marginLeft: 5}}><AiOutlineStar /> Saved Ideas</h1>

    <Input.Search placeholder="Search saved ideas" style={{width: 300, marginBottom: 20}} 
                  onChange={onSearch}/>

    <div className={'scenarios-collection equal-display'}>
      {filteredIdeas?.map((idea, i) => { return (
        <Card key={i} className="scenario" title={
            <Space direction="vertical">
              <div style={{marginTop: 15}}><Tag color="blue" style={{margin: 0}} size="small">{idea.type}</Tag></div>
              <div>{idea.title}{idea.tagline && ": " + idea.tagline}</div>
            </Space>
          } 
          actions={[
            <Button danger onClick={() => deleteIdea(i)}>Delete</Button>
          ]}>
            <div className="scenario-card-content">
              {idea.type === 'strategy' && <>
                <div className="card-prop stackable">
                  <div className="card-prop-name">Winning aspiration</div>
                  <div className="card-prop-value">{idea.winning_aspiration}</div>
                </div>
                <div className="card-prop stackable" style={{marginTop: 10}}>
                  <div className="card-prop-name">Problem diagnosis</div>
                  <div className="card-prop-value">{idea.problem_diagnosis}</div>
                </div>
                <div className="card-prop stackable" style={{marginTop: 10}}>
                  <div className="card-prop-name">Where to play</div>
                  <div className="card-prop-value">{idea.where_to_play}</div>
                </div>
                <div className="card-prop stackable" style={{marginTop: 10}}>
                  <div className="card-prop-name">How to win</div>
                  <div className="card-prop-value">{idea.how_to_win}</div>
                </div>
                <div className="card-prop stackable" style={{marginTop: 10}}>
                  <div className="card-prop-name">What would have to be true?</div>
                  <div className="card-prop-value">{idea.assumptions}</div>
                </div>
              </>}
              {idea.type === 'concept' && <>
                <div className="card-prop stackable" >
                  <div className="card-prop-value">{idea.pitch}</div>
                </div>
                {idea.hypothesis && <div className="card-prop stackable" style={{marginTop: 10}}>
                  <div className="card-prop-name">Hypothesis</div>
                  <div className="card-prop-value">{idea.hypothesis}</div>
                </div> }
              </>}
              {idea.type === 'scenario' && <>
                <div className="scenario-summary">{idea.summary}</div>
                {idea.horizon && <div className="card-prop stackable">
                  <div className="card-prop-name">Horizon</div>
                  <div className="card-prop-value">{idea.horizon}</div>
                </div> }
                {idea.plausibility && <div className="card-prop stackable">
                  <div className="card-prop-name">Plausibility</div>
                  <div className="card-prop-value">{idea.plausibility}</div>
                </div> }
                {idea.probability && <div className="card-prop stackable">
                  <div className="card-prop-name">Probability</div>
                  <div className="card-prop-value">{idea.probability}</div>
                </div> }
                {idea.signals && <div className="card-prop">
                  <div className="card-prop-name">Signals/Driving Forces</div>
                  <div className="card-prop-value">{(idea.signals || []).join(', ')}</div>
                </div> }
                {idea.threats && <div className="card-prop">
                  <div className="card-prop-name">Threats</div>
                  <div className="card-prop-value">{(idea.threats || []).join(', ')}</div>
                </div> }
                {idea.opportunities && <div className="card-prop">
                  <div className="card-prop-name">Opportunities</div>
                  <div className="card-prop-value">{(idea.opportunities || []).join(', ')}</div>
                </div> }
              </>}

              <br/>
              <b>Prompt: </b> {idea.prompt}
            </div>
        </Card>
      )})}
    </div>
  </div>
}

export default SavedIdeas;