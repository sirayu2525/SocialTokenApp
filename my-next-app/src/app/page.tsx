// /app/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useSession, signIn, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

export function Clock(){
    const [time, setTime] = useState(new Date().toLocaleTimeString());

    useEffect(() => {
        const timer = setInterval(() => {
            setTime(new Date().toLocaleTimeString());
        }, 1000);
    
        return () => clearInterval(timer);
    },[]);

    return <p>{time}</p>;
}

export default function Home() {
  const { data: session } = useSession();
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      {/*  キャッチコピー */}
      <h1 className="text-4xl font-bold mb-4 text-center">
        🎉 Welcome to Social Token App!
      </h1>
      <p className="text-lg text-gray-600 mb-8 text-center">
        Discordでログインして、あなたのウォレット残高を確認しましょう。
      </p>

      {/*  ログイン状態による表示切り替え */}
      {session ? (
        <div className="text-center">
          <p className="mb-4">
             ようこそ、<strong>{session.user?.name}</strong> さん！
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            ダッシュボードへ進む
          </button>
          <button
            onClick={() => signOut()}
            className="mt-4 text-red-500 underline"
          >
            ログアウト
          </button>
        </div>
      ) : (
        <button
          onClick={() => router.push("/login")}
          className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600"
        >
           Discordでログイン
        </button>
      )}
    </div>
  );
}
