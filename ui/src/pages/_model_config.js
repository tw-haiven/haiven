import { Select } from "antd";

export default function ModelConfig({ onModelChange, availableModels }) {
  return (
    <div className="model-config">
      <Select
        onChange={onModelChange}
        options={availableModels}
        style={{ width: 200 }}
      />
    </div>
  );
}
