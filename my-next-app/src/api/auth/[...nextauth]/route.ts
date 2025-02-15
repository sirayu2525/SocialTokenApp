// /app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";

const handler = {
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account && profile) {
        token.id = profile.id;
        token.name = profile.username;
      }
      return token;
    },
  },
  pages: {
    signIn: "/login",
  },
};

export { handler as GET, handler as POST };
