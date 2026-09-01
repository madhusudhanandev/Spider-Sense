import type { ReactNode } from "react";
import Navbar from "./Navbar";

export default function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-void">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">{children}</main>
    </div>
  );
}
