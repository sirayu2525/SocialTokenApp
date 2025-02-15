// /app/login/page.tsx
"use client";

import { signIn } from "next-auth/react";

export default function LoginPage() {
  return (
    <div className="p-6 max-w-lg mx-auto text-center">
      <h1 className="text-3xl font-bold mb-6">Discordでログイン</h1>
      <button
        onClick={() => signIn("discord")}
        className="bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600"
      >
        Discordでログイン
      </button>
    </div>
  );
}
