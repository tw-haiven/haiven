import { Button } from "antd";
import { Col, Row } from 'antd';
import { Carousel } from 'antd';

export default function Landing() {

  const contentStyle = {
    width: '90%',
    height: '90%',
    color: '#364d79',
    lineHeight: '160px',
    textAlign: 'center',
    background: '#f1f1f1',
    border: '1px solid #f1f1f1',
  };

  return (
    <div id="landing-page">

      <Row>
        <Col span={24} style={{padding: "0 10px", height: 350}}>
          <div className="landing-main">
            <h1 style={{ padding: 0, marginTop: 0, marginBottom: 0 }}>
              We're merging <br/><a href="https://www.boba-ai.com/">Boba's</a> generative ideation features <br/>into Haiven! 
            </h1>
            <div>This is a work in progress, stay tuned while we stitch it together.</div>
          </div>
        </Col>
      </Row>
      
      {/* RESEARCH */}
      {/* <Row justify="space-around" style={{background: '#f1f1f1', paddingTop: 20}}>
        <Col span={10} style={{padding: "0 20px"}}>
          <h1>Research signals and trends</h1>
          <div className="prompt-example">Boba can search the web for articles and news to help you answer your qualitative research questions. For example:</div>
          <div className="prompt-example"> ✨ How is the hotel industry using generative AI today?</div>
          <div className="prompt-example"> ✨ What are the key challenges facing retailers in 2023 and beyond?</div>
          <div className="prompt-example"> ✨ How are pharma companies using AI to accelerate drug discovery?</div>
          <div className="prompt-example"> ✨ What were the key takeaways from Nike's latests earnings call?</div>
          <div className="prompt-example"> ✨ How do people on Reddit feel about Lululemon's products?</div>
          <br/>
          <Button type="primary" href="/research">Start researching &gt;</Button>
        </Col>
        <Col span={14}>
          <div>
            <Carousel autoplay effect="fade">
              <div>
                <h2>I can help you research articles and news on the web</h2>
                <img style={contentStyle} src="/boba/screenshots/research-1.png" />
              </div>
              
              <div>
                <h2>Quickly analyze and summarize articles, earnings calls, etc.</h2>
                <img style={contentStyle} src="/boba/screenshots/research-1.png" />
              </div>
              
              <div>
                <h2>Dig deeper to explore signals and discuss articles with me</h2>
                <img style={contentStyle} src="/boba/screenshots/research-1.png" />
              </div>
              
            </Carousel>
          </div>
        </Col>
      </Row> */}

      <div style={{margin: "50px 0"}} />

      {/* IDEATE: SCENARIOS */}
      <Row justify="space-around" style={{background: '#ffffff'}}>
        <Col span={14} style={{padding: "0 20px"}}>
          <div>
            <Carousel autoplay effect="fade">
              <div style={{textAlign: 'right'}}>
                <h2>I can brainstorm possible futures based on a strategic prompt</h2>
                <img style={contentStyle} src="/boba/screenshots/scenarios-1.png" />
              </div>
              <div>
              <h2>Explore opportunities, threats, plausibility and probability of scenarios</h2>
                <img style={contentStyle} src="/boba/screenshots/scenarios-2.png" />
              </div>
              <div>
              <h2>Dig deeper to create examples and storyboards for scenarios</h2>
                <img style={contentStyle} src="/boba/screenshots/scenarios-1.png" />
              </div>
            </Carousel>
          </div>
        </Col>
        <Col span={10} style={{padding: "0"}}>
          <h1>Ideate: Envision future scenarios</h1>
          <div className="prompt-example">Scenario building is a process of generating future-oriented stories by researching signals of change in business, culture, and technology. Scenarios are used to socialize learnings in a contextualized narrative, inspire divergent product thinking, conduct resilience/desirability testing, and/or inform strategic planning. For example, you can prompt Boba with:</div>
          <div className="prompt-example"> ✨ Hotel industry uses generative AI to transform the guest experience</div>
          <div className="prompt-example"> ✨ Pfizer accelerates drug discovery with the use of generative AI</div>
          <div className="prompt-example"> ✨ Show me the future of payments 10 years from now</div>
          <div className="prompt-example"> ✨ China becomes the next superpower (optimistic, sci-fi future)</div>
          <br/>
          <Button type="primary" href="/boba/scenarios.html">Start brainstorming scenarios &gt;</Button>
        </Col>
      </Row>

      <div style={{margin: "50px 0"}} />

      {/* IDEATE: STRATEGIES */}
      {/* <Row justify="space-around" style={{paddingTop: 20, background: '#f1f1f1'}}>
        <Col span={10} style={{padding: "0 20px"}}>
          <h1>Ideate: Brainstorm strategies</h1>
          <div className="prompt-example">Using the Playing to Win strategy framework, I can help you brainstorm "where to play" and "how to win" choices based on a strategic prompt and possible future scenarios. For example you can prompt me with:</div>
          <div className="prompt-example"> ✨ How might Nike use generative AI to transform its business model?</div>
          <div className="prompt-example"> &nbsp;&nbsp; ✨ SmartSneakers: Using Generative AI to Design Customized Sneakers</div>
          <div className="prompt-example"> &nbsp;&nbsp; ✨ AI-Driven Supply Chain Optimization</div>
          <div className="prompt-example"> &nbsp;&nbsp; ✨ Intelligent Marketing: Personalized Campaigns with AI</div>
          <div className="prompt-example">Based on a prompt and any future scenarios, Boba can generate potential strategies and key questions for you to consider, such as the ones above.</div>
          <br/>
          <Button type="primary" href="/strategies">Start brainstorming strategies &gt;</Button>
        </Col>
        <Col span={14}>
          <div>
            <Carousel autoplay effect="fade">
              <div>
                <h2>I can help you brainstorm strategies for scenarios</h2>
                <img style={contentStyle} src="/boba/screenshots/strategies-2.png" />
              </div>
              
              <div>
                <h2>Generate "where to play" and "how to win" choices</h2>
                <img style={contentStyle} src="/boba/screenshots/strategies-4.png" />
              </div>
              
              <div>
                <h2>Dig deeper and explore strategic narratives</h2>
                <img style={contentStyle} src="/boba/screenshots/strategies-3.png" />
              </div>
              
            </Carousel>
          </div>
        </Col>
      </Row> */}
     
      <div style={{margin: "50px 0"}} />

      {/* STORYBOARDING */}
      {/* <Row justify="space-around">
        <Col span={10} style={{padding: "0 20px"}}>
          <h1>Storyboarding</h1>
          <div className="prompt-example">Boba can help you build storyboards for current or future state scenarios. </div>
          <div className="prompt-example"> ✨ Brainstorm story-driven POVs (points of view) and pitches</div>
          <div className="prompt-example"> ✨ Generate illustrated scenes to describe your customer journeys</div>
          <div className="prompt-example"> ✨ Customize the script if you want, and let me do the rest</div>
          <div className="prompt-example"> ✨ Customize the styles, illustrations and more</div>
          <div className="prompt-example"> ✨ Generate storyboards directly from generated scenarios</div>

          <br/>
          <Button type="primary" href="/storyboard">Start storyboarding &gt;</Button>
        </Col>
        <Col span={14}>
          <div>
            <Carousel autoplay effect="fade">
              <div>
                <h2>Storyboard: The Hotel of the Future transforms the guest experience</h2>
                <img style={contentStyle} src="/boba/screenshots/hotel storyboard.png" />
              </div>
              <div>
                <h2>Storyboard: Generative AI accelerates drug discovery</h2>
                <img style={contentStyle} src="/boba/screenshots/cancer storyboard.png" />
              </div>
              <div>
                <h2>Storyboard: China colonizes Mars</h2>
                <img style={contentStyle} src="/boba/screenshots/mars storyboard.png" />
              </div>
            </Carousel>
          </div>
          <br/>
          <br/>
        </Col>
      </Row> */}
    </div>
  );
}
