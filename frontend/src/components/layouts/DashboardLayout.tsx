'use client'

import SessionProvider from '../providers/SessionProvider'
import Header from './Header'
import SideNav from './SideNav'
import Footer from './Footer'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <SessionProvider>
      <div className="min-h-screen bg-background flex flex-col">
        <Header />
        <div className="flex flex-1">
          <SideNav />
          <main className="flex-1 p-6 lg:p-8">
            <div className="mx-auto max-w-6xl">
              {children}
            </div>
          </main>
        </div>
        <Footer />
      </div>
    </SessionProvider>
  )
}