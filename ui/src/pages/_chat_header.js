// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
const ChatHeader = ({ models, titleComponent }) => {
  const chatModel = models["chat"]?.name || "";

  return (
    <div className="chat-header">
      {titleComponent}
      <div className="model-disclaimer">
        AI model:&nbsp;<b>{chatModel}</b>&nbsp;|&nbsp;AI-generated content can
        be inaccurate—validate all important information. Do not include client
        confidential information or personal data in your inputs. Review our
        guidelines <a href="/about">here</a>.
      </div>
    </div>
  );
};

export default ChatHeader;
