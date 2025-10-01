import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { compare } from "bcryptjs"
import jwt from "jsonwebtoken" // Import the library

export const authOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  basePath: '/api/auth',
  providers: [
    Credentials({
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          console.log('Missing credentials')
          return null
        }

        try {
          console.log('Attempting to authenticate user:', credentials.email)
          
          // Query user from Hasura
          const response = await fetch(process.env.NEXT_PUBLIC_HASURA_GRAPHQL_URL!, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-hasura-admin-secret': process.env.HASURA_GRAPHQL_ADMIN_SECRET!,
            },
            body: JSON.stringify({
              query: `
                query GetUser($email: String!) {
                  users(where: {email: {_eq: $email}}) {
                    id
                    email
                    full_name
                    password_hash
                    role
                    is_active
                    email_verified
                  }
                }
              `,
              variables: { email: credentials.email }
            })
          })

          const { data, errors } = await response.json()
          
          if (errors) {
            console.error('GraphQL errors:', errors)
            return null
          }
          
          const user = data?.users?.[0]
          console.log('User found:', user ? { id: user.id, email: user.email, role: user.role, is_active: user.is_active } : 'No user found')

          if (!user || !user.is_active) {
            console.log('User not found or inactive')
            return null
          }

          // Verify password
          const isValidPassword = await compare(credentials.password as string, user.password_hash)
          console.log('Password valid:', isValidPassword)
          
          if (!isValidPassword) {
            console.log('Invalid password')
            return null
          }

          console.log('Authentication successful for user:', user.email)
          return {
            id: user.id,
            email: user.email,
            name: user.full_name,
            role: user.role,
            emailVerified: user.email_verified
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      }
    })
  ],
  pages: {
    signIn: '/login',
    signUp: '/signup'
  },
  callbacks: {
    jwt: async ({ token, user }) => {
      if (user) {
        token.role = user.role
        token.id = user.id
      }
      return token
    },
    session: async ({ session, token }) => {
      if (token && session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string

        // --- ADD THIS BLOCK ---
        // Create a payload that the backend will understand
        const payload = {
          sub: token.id, // 'sub' is the standard claim for subject (user ID)
        };
        
        // Sign the token with the same secret your backend uses
        const accessToken = jwt.sign(payload, process.env.SECRET_KEY!, {
          algorithm: 'HS256', // Must match your backend's algorithm
        });
        
        // Add the signed token to the session object
        (session as any).accessToken = accessToken;
        // --- END OF BLOCK ---
      }
      return session
    }
  },
  session: {
    strategy: "jwt"
  }
}

export const { auth, signIn, signOut, handlers } = NextAuth(authOptions)