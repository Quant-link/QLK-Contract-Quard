import axios, { AxiosResponse } from 'axios'
import { AnalysisResponse, HealthResponse, ApiError } from '@/types'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data)
    }
    
    return Promise.reject(error)
  }
)

// API service functions
export const apiService = {
  // Health check
  async healthCheck(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/api/health')
    return response.data
  },

  // Upload and analyze file
  async analyzeFile(file: File): Promise<AnalysisResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<AnalysisResponse>('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for analysis
    })
    
    return response.data
  },

  // Get analysis result by ID
  async getAnalysisResult(analysisId: string): Promise<AnalysisResponse> {
    const response = await api.get<AnalysisResponse>(`/api/analysis/${analysisId}`)
    return response.data
  },

  // Upload multiple files (if supported in future)
  async analyzeMultipleFiles(files: File[]): Promise<AnalysisResponse[]> {
    const promises = files.map(file => this.analyzeFile(file))
    return Promise.all(promises)
  },
}

// WebSocket service for real-time updates
export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  constructor(private url: string = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.handleReconnect()
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(data: any) {
    const { type } = data
    const listeners = this.listeners.get(type)
    if (listeners) {
      listeners.forEach(callback => callback(data))
    }

    // Also notify 'all' listeners
    const allListeners = this.listeners.get('all')
    if (allListeners) {
      allListeners.forEach(callback => callback(data))
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(console.error)
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  subscribe(eventType: string, callback: (data: any) => void) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(callback)

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType)
      if (listeners) {
        listeners.delete(callback)
        if (listeners.size === 0) {
          this.listeners.delete(eventType)
        }
      }
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Create singleton WebSocket instance
export const wsService = new WebSocketService()

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  } else if (error.message) {
    return error.message
  } else {
    return 'An unexpected error occurred'
  }
}

export const isApiError = (error: any): error is ApiError => {
  return error.response?.data?.detail !== undefined
}

export default api
