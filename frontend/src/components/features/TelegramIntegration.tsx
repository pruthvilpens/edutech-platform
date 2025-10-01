'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'

interface TelegramLinkStatus {
  is_linked: boolean
  telegram_username?: string
  telegram_first_name?: string
  linked_at?: string
}

export default function TelegramIntegration() {
  const { data: session } = useSession()
  const [linkStatus, setLinkStatus] = useState<TelegramLinkStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [linkToken, setLinkToken] = useState('')
  const [isLinking, setIsLinking] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)

  // Fetch current Telegram link status
  const fetchLinkStatus = async () => {
    try {
      const response = await fetch('/api/telegram/status', {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setLinkStatus(data)
      }
    } catch (error) {
      console.error('Failed to fetch Telegram link status:', error)
    } finally {
      setLoading(false)
    }
  }

  // Link account with token
  const handleLinkAccount = async () => {
    if (!linkToken.trim()) {
      setMessage({ type: 'error', text: 'Please enter a valid token' })
      return
    }

    setIsLinking(true)
    setMessage(null)

    try {
      const response = await fetch('/api/telegram/link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.accessToken}`,
        },
        body: JSON.stringify({ token: linkToken }),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: 'Telegram account linked successfully!' })
        setLinkToken('')
        await fetchLinkStatus() // Refresh status
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to link account' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' })
    } finally {
      setIsLinking(false)
    }
  }

  // Unlink account
  const handleUnlinkAccount = async () => {
    setIsLinking(true)
    setMessage(null)

    try {
      const response = await fetch('/api/telegram/unlink', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: 'Telegram account unlinked successfully!' })
        await fetchLinkStatus() // Refresh status
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to unlink account' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' })
    } finally {
      setIsLinking(false)
    }
  }

  useEffect(() => {
    if (session) {
      fetchLinkStatus()
    }
  }, [session])

  if (loading) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Telegram Integration</h2>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="animate-pulse">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Telegram Integration</h2>
      
      {/* Status Card */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium">Telegram Account Status</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            linkStatus?.is_linked 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {linkStatus?.is_linked ? 'Connected' : 'Not Connected'}
          </div>
        </div>

        {linkStatus?.is_linked ? (
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-green-400 text-xl">✅</span>
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-green-800">
                    Successfully Connected
                  </h4>
                  <div className="mt-2 text-sm text-green-700">
                    <p><strong>Username:</strong> @{linkStatus.telegram_username || 'N/A'}</p>
                    <p><strong>Name:</strong> {linkStatus.telegram_first_name || 'N/A'}</p>
                    <p><strong>Connected:</strong> {linkStatus.linked_at ? new Date(linkStatus.linked_at).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <button
                onClick={handleUnlinkAccount}
                disabled={isLinking}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLinking ? 'Unlinking...' : 'Unlink Account'}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-blue-400 text-xl">📱</span>
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-blue-800">
                    Connect Your Telegram Account
                  </h4>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>Link your Telegram account to take tests directly from Telegram!</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-gray-50 p-4 rounded-md">
              <h4 className="text-sm font-medium text-gray-800 mb-2">How to link your account:</h4>
              <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
                <li>Open Telegram and search for <strong>@yeebitz_bot</strong></li>
                <li>Send <code className="bg-gray-200 px-1 rounded">/start</code> to the bot</li>
                <li>Send <code className="bg-gray-200 px-1 rounded">/link</code> to get your linking token</li>
                <li>Copy the token and paste it below</li>
                <li>Click "Link Account" to complete the process</li>
              </ol>
            </div>

            {/* Token Input */}
            <div className="space-y-3">
              <label htmlFor="linkToken" className="block text-sm font-medium text-gray-700">
                Telegram Link Token
              </label>
              <input
                type="text"
                id="linkToken"
                value={linkToken}
                onChange={(e) => setLinkToken(e.target.value)}
                placeholder="Enter your token from @yeebitz_bot"
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={handleLinkAccount}
                disabled={isLinking || !linkToken.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLinking ? 'Linking...' : 'Link Account'}
              </button>
            </div>
          </div>
        )}

        {/* Message Display */}
        {message && (
          <div className={`mt-4 p-4 rounded-md ${
            message.type === 'success' ? 'bg-green-50 text-green-800' :
            message.type === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {message.text}
          </div>
        )}
      </div>

      {/* Benefits Card */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Benefits of Telegram Integration</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            Take tests directly from Telegram
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            Receive instant notifications about new tests
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            View your results and progress
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            Access study materials on the go
          </li>
        </ul>
      </div>
    </div>
  )
}