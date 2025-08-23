import { useEffect, useState } from 'react'
import { CheckCircle, Clock, AlertTriangle, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'

interface AnalysisStep {
  id: string
  name: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  duration?: number
}

interface AnalysisProgressProps {
  isAnalyzing: boolean
  currentStep?: string
  onComplete?: () => void
}

export default function AnalysisProgress({
  isAnalyzing,
  currentStep,
  onComplete
}: AnalysisProgressProps) {
  const [steps, setSteps] = useState<AnalysisStep[]>([
    { id: 'upload', name: 'File Upload', status: 'completed' },
    { id: 'parse', name: 'Parsing Contract', status: 'pending' },
    { id: 'ast', name: 'AST Analysis', status: 'pending' },
    { id: 'security', name: 'Security Checks', status: 'pending' },
    { id: 'report', name: 'Generating Report', status: 'pending' }
  ])

  const [, setCurrentStepIndex] = useState(0)

  useEffect(() => {
    if (!isAnalyzing) return

    const interval = setInterval(() => {
      setSteps(prevSteps => {
        const newSteps = [...prevSteps]
        const currentIndex = newSteps.findIndex(step => step.status === 'in_progress')
        
        if (currentIndex !== -1) {
          // Complete current step
          newSteps[currentIndex].status = 'completed'
          newSteps[currentIndex].duration = Math.random() * 2000 + 500 // Random duration
          
          // Start next step
          if (currentIndex + 1 < newSteps.length) {
            newSteps[currentIndex + 1].status = 'in_progress'
            setCurrentStepIndex(currentIndex + 1)
          } else {
            // All steps completed
            setTimeout(() => onComplete?.(), 500)
          }
        } else {
          // Start first pending step
          const firstPending = newSteps.findIndex(step => step.status === 'pending')
          if (firstPending !== -1) {
            newSteps[firstPending].status = 'in_progress'
            setCurrentStepIndex(firstPending)
          }
        }
        
        return newSteps
      })
    }, 1500 + Math.random() * 1000) // Random interval between 1.5-2.5s

    return () => clearInterval(interval)
  }, [isAnalyzing, onComplete])

  const getStepIcon = (step: AnalysisStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'in_progress':
        return <Loader2 className="h-5 w-5 text-Quantlink-cyan animate-spin" />
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getStepBadge = (step: AnalysisStep) => {
    switch (step.status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>
      case 'in_progress':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">In Progress</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  const completedSteps = steps.filter(step => step.status === 'completed').length
  const totalSteps = steps.length
  const progressPercentage = (completedSteps / totalSteps) * 100

  if (!isAnalyzing && completedSteps === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Analysis Progress</span>
          <span className="text-sm font-normal text-muted-foreground">
            {completedSteps}/{totalSteps} steps completed
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>

        {/* Step Details */}
        <div className="space-y-4">
          {steps.map((step) => (
            <div
              key={step.id}
              className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                step.status === 'in_progress' 
                  ? 'bg-blue-50 border-blue-200' 
                  : step.status === 'completed'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-muted/30'
              }`}
            >
              <div className="flex items-center space-x-3">
                {getStepIcon(step)}
                <div>
                  <p className="font-medium">{step.name}</p>
                  {step.duration && (
                    <p className="text-xs text-muted-foreground">
                      Completed in {(step.duration / 1000).toFixed(1)}s
                    </p>
                  )}
                </div>
              </div>
              
              {getStepBadge(step)}
            </div>
          ))}
        </div>

        {/* Current Step Details */}
        {isAnalyzing && currentStep && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center space-x-2">
              <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
              <p className="text-sm font-medium text-blue-900">
                {currentStep}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
