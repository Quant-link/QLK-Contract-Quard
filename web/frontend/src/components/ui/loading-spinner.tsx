import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

export function LoadingSpinner({ size = 'md', className, text }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  }

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div className="flex flex-col items-center space-y-2">
        <Loader2 className={cn('animate-spin text-primary', sizeClasses[size])} />
        {text && (
          <p className="text-sm text-muted-foreground">{text}</p>
        )}
      </div>
    </div>
  )
}

export function PageLoader({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <LoadingSpinner size="lg" text={text} />
    </div>
  )
}

export function InlineLoader({ text }: { text?: string }) {
  return (
    <div className="flex items-center space-x-2">
      <Loader2 className="h-4 w-4 animate-spin" />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </div>
  )
}
