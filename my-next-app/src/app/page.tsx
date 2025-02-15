"use client";

import React, { useState } from "react";
import { getWalletId, getWalletBalance } from "@/services/api";

export default function Home() {
  const [discordId, setDiscordId] = useState("");
  const [walletId, setWalletId] = useState<string | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const wallet = await getWalletId(discordId);
      if (!wallet) {
        setError("ウォレットIDが見つかりませんでした");
        return;
      }
      setWalletId(wallet);
      const bal = await getWalletBalance(wallet);
      setBalance(bal);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Discord IDでウォレット残高を確認</h1>
      <input
        type="text"
        value={discordId}
        onChange={(e) => setDiscordId(e.target.value)}
        placeholder="Discord IDを入力"
        className="border p-2 rounded w-full mb-4"
      />
      <button
        onClick={handleSearch}
        disabled={loading}
        className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        検索
      </button>
      {loading && <p className="mt-4">検索中...</p>}
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {walletId && (
        <div className="mt-4">
          <p>ウォレットID: {walletId}</p>
          <p className="text-green-500">残高: {balance ?? "取得中..."} MOP</p>
        </div>
      )}
    </div>
  );
}
