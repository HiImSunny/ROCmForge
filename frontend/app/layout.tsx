import type { Metadata } from "next";
import { GeistSans, GeistMono } from "geist/font";
import "./globals.css";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "ROCmForge | CUDA → ROCm on Real MI300X",
  description: "Autonomous multi-agent swarm for porting, validating and benchmarking CUDA workloads on AMD Instinct MI300X GPUs.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="bg-background text-text-primary antialiased">
        {children}
        <Toaster position="top-center" richColors closeButton />
      </body>
    </html>
  );
}
