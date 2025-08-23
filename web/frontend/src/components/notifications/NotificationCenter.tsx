import { useState, useEffect } from 'react'
import { Bell, X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { ScrollArea } from '../ui/scroll-area'
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover'
import { useNotificationWebSocket } from '../../hooks/useWebSocket'
import { formatDistanceToNow } from 'date-fns'

interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
  action?: {
    label: string
    url: string
  }
  metadata?: {
    analysis_id?: string
    filename?: string
    risk_score?: number
  }
}

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'success',
      title: 'Analysis Complete',
      message: 'Security analysis for contract.sol completed successfully',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      read: false,
      action: {
        label: 'View Report',
        url: '/analysis/abc123'
      },
      metadata: {
        analysis_id: 'abc123',
        filename: 'contract.sol',
        risk_score: 85
      }
    },
    {
      id: '2',
      type: 'warning',
      title: 'High Risk Detected',
      message: 'Critical vulnerabilities found in token.rs',
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      read: false,
      metadata: {
        analysis_id: 'def456',
        filename: 'token.rs',
        risk_score: 95
      }
    },
    {
      id: '3',
      type: 'info',
      title: 'System Update',
      message: 'New vulnerability detectors have been added',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      read: true
    }
  ])

  const [isOpen, setIsOpen] = useState(false)
  
  const { isConnected, notifications: wsNotifications } = useNotificationWebSocket()

  const unreadCount = notifications.filter(n => !n.read).length

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      case 'info':
        return <Info className="h-4 w-4 text-blue-600" />
      default:
        return <Info className="h-4 w-4 text-gray-600" />
    }
  }

  const getNotificationBorderColor = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return 'border-l-green-500'
      case 'warning':
        return 'border-l-yellow-500'
      case 'error':
        return 'border-l-red-500'
      case 'info':
        return 'border-l-blue-500'
      default:
        return 'border-l-gray-500'
    }
  }

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id
          ? { ...notification, read: true }
          : notification
      )
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    )
  }

  const removeNotification = (id: string) => {
    setNotifications(prev =>
      prev.filter(notification => notification.id !== id)
    )
  }

  const clearAll = () => {
    setNotifications([])
  }

  useEffect(() => {
    // Convert WebSocket messages to notifications
    wsNotifications.forEach(wsMessage => {
      if (wsMessage.type === 'notification') {
        const notification: Notification = {
          id: Date.now().toString(),
          type: wsMessage.data?.type || 'info',
          title: wsMessage.data?.title || 'Notification',
          message: wsMessage.message || '',
          timestamp: wsMessage.timestamp,
          read: false,
          metadata: wsMessage.data?.metadata
        }
        
        setNotifications(prev => [notification, ...prev])
      }
    })
  }, [wsNotifications])

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent className="w-96 p-0" align="end">
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Notifications</CardTitle>
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xs text-muted-foreground">
                    {isConnected ? 'Live' : 'Offline'}
                  </span>
                </div>
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={markAllAsRead}
                    className="text-xs"
                  >
                    Mark all read
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">
                <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            ) : (
              <ScrollArea className="h-96">
                <div className="space-y-1 p-2">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-3 rounded-lg border-l-4 cursor-pointer transition-colors hover:bg-muted/50 ${
                        getNotificationBorderColor(notification.type)
                      } ${notification.read ? 'opacity-60' : ''}`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <div className="flex-shrink-0 mt-0.5">
                            {getNotificationIcon(notification.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium truncate">
                                {notification.title}
                              </h4>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 ml-2" />
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {notification.message}
                            </p>
                            
                            {notification.metadata && (
                              <div className="flex items-center space-x-2 mt-2">
                                {notification.metadata.filename && (
                                  <Badge variant="outline" className="text-xs">
                                    {notification.metadata.filename}
                                  </Badge>
                                )}
                                {notification.metadata.risk_score && (
                                  <Badge 
                                    variant={notification.metadata.risk_score >= 80 ? 'destructive' : 'secondary'}
                                    className="text-xs"
                                  >
                                    Risk: {notification.metadata.risk_score}/100
                                  </Badge>
                                )}
                              </div>
                            )}
                            
                            <div className="flex items-center justify-between mt-2">
                              <span className="text-xs text-muted-foreground">
                                {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
                              </span>
                              
                              {notification.action && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="text-xs h-6 px-2"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    window.location.href = notification.action!.url
                                  }}
                                >
                                  {notification.action.label}
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 ml-2"
                          onClick={(e) => {
                            e.stopPropagation()
                            removeNotification(notification.id)
                          }}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}
            
            {notifications.length > 0 && (
              <div className="border-t p-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearAll}
                  className="w-full text-xs"
                >
                  Clear all notifications
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </PopoverContent>
    </Popover>
  )
}
