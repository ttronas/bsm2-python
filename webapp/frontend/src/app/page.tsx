'use client'

import dynamic from 'next/dynamic'

// Dynamically import the FlowEditor to avoid SSR issues with React Flow
const FlowEditor = dynamic(() => import('@/components/FlowEditor'), {
  ssr: false,
})

export default function Home() {
  return (
    <main className="h-screen w-screen">
      <FlowEditor />
    </main>
  )
}