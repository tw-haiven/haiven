// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
function formatModel(model) {
  if (model === "azure-gpt4") {
    return "GPT-4";
  }
  return model;
}

const Disclaimer = ({ models }) => {
  return (
    <div className="disclaimer">
      AI model: <b>{formatModel(models.chat)}</b>&nbsp;|&nbsp;AI-generated
      content may be incorrect. Validate important information.
    </div>
  );
};

export default Disclaimer;
