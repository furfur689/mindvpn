'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Server, 
  Users, 
  Activity, 
  Globe, 
  CheckCircle, 
  AlertCircle,
  Clock,
  TrendingUp
} from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'

interface DashboardStats {
  nodes: {
    total: number
    online: number
    offline: number
  }
  users: {
    total: number
    active: number
  }
  tasks: {
    total: number
    running: number
    completed: number
    failed: number
  }
  inbounds: {
    total: number
    active: number
  }
}

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>('dashboard-stats', async () => {
    const response = await axios.get('/api/metrics/dashboard')
    return response.data
  }, {
    refetchInterval: 30000, // Обновляем каждые 30 секунд
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your MindVPN infrastructure
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Nodes</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.nodes.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">{stats?.nodes.online || 0} online</span>
              {' • '}
              <span className="text-red-600">{stats?.nodes.offline || 0} offline</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.users.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">{stats?.users.active || 0} active</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasks</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.tasks.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-blue-600">{stats?.tasks.running || 0} running</span>
              {' • '}
              <span className="text-green-600">{stats?.tasks.completed || 0} completed</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inbounds</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.inbounds.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">{stats?.inbounds.active || 0} active</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest tasks and system events
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Task completed</span>
                  </div>
                  <Badge variant="secondary">APPLY_INBOUND</Badge>
                  <span className="text-sm text-muted-foreground">
                    Node-{i} • 2 minutes ago
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common operations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button className="w-full justify-start" variant="outline">
              <Server className="mr-2 h-4 w-4" />
              Add Node
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Globe className="mr-2 h-4 w-4" />
              Create Inbound
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Users className="mr-2 h-4 w-4" />
              Add User
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Activity className="mr-2 h-4 w-4" />
              View Tasks
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
