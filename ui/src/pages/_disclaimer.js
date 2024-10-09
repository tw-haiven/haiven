// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
const Disclaimer = ({ models }) => {
  const chatModel = models["chat"]?.name || "";

  return (
    <div className="disclaimer">
      AI model:&nbsp;<b>{chatModel}</b>&nbsp;|&nbsp;AI-generated content may be
      incorrect. Validate important information.
    </div>
  );
};

export default Disclaimer;
