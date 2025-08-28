import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Date formatting utilities
export function formatDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj)
}

export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return formatDate(dateObj)
}

// File size formatting
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Duration formatting
export function formatDuration(milliseconds: number): string {
  if (milliseconds < 1000) return `${milliseconds}ms`
  if (milliseconds < 60000) return `${(milliseconds / 1000).toFixed(1)}s`
  if (milliseconds < 3600000) return `${(milliseconds / 60000).toFixed(1)}m`
  return `${(milliseconds / 3600000).toFixed(1)}h`
}

// Number formatting
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num)
}

// Text utilities
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function capitalizeFirst(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

// Risk score utilities
export function getRiskLevel(score: number): {
  level: string
  color: string
  bgColor: string
} {
  if (score >= 80) return { level: 'Critical', color: 'text-red-600', bgColor: 'bg-red-50' }
  if (score >= 60) return { level: 'High', color: 'text-orange-600', bgColor: 'bg-orange-50' }
  if (score >= 40) return { level: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-50' }
  if (score >= 20) return { level: 'Low', color: 'text-blue-600', bgColor: 'bg-blue-50' }
  return { level: 'Minimal', color: 'text-green-600', bgColor: 'bg-green-50' }
}

// Language utilities
export function getLanguageInfo(extension: string): {
  name: string
  icon: string
  color: string
} {
  switch (extension.toLowerCase()) {
    case 'sol':
      return { name: 'Solidity', icon: '⟠', color: 'text-blue-600 bg-blue-50' }
    case 'rs':
      return { name: 'Rust', icon: '🦀', color: 'text-orange-600 bg-orange-50' }
    case 'go':
      return { name: 'Go', icon: '🐹', color: 'text-cyan-600 bg-cyan-50' }
    default:
      return { name: 'Unknown', icon: '📄', color: 'text-gray-600 bg-gray-50' }
  }
}

// Severity utilities
export function getSeverityColor(severity: string): string {
  switch (severity.toUpperCase()) {
    case 'CRITICAL':
      return 'text-red-600 bg-red-50 border-red-200'
    case 'HIGH':
      return 'text-orange-600 bg-orange-50 border-orange-200'
    case 'MEDIUM':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'LOW':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'INFO':
      return 'text-gray-600 bg-gray-50 border-gray-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getSeverityBadgeColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'destructive'
    case 'high':
      return 'destructive'
    case 'medium':
      return 'secondary'
    case 'low':
      return 'outline'
    case 'info':
      return 'default'
    default:
      return 'default'
  }
}

// File type utilities
export function getFileTypeInfo(filename: string) {
  const extension = filename.toLowerCase().split('.').pop() || ''

  switch (extension) {
    case 'sol':
      return {
        language: 'Solidity',
        icon: '⟠',
        color: 'text-purple-600',
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200',
        description: 'Ethereum Smart Contract'
      }
    case 'rs':
      return {
        language: 'Rust',
        icon: '🦀',
        color: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        description: 'Substrate/ink! Contract'
      }
    case 'go':
      return {
        language: 'Go',
        icon: '🐹',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        description: 'Cosmos SDK Module'
      }
    default:
      return {
        language: 'Unknown',
        icon: '📄',
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        description: 'Unknown File Type'
      }
  }
}

// Performance utilities
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }

    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Validation utilities
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

// Math utilities
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}

// Async utilities
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// ID generation
export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

// String utilities
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// Safe JSON parsing
export function safeJsonParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json)
  } catch {
    return fallback
  }
}
