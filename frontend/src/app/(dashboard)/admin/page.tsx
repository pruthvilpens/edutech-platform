'use client'

import { useSession } from 'next-auth/react'

export default function AdminDashboard() {
  const { data: session } = useSession()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {session?.user?.name}! Manage your EduTech platform.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Total Users</h3>
          <p className="text-3xl font-bold text-primary">1,234</p>
          <p className="text-sm text-muted-foreground">+12% from last month</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Active Tests</h3>
          <p className="text-3xl font-bold text-primary">56</p>
          <p className="text-sm text-muted-foreground">+8% from last month</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Documents</h3>
          <p className="text-3xl font-bold text-primary">789</p>
          <p className="text-sm text-muted-foreground">+15% from last month</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">System Health</h3>
          <p className="text-3xl font-bold text-green-600">99.9%</p>
          <p className="text-sm text-muted-foreground">All systems operational</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              📊 View System Analytics
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              👥 Manage Users
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              📝 Review Content
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              ⚙️ System Settings
            </button>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm">New user registered</span>
              <span className="text-xs text-muted-foreground">2 mins ago</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Test completed by student</span>
              <span className="text-xs text-muted-foreground">5 mins ago</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Document uploaded</span>
              <span className="text-xs text-muted-foreground">10 mins ago</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">System backup completed</span>
              <span className="text-xs text-muted-foreground">1 hour ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}