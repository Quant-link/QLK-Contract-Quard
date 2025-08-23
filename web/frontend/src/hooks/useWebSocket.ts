import { useEffect, useRef, useState, useCallback } from 'react'
import { WebSocketMessage } from '../types'

interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

interface UseWebSocketReturn {
  socket: WebSocket | null
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  sendMessage: (message: any) => void
  reconnect: () => void
  disconnect: () => void
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectAttempts = 5,
  reconnectInterval = 3000
}: UseWebSocketOptions): UseWebSocketReturn {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reconnectCount, setReconnectCount] = useState(0)

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const shouldReconnectRef = useRef(true)

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) {
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setIsConnecting(false)
        setError(null)
        setReconnectCount(0)
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          onMessage?.(message)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setIsConnecting(false)
        setSocket(null)
        onClose?.()

        // Attempt to reconnect if not manually closed
        if (shouldReconnectRef.current && reconnectCount < reconnectAttempts) {
          console.log(`Attempting to reconnect... (${reconnectCount + 1}/${reconnectAttempts})`)
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1)
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
        setIsConnecting(false)
        onError?.(event)
      }

      setSocket(ws)
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      setError('Failed to create WebSocket connection')
      setIsConnecting(false)
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnectAttempts, reconnectInterval, reconnectCount, socket])

  const sendMessage = useCallback((message: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [socket])

  const reconnect = useCallback(() => {
    setReconnectCount(0)
    connect()
  }, [connect])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (socket) {
      socket.close()
    }
  }, [socket])

  useEffect(() => {
    shouldReconnectRef.current = true
    // Temporarily disable WebSocket connections until backend supports it
    // connect()

    return () => {
      shouldReconnectRef.current = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socket) {
        socket.close()
      }
    }
  }, []) // Only run on mount

  return {
    socket,
    isConnected,
    isConnecting,
    error,
    sendMessage,
    reconnect,
    disconnect
  }
}

// Hook for analysis-specific WebSocket connection
export function useAnalysisWebSocket(analysisId?: string) {
  const [status, setStatus] = useState<string>('pending')
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [messages, setMessages] = useState<WebSocketMessage[]>([])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    setMessages(prev => [...prev, message])

    if (message.analysis_id === analysisId) {
      switch (message.type) {
        case 'analysis_status':
          setStatus(message.status || 'pending')
          break
        case 'analysis_progress':
          setProgress(message.data?.progress || 0)
          setCurrentStep(message.data?.step || '')
          break
        case 'analysis_complete':
          setStatus('completed')
          setProgress(100)
          break
        case 'analysis_error':
          setStatus('failed')
          break
      }
    }
  }, [analysisId])

  const wsUrl = `ws://localhost:8000/ws${analysisId ? `/${analysisId}` : ''}`

  const webSocket = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
    onOpen: () => console.log('Analysis WebSocket connected'),
    onClose: () => console.log('Analysis WebSocket disconnected'),
    onError: (error) => console.error('Analysis WebSocket error:', error)
  })

  return {
    ...webSocket,
    status,
    progress,
    currentStep,
    messages
  }
}

// Hook for real-time notifications
export function useNotificationWebSocket() {
  const [notifications, setNotifications] = useState<WebSocketMessage[]>([])
  const [unreadCount, setUnreadCount] = useState(0)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'notification') {
      setNotifications(prev => [message, ...prev])
      setUnreadCount(prev => prev + 1)
    }
  }, [])

  const markAsRead = useCallback(() => {
    setUnreadCount(0)
  }, [])

  const clearNotifications = useCallback(() => {
    setNotifications([])
    setUnreadCount(0)
  }, [])

  const webSocket = useWebSocket({
    url: 'ws://localhost:8000/ws/notifications',
    onMessage: handleMessage,
    onOpen: () => console.log('Notification WebSocket connected'),
    onClose: () => console.log('Notification WebSocket disconnected'),
    onError: (error) => console.error('Notification WebSocket error:', error)
  })

  return {
    ...webSocket,
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications
  }
}
