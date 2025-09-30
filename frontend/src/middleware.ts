import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'
import { canAccessRoute, getDefaultRoute, type Role } from './lib/rbac'

export async function middleware(request: NextRequest) {
  const token = await getToken({ 
    req: request,
    secret: process.env.NEXTAUTH_SECRET 
  })
  const pathname = request.nextUrl.pathname

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/signup', '/']
  const isPublicRoute = publicRoutes.includes(pathname)

  // Protected routes that require authentication (exclude auth API routes)
  const isProtectedRoute = pathname.startsWith('/dashboard') || (pathname.startsWith('/api') && !pathname.startsWith('/api/auth'))

  // If user is not authenticated and trying to access protected route
  if (!token && isProtectedRoute) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // If user is authenticated and trying to access auth pages, redirect to dashboard
  if (token && (pathname === '/login' || pathname === '/signup')) {
    const userRole = token.role as Role
    const defaultRoute = getDefaultRoute(userRole)
    return NextResponse.redirect(new URL(defaultRoute, request.url))
  }

  // Handle dashboard route without specific role path
  if (token && pathname === '/dashboard') {
    const userRole = token.role as Role
    const defaultRoute = getDefaultRoute(userRole)
    return NextResponse.redirect(new URL(defaultRoute, request.url))
  }

  // Check role-based access for dashboard routes
  if (token && pathname.startsWith('/dashboard/')) {
    const userRole = token.role as Role
    
    if (!canAccessRoute(userRole, pathname)) {
      const defaultRoute = getDefaultRoute(userRole)
      return NextResponse.redirect(new URL(defaultRoute, request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)',
  ],
}