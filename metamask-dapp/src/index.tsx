// index.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { MetaMaskProvider } from "@metamask/sdk-react";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <MetaMaskProvider
      debug={false}
      sdkOptions={{
        dappMetadata: {
          name: "Example React Dapp",
          url: window.location.href,
        },
        infuraAPIKey: process.env.REACT_APP_INFURA_API_KEY, // .envから読み取る
      }}
    >
      <App />
    </MetaMaskProvider>
  </React.StrictMode>
);
