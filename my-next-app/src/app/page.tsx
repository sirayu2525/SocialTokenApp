"use client";

import { getWalletBalance, getWalletId } from "@/services/api";
import { signIn, signOut, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";


export default function Home() {
  const router = useRouter();
  const session = useSession();
  console.log(session);
  const [discordName, setDiscordName] = useState("");
  const [walletId, setWalletId] = useState<string>("");
  const [walletBalance, setWalletBalance] = useState<number | null>(null);

  useEffect(() => {
    const fetchWalletData = async () => {
      if (session.data?.user) {
        const username = session.data.user.name ?? "";
        setDiscordName(username);
        try {
          const id = await getWalletId(username);
          setWalletId(id ?? "未取得");
          const bal = id ? await getWalletBalance(id) : null;
          setWalletBalance(bal);
        } catch (error) {
          console.error("ウォレット情報の取得に失敗しました", error);
        }
      }
    };
    fetchWalletData();
  }, [session]);

  
  return (
    <div>
      {session.data?.user ? (
        <div>
          <h1>Welcome, {discordName}</h1>
          <p>ウォレットID: {walletId || "未取得"}</p>
          <p>ウォレット残高: {walletBalance !== null ? `${walletBalance} トークン` : "取得中..."}</p>
          <button onClick={() => signOut()}>ログアウト</button>
        </div>
      ) : (
        <div>
          <button onClick={() => signIn("/api/auth/signin")}>ログインしてください</button>
        </div>
      )}
    </div>
  );
}
