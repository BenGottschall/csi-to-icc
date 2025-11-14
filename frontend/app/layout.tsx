import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CSI to ICC Code Mapper",
  description: "Map CSI MasterFormat codes to ICC building code sections for student and educational use",
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
