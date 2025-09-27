import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BSM2 Simulator',
  description: 'Dynamic wastewater treatment plant simulator based on BSM2',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}