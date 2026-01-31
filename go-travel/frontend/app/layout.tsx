import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "go.",
  description: "Extreme minimalist travel planner",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-black antialiased">{children}</body>
    </html>
  );
}
