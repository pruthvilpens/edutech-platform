'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import TelegramIntegration from '@/components/features/TelegramIntegration'

interface SettingsTab {
  id: string
  name: string
  icon: string
}

const settingsTabs: SettingsTab[] = [
  { id: 'profile', name: 'Profile', icon: '👤' },
  { id: 'telegram', name: 'Telegram Integration', icon: '📱' },
  { id: 'notifications', name: 'Notifications', icon: '🔔' },
  { id: 'security', name: 'Security', icon: '🔒' },
]

export default function SettingsPage() {
  const { data: session } = useSession()
  const [activeTab, setActiveTab] = useState('profile')

  if (!session) {
    return <div>Please log in to access settings.</div>
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Profile Settings</h2>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    defaultValue={session.user?.name || ''}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    disabled
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    defaultValue={session.user?.email || ''}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    disabled
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <input
                    type="text"
                    defaultValue={session.user?.role || ''}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    disabled
                  />
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'telegram':
        return <TelegramIntegration />
      
      case 'notifications':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Notification Settings</h2>
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600">Notification preferences will be available soon.</p>
            </div>
          </div>
        )
      
      case 'security':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Security Settings</h2>
            <div className="bg-white p-6 rounded-lg shadow">
              <p className="text-gray-600">Security settings will be available soon.</p>
            </div>
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="flex space-x-8">
        {/* Settings Navigation */}
        <div className="w-64 flex-shrink-0">
          <nav className="bg-white rounded-lg shadow">
            <div className="p-4">
              <ul className="space-y-1">
                {settingsTabs.map((tab) => (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <span className="mr-3">{tab.icon}</span>
                      {tab.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </nav>
        </div>

        {/* Settings Content */}
        <div className="flex-1">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}