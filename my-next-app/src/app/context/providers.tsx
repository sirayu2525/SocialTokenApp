"use client";

import { SessionProvider } from "next-auth/react";
import { ReactNode } from "react";

type ProviderProps = {
    children: ReactNode;
}

function Provider({ children }: ProviderProps) {
    return <SessionProvider>{children}</SessionProvider>
}

export default Provider;