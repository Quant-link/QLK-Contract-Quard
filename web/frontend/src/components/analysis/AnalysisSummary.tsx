import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { AlertTriangle, Shield, Clock, FileText } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { AnalysisMetadata } from '../../types'
import { formatDate, formatFileSize } from '../../lib/utils'

interface AnalysisSummaryProps {
  metadata: AnalysisMetadata
  timestamp: string
}

export default function AnalysisSummary({ metadata, timestamp }: AnalysisSummaryProps) {
  const severityData = [
    { name: 'Critical', value: metadata.critical_count, color: '#dc2626' },
    { name: 'High', value: metadata.high_count, color: '#ea580c' },
    { name: 'Medium', value: metadata.medium_count, color: '#ca8a04' },
    { name: 'Low', value: metadata.low_count, color: '#2563eb' },
    { name: 'Info', value: metadata.info_count, color: '#6b7280' }
  ].filter(item => item.value > 0)

  const barData = [
    { severity: 'Critical', count: metadata.critical_count, color: '#dc2626' },
    { severity: 'High', count: metadata.high_count, color: '#ea580c' },
    { severity: 'Medium', count: metadata.medium_count, color: '#ca8a04' },
    { severity: 'Low', count: metadata.low_count, color: '#2563eb' },
    { severity: 'Info', count: metadata.info_count, color: '#6b7280' }
  ]

  const getRiskLevel = () => {
    if (metadata.critical_count > 0) return { level: 'Critical', color: 'text-red-600', bgColor: 'bg-red-50' }
    if (metadata.high_count > 0) return { level: 'High', color: 'text-orange-600', bgColor: 'bg-orange-50' }
    if (metadata.medium_count > 0) return { level: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-50' }
    if (metadata.low_count > 0) return { level: 'Low', color: 'text-blue-600', bgColor: 'bg-blue-50' }
    return { level: 'Clean', color: 'text-green-600', bgColor: 'bg-green-50' }
  }

  const riskLevel = getRiskLevel()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Overall Risk */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Overall Risk</CardTitle>
          <AlertTriangle className={`h-4 w-4 ${riskLevel.color}`} />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${riskLevel.color}`}>
            {riskLevel.level}
          </div>
          <p className="text-xs text-muted-foreground">
            Based on {metadata.total_findings} findings
          </p>
        </CardContent>
      </Card>

      {/* Total Findings */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Findings</CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metadata.total_findings}</div>
          <p className="text-xs text-muted-foreground">
            Security issues detected
          </p>
        </CardContent>
      </Card>

      {/* File Info */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">File Analyzed</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold truncate" title={metadata.filename}>
            {metadata.filename}
          </div>
          <p className="text-xs text-muted-foreground">
            {formatFileSize(metadata.file_size)}
          </p>
        </CardContent>
      </Card>

      {/* Analysis Time */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Analysis Time</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold">
            {metadata.analysis_duration_ms 
              ? `${(metadata.analysis_duration_ms / 1000).toFixed(1)}s`
              : 'N/A'
            }
          </div>
          <p className="text-xs text-muted-foreground">
            {formatDate(timestamp)}
          </p>
        </CardContent>
      </Card>

      {/* Severity Distribution - Pie Chart */}
      {severityData.length > 0 && (
        <Card className="md:col-span-2">
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
            <div className="flex flex-wrap justify-center gap-2 mt-4">
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
      )}

      {/* Severity Breakdown - Bar Chart */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Findings by Severity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="severity" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8">
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
