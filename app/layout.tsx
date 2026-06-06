import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Striver Judge",
  description: "Local C/C++ judge for the Striver problem set",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
