import { cn } from '../../lib/utils'

interface LoadingAnimationProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

export function LoadingAnimation({ size = 'md', className, text }: LoadingAnimationProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className={cn('flex flex-col items-center justify-center space-y-2', className)}>
      <div className="relative">
        <div className={cn(
          'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
          sizeClasses[size]
        )} />
        <div className={cn(
          'absolute top-0 left-0 animate-ping rounded-full border-2 border-blue-400 opacity-75',
          sizeClasses[size]
        )} />
      </div>
      {text && (
        <p className="text-sm text-muted-foreground animate-pulse">{text}</p>
      )}
    </div>
  )
}

export function SkeletonLoader({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse bg-gray-200 rounded', className)} />
  )
}

export function CardSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <SkeletonLoader className="h-4 w-3/4" />
      <SkeletonLoader className="h-4 w-1/2" />
      <SkeletonLoader className="h-20 w-full" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      <SkeletonLoader className="h-8 w-full" />
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonLoader key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}
