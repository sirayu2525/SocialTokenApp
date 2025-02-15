// /app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";

const handler = NextAuth({
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
      authorization: { params: { scope: "identify" } },
    }),
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account && profile) {
        token.id = profile.sub;
        token.name = profile.name;
      }
      return token;
    },
    async session({ session, token }) {
      if(session.user){
        session.user.id = token.id as string;
        session.user.name = token.name as string;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
