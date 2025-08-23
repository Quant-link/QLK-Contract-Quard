import { useEffect, useRef, useState } from 'react'
import { wsService } from '../services/api'

interface UseWebSocketOptions {
  autoConnect?: boolean
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { autoConnect = true, onConnect, onDisconnect, onError } = options
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const subscriptionsRef = useRef<(() => void)[]>([])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      // Cleanup subscriptions
      subscriptionsRef.current.forEach(unsubscribe => unsubscribe())
      subscriptionsRef.current = []
      
      if (wsService.isConnected()) {
        wsService.disconnect()
      }
    }
  }, [autoConnect])

  const connect = async () => {
    try {
      setConnectionError(null)
      await wsService.connect()
      setIsConnected(true)
      onConnect?.()
    } catch (error) {
      setConnectionError('Failed to connect to WebSocket')
      setIsConnected(false)
      onError?.(error as Event)
    }
  }

  const disconnect = () => {
    wsService.disconnect()
    setIsConnected(false)
    onDisconnect?.()
  }

  const subscribe = (eventType: string, callback: (data: any) => void) => {
    const unsubscribe = wsService.subscribe(eventType, callback)
    subscriptionsRef.current.push(unsubscribe)
    return unsubscribe
  }

  const send = (data: any) => {
    wsService.send(data)
  }

  return {
    isConnected,
    connectionError,
    connect,
    disconnect,
    subscribe,
    send,
  }
}
