import React, { useState } from 'react';
import { Input, Button, Drawer } from 'antd';
const { Search } = Input;
import { AiOutlineDelete, AiOutlinePlusCircle } from 'react-icons/ai';
const CreativeMatrix = () => {
  const [dimensions, setDimensions] = useState(['Dimension 1', 'Dimension 2']);
  const [dimensionValues, setDimensionValues] = useState([['Dim 1 Value 1', 'Dim 1 Value 2'], ['D2 Value 1', 'D2 Value 2']]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [prompt, setPrompt] = useState('');

  const addDimension = () => {
    const newDimensions = [...dimensions];
    newDimensions.push('Dimension ' + (newDimensions.length+1));
    setDimensions(newDimensions);
  }
  
  const updateDimension = (e, index) => {
    const newDimensions = [...dimensions];
    newDimensions[index] = e.target.value;
    setDimensions(newDimensions);
  }

  const deleteDimension = (e, index) => {
    const newDimensions = [...dimensions];
    newDimensions.splice(index, 1);
    setDimensions(newDimensions);
  }

  const addDimensionValue = (index) => {
    const newDimensionValues = [...dimensionValues];
    newDimensionValues[index] = newDimensionValues[index] || [];
    newDimensionValues[index].push('Dim ' + (index+1) + ' value ' + (newDimensionValues[index].length+1));
    setDimensionValues(newDimensionValues);
  }

  const updateDimensionValue = (e, index, valueIndex) => {
    const newDimensionValues = [...dimensionValues];
    newDimensionValues[index][valueIndex] = e.target.value;
    setDimensionValues(newDimensionValues);
  }

  const deleteDimensionValue = (index, valueIndex) => {
    const newDimensionValues = [...dimensionValues];
    newDimensionValues[index].splice(valueIndex, 1);
    setDimensionValues(newDimensionValues);
  }

  const onSubmitPrompt = () => {
  }
  
  return <div id="canvas">
    <h1 style={{marginTop: 0}}>Creative Matrix</h1>
    <Button type="primary" onClick={() => setDrawerOpen(!drawerOpen)}>Configure Dimensions</Button>
    <Search placeholder="What do you want to create?"
              value={prompt} onChange={(e,v)=> {setPrompt(e.target.value)}}
              onSearch={onSubmitPrompt} style={{ width: 500, color: 'white', marginLeft: 10 }}
              disabled={isLoading} enterButton={
                <div>
                  <span>Go</span>
                </div>}
            />
    <div style={{marginTop: 20}}>
    
      {/* DIMENSIONS */}
      <Drawer title="Dimensions" placement="right" closable={true} width={300} mask={false} open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <div>
          <Button size="small" type="primary" onClick={addDimension}>Add Dimension</Button>
          {dimensions.map((dimension, index) => {
            return <div style={{marginTop: 10}}>
              
              <Input size="small" style={{marginTop: 5, width: 200}} key={index} value={dimension} onChange={e => updateDimension(e, index)} />
              {dimensions.length > 2 &&
                <Button size="small" style={{marginTop: 5, marginLeft: 25}} danger onClick={e => deleteDimension(e, index)}><AiOutlineDelete/></Button>
              }<br/>

              <div style={{marginLeft: 20, marginBottom: 5}}>
                {dimensionValues[index]?.map((value, valueIndex) => {
                  return <div className='dimension-value'>
                    <Input size="small" style={{marginTop: 5, width: 200}} key={valueIndex} value={value} onChange={e => updateDimensionValue(e, index, valueIndex)} />
                    <Button size="small" style={{marginTop: 5, marginLeft: 5}} danger onClick={() => deleteDimensionValue(index, valueIndex)}><AiOutlineDelete/></Button>
                  </div>
                })}
              </div>

              <Button size="small" type="primary" style={{marginLeft: 20}} onClick={() => addDimensionValue(index)}>
                Add value
              </Button>
            </div>
          })}
        </div>
      </Drawer>
      
      {/* MATRIX */}
      <div>
        <table style={{width: '95%'}}>
          <thead>
            <tr>
              <th></th>
              {dimensions[0] && dimensionValues[0]?.map((colValue, index) => {
                return <th>{colValue}</th>
              })}
            </tr>
          </thead>
          <tbody style={{border: '1px solid silver'}}>
            {dimensions[1] && dimensionValues[1]?.map((rowValue, index) => {
              return <tr>
                <td><b>{rowValue}</b></td>
                {dimensionValues[0]?.map((colValue, index) => {
                  return <td style={{border: '1px solid silver'}}>{colValue} - {rowValue}</td>
                })}
              </tr>
            })}
          </tbody>
        </table>
      </div>
    </div>
  </div>
}

export default CreativeMatrix;