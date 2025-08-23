import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { TrendingUp, FileText, Clock, AlertTriangle } from 'lucide-react'
import RecentAnalyses from './RecentAnalyses'

interface AnalyticsData {
  total_analyses: number
  severity_distribution: {
    critical: number
    high: number
    medium: number
  }
  language_distribution: Record<string, number>
  supported_languages: string[]
}

interface AnalysisHistory {
  analyses: Array<{
    analysis_id: string
    filename: string
    language: string
    status: string
    risk_score: number
    total_findings: number
    critical_count: number
    high_count: number
    medium_count: number
    low_count: number
    info_count: number
    analysis_duration_ms: number
    created_at: string
  }>
  total: number
}

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [history, setHistory] = useState<AnalysisHistory | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, historyRes] = await Promise.all([
          fetch('/api/statistics'),
          fetch('/api/analyses?limit=20')
        ])
        
        const analyticsData = await analyticsRes.json()
        const historyData = await historyRes.json()
        
        setAnalytics(analyticsData)
        setHistory(historyData)
      } catch (error) {
        console.error('Failed to fetch analytics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!analytics || !history) {
    return (
      <div className="text-center text-muted-foreground">
        Failed to load analytics data
      </div>
    )
  }

  const severityData = [
    { name: 'Critical', value: analytics.severity_distribution.critical, color: '#dc2626' },
    { name: 'High', value: analytics.severity_distribution.high, color: '#ea580c' },
    { name: 'Medium', value: analytics.severity_distribution.medium, color: '#ca8a04' }
  ]

  const languageData = Object.entries(analytics.language_distribution).map(([lang, count]) => ({
    language: lang.toUpperCase(),
    count,
    color: lang === 'sol' ? '#627eea' : lang === 'rs' ? '#ce422b' : '#00add8'
  }))

  const riskTrendData = history.analyses.slice(-10).map((analysis, index) => ({
    index: index + 1,
    risk_score: analysis.risk_score,
    filename: analysis.filename.substring(0, 10) + '...'
  }))

  const avgRiskScore = history.analyses.length > 0 
    ? Math.round(history.analyses.reduce((sum, a) => sum + a.risk_score, 0) / history.analyses.length)
    : 0

  const totalFindings = history.analyses.reduce((sum, a) => sum + a.total_findings, 0)
  const avgAnalysisTime = history.analyses.length > 0
    ? Math.round(history.analyses.reduce((sum, a) => sum + a.analysis_duration_ms, 0) / history.analyses.length)
    : 0

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.total_analyses}</div>
            <p className="text-xs text-muted-foreground">
              Contracts analyzed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Risk Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgRiskScore}/100</div>
            <p className="text-xs text-muted-foreground">
              Security risk level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Findings</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalFindings}</div>
            <p className="text-xs text-muted-foreground">
              Security issues found
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Analysis Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(avgAnalysisTime / 1000).toFixed(1)}s</div>
            <p className="text-xs text-muted-foreground">
              Processing speed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="languages">Languages</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Severity Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Severity Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={severityData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {severityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center gap-4 mt-4">
                  {severityData.map((item) => (
                    <Badge key={item.name} variant="outline" className="flex items-center gap-1">
                      <div 
                        className="w-2 h-2 rounded-full" 
                        style={{ backgroundColor: item.color }}
                      />
                      {item.name}: {item.value}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Language Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Language Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={languageData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="language" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8884d8">
                        {languageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Risk Score Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={riskTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="index" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip 
                      labelFormatter={(value) => `Analysis #${value}`}
                      formatter={(value: any) => [value, 'Risk Score']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="risk_score" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      dot={{ fill: '#8884d8' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="languages" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analytics.supported_languages.map((lang) => (
              <Card key={lang}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{lang.toUpperCase()}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analytics.language_distribution[lang] || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Contracts analyzed
                  </p>
                  <div className="mt-2">
                    <Badge variant="outline">
                      {lang === 'sol' ? 'Solidity' : 
                       lang === 'rs' ? 'Rust/ink!' : 
                       lang === 'go' ? 'Go/Cosmos' : lang}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Recent Analyses */}
      <RecentAnalyses limit={10} compact={true} />
    </div>
  )
}
