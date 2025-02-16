// /app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";

export const authOptions = {
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
     jwt: (params) => {
      console.log(params);
      return params.token;
    },
    // session: async ({ session, token }) => {
    //   session.user.name = token.name;
    //   return session;
    // },
  },
  };

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
