// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useCallback, useRef } from "react";
import { Spin, Button } from "antd";

const useLoader = () => {
  const [loading, setLoading] = useState(false);
  const abortCtrlRef = useRef(null);

  const abortLoad = useCallback(() => {
    if (abortCtrlRef.current) {
      abortCtrlRef.current.abort("User aborted");
      setLoading(false);
    }
  }, []);

  const startLoad = useCallback(() => {
    abortLoad();
    abortCtrlRef.current = new AbortController();
    setLoading(true);
    return abortCtrlRef.current.signal;
  }, [abortLoad]);

  const StopLoad = () =>
    loading && (
      <div className="user-input">
        <Spin />
        <Button
          type="secondary"
          danger
          onClick={abortLoad}
          className="stop-button"
          data-testid="stop-button"
        >
          STOP
        </Button>
      </div>
    );

  return {
    loading,
    startLoad,
    abortLoad,
    StopLoad,
  };
};
export default useLoader;
