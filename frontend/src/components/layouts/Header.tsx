'use client'

import { signOut, useSession } from 'next-auth/react'
import Link from 'next/link'

export default function Header() {
  const { data: session } = useSession()

  return (
    <header className="bg-background/80 backdrop-blur border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-base font-semibold tracking-tight text-foreground">
              EduTech
            </Link>
          </div>

          <nav className="hidden md:flex items-center gap-2">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-md text-sm font-medium text-foreground hover:bg-secondary hover:text-secondary-foreground"
            >
              Dashboard
            </Link>
            {session?.user?.role === 'admin' && (
              <Link
                href="/dashboard/admin"
                className="px-3 py-1.5 rounded-md text-sm font-medium text-foreground hover:bg-secondary hover:text-secondary-foreground"
              >
                Admin
              </Link>
            )}
            {(session?.user?.role === 'admin' || session?.user?.role === 'instructor') && (
              <Link
                href="/dashboard/instructor"
                className="px-3 py-1.5 rounded-md text-sm font-medium text-foreground hover:bg-secondary hover:text-secondary-foreground"
              >
                Instructor
              </Link>
            )}
            <Link
              href="/dashboard/student"
              className="px-3 py-1.5 rounded-md text-sm font-medium text-foreground hover:bg-secondary hover:text-secondary-foreground"
            >
              Student
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            {session?.user && (
              <>
                <span className="text-sm text-muted-foreground truncate max-w-[180px]">
                  {session.user.name} ({session.user.role})
                </span>
                <button
                  onClick={() => signOut()}
                  className="inline-flex items-center justify-center rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90"
                >
                  Sign out
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}