// /app/dashboard/page.tsx
"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import { getWalletId, getWalletBalance } from "@/services/api";

export default function DashboardPage() {
  const { data: session } = useSession();
  const [walletId, setWalletId] = useState<string | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWalletData = async () => {
      if (session?.user?.name) {
        try {
          const wallet = await getWalletId(session.user.name);
          setWalletId(wallet);
          if (wallet) {
            const bal = await getWalletBalance(wallet);
            setBalance(bal);
          }
        } catch (err: any) {
          setError(err.message);
        }
      }
    };
    fetchWalletData();
  }, [session]);

  if (!session) {
    return (
      <div className="text-center p-6">
        <p>ログインが必要です</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">ユーザーダッシュボード</h1>
      <p>ユーザー名: {session.user.name}</p>
      {walletId ? (
        <p>ウォレットID: {walletId}</p>
      ) : (
        <p className="text-gray-500">ウォレットID取得中...</p>
      )}
      {balance !== null ? (
        <p className="text-green-500">残高: {balance} MOP</p>
      ) : (
        <p className="text-gray-500">残高取得中...</p>
      )}
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
}
