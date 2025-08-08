import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Bot, 
  Send, 
  Globe, 
  MousePointer, 
  Keyboard, 
  Eye, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Play,
  Square,
  History,
  Settings,
  Wifi,
  WifiOff,
  RefreshCw
} from 'lucide-react'
import { useAgent } from './hooks/useAgent'
import './App.css'

function App() {
  const [task, setTask] = useState('')
  const [maxIterations, setMaxIterations] = useState(10)
  
  const {
    status,
    isRunning,
    taskHistory,
    currentStep,
    totalSteps,
    logs,
    currentObservation,
    error,
    isConnected,
    executeTask,
    stopTask,
    checkConnection,
    progress
  } = useAgent()

  const capabilities = [
    { name: 'Navigate', icon: Globe, color: 'bg-blue-500', description: 'Browse websites' },
    { name: 'Click', icon: MousePointer, color: 'bg-green-500', description: 'Click elements' },
    { name: 'Type', icon: Keyboard, color: 'bg-purple-500', description: 'Fill forms' },
    { name: 'Read DOM', icon: Eye, color: 'bg-orange-500', description: 'Extract content' },
    { name: 'Wait', icon: Clock, color: 'bg-gray-500', description: 'Pause execution' },
    { name: 'Screenshot', icon: Eye, color: 'bg-pink-500', description: 'Capture screens' }
  ]

  const handleSubmit = async () => {
    if (!task.trim()) return
    await executeTask(task, maxIterations)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />
      case 'running': return <AlertCircle className="w-4 h-4 text-blue-500 animate-pulse" />
      default: return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'secondary'
      case 'failed': return 'destructive'
      case 'running': return 'default'
      default: return 'outline'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Autonomous Agent</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI-powered browser automation</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={isConnected ? 'secondary' : 'destructive'}>
                {isConnected ? <Wifi className="w-3 h-3 mr-1" /> : <WifiOff className="w-3 h-3 mr-1" />}
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
              <Badge variant={getStatusColor(status)}>
                {getStatusIcon(status)}
                <span className="ml-1 capitalize">{status}</span>
              </Badge>
              <Button variant="outline" size="sm" onClick={checkConnection}>
                <RefreshCw className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Connection Error Alert */}
        {error && (
          <Alert className="mb-6" variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error}
              <Button 
                variant="outline" 
                size="sm" 
                className="ml-2" 
                onClick={checkConnection}
              >
                Retry Connection
              </Button>
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Chat Interface */}
          <div className="lg:col-span-2 space-y-6">
            {/* Greeting */}
            <div className="text-center py-8">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Hello</h2>
              <p className="text-lg text-gray-600 dark:text-gray-300">What can I do for you?</p>
              {!isConnected && (
                <p className="text-sm text-orange-600 dark:text-orange-400 mt-2">
                  Running in demo mode - start the backend server for full functionality
                </p>
              )}
            </div>

            {/* Task Input */}
            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <Textarea
                    placeholder="Give the agent a task to work on..."
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    className="min-h-[120px] text-lg"
                    disabled={isRunning}
                  />
                  <div className="flex justify-between items-center">
                    <div className="flex space-x-2">
                      {capabilities.slice(0, 4).map((cap, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          <cap.icon className="w-3 h-3 mr-1" />
                          {cap.name}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="text-sm text-gray-500">
                        Max steps: {maxIterations}
                      </div>
                      {isRunning ? (
                        <Button onClick={stopTask} variant="destructive">
                          <Square className="w-4 h-4 mr-2" />
                          Stop
                        </Button>
                      ) : (
                        <Button onClick={handleSubmit} disabled={!task.trim()}>
                          <Send className="w-4 h-4 mr-2" />
                          Execute
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Capabilities Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {capabilities.map((capability, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4 text-center">
                    <div className={`w-12 h-12 ${capability.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                      <capability.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{capability.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{capability.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Progress Section */}
            {(isRunning || status === 'completed' || status === 'failed') && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Play className="w-5 h-5 mr-2" />
                    Task Execution
                  </CardTitle>
                  <CardDescription>
                    {isRunning 
                      ? 'Agent is working on your task...' 
                      : status === 'completed' 
                        ? 'Task completed successfully!' 
                        : 'Task execution failed'
                    }
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Progress</span>
                        <span>{currentStep}/{totalSteps} steps</span>
                      </div>
                      <Progress value={progress} className="h-2" />
                    </div>
                    
                    {currentObservation && (
                      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">Current Observation:</p>
                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{currentObservation}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Task History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <History className="w-5 h-5 mr-2" />
                  Recent Tasks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  <div className="space-y-3">
                    {taskHistory.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                        No tasks executed yet
                      </p>
                    ) : (
                      taskHistory.map((item) => (
                        <div key={item.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                          {getStatusIcon(item.status)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {item.task}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{item.time}</p>
                            {item.executionTime && (
                              <p className="text-xs text-gray-400">
                                {item.executionTime.toFixed(2)}s
                              </p>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Execution Logs */}
            {logs.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Execution Logs</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px]">
                    <div className="space-y-2">
                      {logs.map((log, index) => (
                        <div key={index} className="text-xs">
                          <div className="flex justify-between items-center">
                            <span className="font-mono text-gray-600 dark:text-gray-400">[{log.time}]</span>
                            <Badge variant="outline" className="text-xs">
                              Step {log.step}
                              {log.success === false && <XCircle className="w-3 h-3 ml-1 text-red-500" />}
                            </Badge>
                          </div>
                          <p className="text-gray-900 dark:text-white mt-1">{log.message}</p>
                          {index < logs.length - 1 && <Separator className="my-2" />}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

