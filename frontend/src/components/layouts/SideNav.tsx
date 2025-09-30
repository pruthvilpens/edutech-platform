'use client'

import { useSession } from 'next-auth/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { hasPermission, type Role } from '@/lib/rbac'

interface NavItem {
  name: string
  href: string
  resource?: string
  action?: string
}

const getNavItems = (role: Role): NavItem[] => {
  const baseItems: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard' },
  ]

  if (role === 'admin') {
    return [
      ...baseItems,
      { name: 'Users', href: '/dashboard/admin/users', resource: 'user', action: 'read' },
      { name: 'Documents', href: '/dashboard/admin/documents', resource: 'document', action: 'read' },
      { name: 'Questions', href: '/dashboard/admin/questions', resource: 'question', action: 'read' },
      { name: 'Tests', href: '/dashboard/admin/tests', resource: 'test', action: 'read' },
      { name: 'Results', href: '/dashboard/admin/results', resource: 'result', action: 'read_all' },
    ]
  }

  if (role === 'instructor') {
    return [
      ...baseItems,
      { name: 'Documents', href: '/dashboard/instructor/documents', resource: 'document', action: 'read' },
      { name: 'Questions', href: '/dashboard/instructor/questions', resource: 'question', action: 'read' },
      { name: 'Tests', href: '/dashboard/instructor/tests', resource: 'test', action: 'read' },
      { name: 'Results', href: '/dashboard/instructor/results', resource: 'result', action: 'read_all' },
    ]
  }

  return [
    ...baseItems,
    { name: 'My Tests', href: '/dashboard/student/tests', resource: 'test', action: 'read' },
    { name: 'My Results', href: '/dashboard/student/results', resource: 'result', action: 'read' },
    { name: 'Leaderboard', href: '/dashboard/student/leaderboard' },
  ]
}

export default function SideNav() {
  const { data: session } = useSession()
  const pathname = usePathname()

  if (!session?.user?.role) {
    return null
  }

  const navItems = getNavItems(session.user.role as Role)
  const userRole = session.user.role as Role

  return (
    <nav className="bg-background border-r w-60 min-h-screen">
      <div className="p-3">
        <ul className="space-y-1.5">
          {navItems.map((item) => {
            // Check permissions if resource and action are specified
            if (item.resource && item.action && !hasPermission(userRole, item.resource, item.action)) {
              return null
            }

            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')

            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-secondary text-foreground'
                      : 'text-foreground hover:bg-secondary hover:text-secondary-foreground'
                  }`}
                >
                  {item.name}
                </Link>
              </li>
            )
          })}
        </ul>
      </div>
    </nav>
  )
}