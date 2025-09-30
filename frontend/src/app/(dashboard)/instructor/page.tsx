'use client'

import { useSession } from 'next-auth/react'

export default function InstructorDashboard() {
  const { data: session } = useSession()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Instructor Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {session?.user?.name}! Manage your courses and students.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">My Courses</h3>
          <p className="text-3xl font-bold text-primary">8</p>
          <p className="text-sm text-muted-foreground">Active courses</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Students</h3>
          <p className="text-3xl font-bold text-primary">156</p>
          <p className="text-sm text-muted-foreground">Total enrolled</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Pending Reviews</h3>
          <p className="text-3xl font-bold text-orange-600">23</p>
          <p className="text-sm text-muted-foreground">Tests to grade</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              📁 Upload Document
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              ❓ Create Question Bank
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              📝 Create New Test
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              👥 Assign Test to Students
            </button>
            <button className="w-full text-left p-3 rounded-md hover:bg-secondary text-sm">
              📊 View Student Progress
            </button>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Recent Tests</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Mathematics Quiz 1</span>
                <p className="text-xs text-muted-foreground">45 students completed</p>
              </div>
              <span className="text-xs text-muted-foreground">2 days ago</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Physics Chapter 3</span>
                <p className="text-xs text-muted-foreground">23 students completed</p>
              </div>
              <span className="text-xs text-muted-foreground">1 week ago</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Chemistry Lab Test</span>
                <p className="text-xs text-muted-foreground">12 students completed</p>
              </div>
              <span className="text-xs text-muted-foreground">2 weeks ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}