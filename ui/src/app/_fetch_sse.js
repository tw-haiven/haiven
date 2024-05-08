export function fetchSSE(options) {
  const { url, onData, onStop } = options;
  try {
    const sse = new EventSource(url, { withCredentials: true });
    sse.onmessage = (event) => {
      // if(!isLoadingXhr) {
      //   console.log("is loading xhr", isLoadingXhr);
      //   return;
      // }
      if (event.data == "[DONE]") {
        onStop();
        sse.close();
        return;
      }
      onData(event, sse);
    };
    sse.onerror = (error) => {
      console.log("error", error);
      onStop();
    };
    sse.onopen = (event) => {};
  } catch (error) {
    console.log("error", error);
    onStop();
  }
}
