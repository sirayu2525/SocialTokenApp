// App.tsx
import React, { useState } from "react";
import { useSDK } from "@metamask/sdk-react";

function App() {
  const { sdk, connected, connecting, account, chainId, connect } = useSDK();
  const [balance, setBalance] = useState<string>("");

  const getBalance = async () => {
    if (!window.ethereum || !account) return;
    const wei = await window.ethereum.request({
      method: "eth_getBalance",
      params: [account, "latest"],
    });
    setBalance((parseInt(wei, 16) / 1e18).toFixed(6));
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>🌐 MetaMask DApp</h1>
      {connected ? (
        <>
          <p>✅ Connected to: {account}</p>
          <p>🌐 Chain ID: {chainId}</p>
          <button onClick={getBalance}>Get Balance</button>
          <p>💰 Balance: {balance} ETH</p>
        </>
      ) : (
        <button onClick={() => connect()}>Connect MetaMask</button>
      )}
    </div>
  );
}

export default App;
