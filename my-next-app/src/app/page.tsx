"use client";

import { getWalletBalance, getWalletId } from "@/services/api";
import { signIn, signOut, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";


export default function Home() {
  const router = useRouter();
  const session = useSession();
  console.log(session);
  console.log(session.data);
  console.log(session.data?.user);
  const [discordName, setDiscordName] = useState("");
  const [walletId, setWalletId] = useState<string>("");
  const [walletBalance, setWalletBalance] = useState<number | null>(null);

  useEffect(() => {
    const fetchWalletData = async () => {
      if (session.data?.user?.name) {
        const username = session.data.user.name;
        console.log(username);
        setDiscordName(username);
        try {
          const id = await getWalletId(username);
          console.log(id);
          setWalletId(id ?? "未取得");
          const bal = id ? await getWalletBalance(id) : null;
          console.log(bal);
          setWalletBalance(bal);
        } catch (error) {
          console.error("ウォレット情報の取得に失敗しました", error);
        }
      }
      else{
        console.log("session.data?.user is null");
      }
    };
    fetchWalletData();
  }, [session.data?.user]);

  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-8 text-2xl">
      {session.data?.user ? (
        <div className="bg-gray-800 p-10 rounded-3xl shadow-2xl">
          <h1 className="text-4xl font-bold mb-6">Welcome, {discordName}</h1>
          <p className="text-3xl mb-4">ウォレットID: {walletId || "未取得"}</p>
          <p className="text-3xl mb-6">ウォレット残高: {walletBalance !== null ? `${walletBalance} トークン` : "取得中..."}</p>
          <button 
            onClick={() => signOut()}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-2xl transition-all text-2xl"
          >
            ログアウト
          </button>
        </div>
      ) : (
        <div className="bg-gray-800 p-10 rounded-3xl shadow-2xl">
          <p className="text-3xl mb-6">ログインしてください</p>
          <button 
            onClick={() => signIn("/api/auth/signin")}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-2xl transition-all text-2xl"
          >
            ログイン
          </button>
        </div>
      )}
    </div>
  );
}
