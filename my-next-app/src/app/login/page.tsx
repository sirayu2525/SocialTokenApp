// /app/login/page.tsx
"use client";

import { signIn } from "next-auth/react";

export default function LoginPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-3xl font-bold mb-4">Discordでログイン</h1>
      <button
        onClick={() => signIn("discord")}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
      >
        Discordでログイン
      </button>
    </main>
  );
}
