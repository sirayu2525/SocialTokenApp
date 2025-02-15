// src/react-app-env.d.ts
interface Window {
    ethereum?: {
      isMetaMask?: boolean;
      request?: (...args: any[]) => Promise<any>;
    };
  }
  