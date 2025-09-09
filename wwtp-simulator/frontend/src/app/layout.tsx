import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WWTP Simulator",
  description: "Wastewater Treatment Plant Simulation using BSM2-Python",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
