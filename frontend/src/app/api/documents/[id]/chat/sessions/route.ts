import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth()
    
    if (!session?.accessToken) {
      console.error('No session or accessToken:', { hasSession: !!session, hasToken: !!session?.accessToken })
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    console.log('Fetching chat sessions for document:', params.id)
    const backendUrl = `${BACKEND_URL}/api/documents/${params.id}/chat/sessions`
    console.log('Backend URL:', backendUrl)

    const response = await fetch(backendUrl, {
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    console.log('Backend response status:', response.status)

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Backend error:', errorData)
      return NextResponse.json(
        { error: errorData },
        { status: response.status }
      )
    }

    const data = await response.json()
    console.log('Chat sessions data:', data)
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Chat sessions API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    )
  }
}