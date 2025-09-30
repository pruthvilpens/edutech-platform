import { NextRequest, NextResponse } from 'next/server'
import { hash } from 'bcryptjs'

export async function POST(request: NextRequest) {
  try {
    const { email, password, fullName, role } = await request.json()

    // Hash password
    const hashedPassword = await hash(password, 12)

    // Create user via Hasura
    const response = await fetch(process.env.NEXT_PUBLIC_HASURA_GRAPHQL_URL!, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-hasura-admin-secret': process.env.HASURA_GRAPHQL_ADMIN_SECRET!,
      },
      body: JSON.stringify({
        query: `
          mutation CreateUser($email: String!, $password_hash: String!, $full_name: String!, $role: user_role!) {
            insert_users_one(object: {
              email: $email,
              password_hash: $password_hash,
              full_name: $full_name,
              role: $role
            }) {
              id
              email
              full_name
              role
            }
          }
        `,
        variables: {
          email,
          password_hash: hashedPassword,
          full_name: fullName,
          role
        }
      })
    })

    const { data, errors } = await response.json()

    if (errors) {
      return NextResponse.json(
        { error: errors[0]?.message || 'Failed to create account' },
        { status: 400 }
      )
    }

    if (data?.insert_users_one) {
      return NextResponse.json(
        { message: 'Account created successfully', user: data.insert_users_one },
        { status: 201 }
      )
    }

    return NextResponse.json(
      { error: 'Failed to create account' },
      { status: 400 }
    )
  } catch (error) {
    console.error('Signup error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}