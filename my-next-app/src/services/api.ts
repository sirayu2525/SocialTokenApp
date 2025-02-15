// src/services/api.ts

const DB_API_URL = process.env.NEXT_PUBLIC_DB_API_URL;
const BLOCKCHAIN_API_URL = process.env.NEXT_PUBLIC_BLOCKCHAIN_API_URL;
if (!DB_API_URL || !BLOCKCHAIN_API_URL) {
  throw new Error("環境変数が設定されていません");
}

export async function getWalletId(discord_name: string): Promise<string | null> {
    const response = await fetch(
      `${DB_API_URL}/data/search?table_name=data_records&column=discord_name&value=${discord_name}`,
      {
        headers: {
          "X-API-Key": "mysecretkey",
        },
      }
    );
    if (!response.ok) {
      throw new Error("ウォレットIDの取得に失敗しました");
    }
    const data = await response.json();
    return data?.wallet_id ?? null;
  }
  
  export async function getWalletBalance(walletId: string): Promise<number | null> {
    const response = await fetch(
      `${BLOCKCHAIN_API_URL}/wallet_balance/${walletId}`
    );
    if (!response.ok) {
      throw new Error("ウォレット残高の取得に失敗しました");
    }
    const data = await response.json();
    return data?.wallet_balance ?? null;
  }
  