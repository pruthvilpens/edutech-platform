export type Role = 'admin' | 'instructor' | 'student'

export interface Permission {
  resource: string
  action: string
}

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: [
    { resource: 'user', action: 'create' },
    { resource: 'user', action: 'read' },
    { resource: 'user', action: 'update' },
    { resource: 'user', action: 'delete' },
    { resource: 'document', action: 'create' },
    { resource: 'document', action: 'read' },
    { resource: 'document', action: 'delete' },
    { resource: 'question', action: 'create' },
    { resource: 'question', action: 'read' },
    { resource: 'question', action: 'update' },
    { resource: 'question', action: 'delete' },
    { resource: 'test', action: 'create' },
    { resource: 'test', action: 'read' },
    { resource: 'test', action: 'update' },
    { resource: 'test', action: 'delete' },
    { resource: 'test', action: 'assign' },
    { resource: 'result', action: 'read_all' },
  ],
  instructor: [
    { resource: 'document', action: 'create' },
    { resource: 'document', action: 'read' },
    { resource: 'question', action: 'create' },
    { resource: 'question', action: 'read' },
    { resource: 'question', action: 'update' },
    { resource: 'question', action: 'delete' },
    { resource: 'test', action: 'create' },
    { resource: 'test', action: 'read' },
    { resource: 'test', action: 'update' },
    { resource: 'test', action: 'delete' },
    { resource: 'test', action: 'assign' },
    { resource: 'result', action: 'read_all' },
  ],
  student: [
    { resource: 'test', action: 'read' },
    { resource: 'result', action: 'read' },
  ]
}

export const ROLE_ROUTES: Record<Role, string[]> = {
  admin: ['/dashboard/admin', '/dashboard/instructor', '/dashboard/student'],
  instructor: ['/dashboard/instructor'],
  student: ['/dashboard/student']
}

export function hasPermission(userRole: Role, resource: string, action: string): boolean {
  const permissions = ROLE_PERMISSIONS[userRole] || []
  return permissions.some(p => p.resource === resource && p.action === action)
}

export function canAccessRoute(userRole: Role, route: string): boolean {
  const allowedRoutes = ROLE_ROUTES[userRole] || []
  return allowedRoutes.some(allowedRoute => route.startsWith(allowedRoute))
}

export function getDefaultRoute(userRole: Role): string {
  switch (userRole) {
    case 'admin':
      return '/dashboard/admin'
    case 'instructor':
      return '/dashboard/instructor'
    case 'student':
      return '/dashboard/student'
    default:
      return '/dashboard/student'
  }
}