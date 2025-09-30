import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { compare } from "bcryptjs"

export const { auth, signIn, signOut, handlers } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  basePath: '/api/auth',
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
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

          const { data } = await response.json()
          const user = data?.users?.[0]

          if (!user || !user.is_active) {
            return null
          }

          // Verify password
          const isValidPassword = await compare(credentials.password as string, user.password_hash)
          
          if (!isValidPassword) {
            return null
          }

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
      if (token) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    }
  },
  session: {
    strategy: "jwt"
  }
})