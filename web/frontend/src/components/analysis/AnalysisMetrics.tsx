import { useState, useEffect } from 'react'
import { Activity, Clock, FileText, Shield, TrendingUp, Users } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'

interface AnalysisMetricsProps {
  totalAnalyses?: number
  avgAnalysisTime?: number
  successRate?: number
  activeUsers?: number
}

export default function AnalysisMetrics({
  totalAnalyses = 0,
  avgAnalysisTime = 0,
  successRate = 0,
  activeUsers = 0
}: AnalysisMetricsProps) {
  const [metrics, setMetrics] = useState({
    totalAnalyses,
    avgAnalysisTime,
    successRate,
    activeUsers
  })

  // Simulate real-time metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        totalAnalyses: prev.totalAnalyses + Math.floor(Math.random() * 3),
        avgAnalysisTime: Math.max(1, prev.avgAnalysisTime + (Math.random() - 0.5) * 0.5),
        successRate: Math.min(100, Math.max(85, prev.successRate + (Math.random() - 0.5) * 2)),
        activeUsers: Math.max(0, prev.activeUsers + Math.floor((Math.random() - 0.5) * 5))
      }))
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Analyses */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.totalAnalyses.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            <TrendingUp className="inline h-3 w-3 mr-1" />
            +12% from last month
          </p>
        </CardContent>
      </Card>

      {/* Average Analysis Time */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Analysis Time</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatDuration(metrics.avgAnalysisTime)}</div>
          <p className="text-xs text-muted-foreground">
            -8% faster than average
          </p>
        </CardContent>
      </Card>

      {/* Success Rate */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.successRate.toFixed(1)}%</div>
          <Progress value={metrics.successRate} className="mt-2" />
          <p className="text-xs text-muted-foreground mt-2">
            {metrics.successRate >= 95 ? (
              <Badge variant="success" className="text-xs">Excellent</Badge>
            ) : metrics.successRate >= 90 ? (
              <Badge variant="info" className="text-xs">Good</Badge>
            ) : (
              <Badge variant="warning" className="text-xs">Needs Attention</Badge>
            )}
          </p>
        </CardContent>
      </Card>

      {/* Active Users */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.activeUsers}</div>
          <div className="flex items-center space-x-2 mt-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-muted-foreground">Online now</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card className="md:col-span-2 lg:col-span-4">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>System Status</span>
          </CardTitle>
          <CardDescription>
            Real-time system health and performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Response Time</span>
                <Badge variant="success">Healthy</Badge>
              </div>
              <Progress value={85} className="h-2" />
              <p className="text-xs text-muted-foreground">Average: 245ms</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Analysis Queue</span>
                <Badge variant="info">Normal</Badge>
              </div>
              <Progress value={35} className="h-2" />
              <p className="text-xs text-muted-foreground">3 jobs pending</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Error Rate</span>
                <Badge variant="success">Low</Badge>
              </div>
              <Progress value={5} className="h-2" />
              <p className="text-xs text-muted-foreground">0.2% last 24h</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
