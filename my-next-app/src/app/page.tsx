// /app/page.tsx
"use client";

import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-6">
      <h1 className="text-4xl font-bold mb-6">
        Next.js App
      </h1>
      <p className="text-lg text-gray-600 mb-8 text-center">
        ようこそ！
      </p>
      <div className="space-x-4">
        <button
          onClick={() => router.push("/login")}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          ログインページへ
        </button>
      </div>
    </main>
  );
}
