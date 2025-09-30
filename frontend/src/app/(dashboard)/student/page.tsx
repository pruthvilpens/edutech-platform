'use client'

import { useSession } from 'next-auth/react'

export default function StudentDashboard() {
  const { data: session } = useSession()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Student Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {session?.user?.name}! Continue your learning journey.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Assigned Tests</h3>
          <p className="text-3xl font-bold text-primary">5</p>
          <p className="text-sm text-muted-foreground">Pending completion</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Completed Tests</h3>
          <p className="text-3xl font-bold text-green-600">12</p>
          <p className="text-sm text-muted-foreground">This month</p>
        </div>
        
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-2">Average Score</h3>
          <p className="text-3xl font-bold text-blue-600">87%</p>
          <p className="text-sm text-muted-foreground">+5% improvement</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Upcoming Tests</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-secondary rounded-md">
              <div>
                <span className="text-sm font-medium">Mathematics Quiz 2</span>
                <p className="text-xs text-muted-foreground">Due: Tomorrow</p>
              </div>
              <button className="text-xs bg-primary text-primary-foreground px-3 py-1 rounded">
                Start Test
              </button>
            </div>
            <div className="flex justify-between items-center p-3 bg-secondary rounded-md">
              <div>
                <span className="text-sm font-medium">Physics Chapter 4</span>
                <p className="text-xs text-muted-foreground">Due: 3 days</p>
              </div>
              <button className="text-xs bg-primary text-primary-foreground px-3 py-1 rounded">
                Start Test
              </button>
            </div>
            <div className="flex justify-between items-center p-3 bg-secondary rounded-md">
              <div>
                <span className="text-sm font-medium">Chemistry Lab Review</span>
                <p className="text-xs text-muted-foreground">Due: 1 week</p>
              </div>
              <button className="text-xs bg-secondary text-secondary-foreground px-3 py-1 rounded">
                View Details
              </button>
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold text-card-foreground mb-4">Recent Results</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Mathematics Quiz 1</span>
                <p className="text-xs text-muted-foreground">Completed yesterday</p>
              </div>
              <span className="text-sm font-bold text-green-600">92%</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Physics Chapter 3</span>
                <p className="text-xs text-muted-foreground">Completed 3 days ago</p>
              </div>
              <span className="text-sm font-bold text-blue-600">85%</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-medium">Chemistry Basics</span>
                <p className="text-xs text-muted-foreground">Completed 1 week ago</p>
              </div>
              <span className="text-sm font-bold text-yellow-600">78%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-card p-6 rounded-lg border">
        <h3 className="text-lg font-semibold text-card-foreground mb-4">Study Progress</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm">Mathematics</span>
              <span className="text-sm text-muted-foreground">85%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm">Physics</span>
              <span className="text-sm text-muted-foreground">72%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '72%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm">Chemistry</span>
              <span className="text-sm text-muted-foreground">68%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '68%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}