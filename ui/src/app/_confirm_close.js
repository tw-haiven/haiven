// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import { Modal, Button } from "antd";

const ConfirmClose = ({ isVisible, onForceClose, onReturnBack }) => {
  return (
    <Modal
      className="close-confirmation-modal"
      title="Are you sure you want to close?"
      open={isVisible}
      closable={false}
    >
      <p>
        You have unsaved edits. By closing any unsaved changes will be lost.
      </p>
      <div className="confirmation-modal-footer">
        <Button className="confirmation-modal-close-btn" onClick={onForceClose}>
          CLOSE ANYWAY
        </Button>
        <Button
          className="confirmation-modal-cancel-btn"
          onClick={onReturnBack}
        >
          GO BACK
        </Button>
      </div>
    </Modal>
  );
};

export default ConfirmClose;
