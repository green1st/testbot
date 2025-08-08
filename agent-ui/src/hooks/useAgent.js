import { useState, useEffect, useCallback } from 'react'
import { agentAPI } from '../services/api'

export const useAgent = () => {
  const [status, setStatus] = useState('idle') // idle, running, completed, failed
  const [isRunning, setIsRunning] = useState(false)
  const [currentTask, setCurrentTask] = useState(null)
  const [taskHistory, setTaskHistory] = useState([])
  const [currentStep, setCurrentStep] = useState(0)
  const [totalSteps, setTotalSteps] = useState(0)
  const [logs, setLogs] = useState([])
  const [currentObservation, setCurrentObservation] = useState('')
  const [error, setError] = useState(null)
  const [isConnected, setIsConnected] = useState(false)

  // Check backend connection
  const checkConnection = useCallback(async () => {
    try {
      await agentAPI.healthCheck()
      setIsConnected(true)
      setError(null)
    } catch (err) {
      setIsConnected(false)
      setError('Cannot connect to agent backend. Make sure the server is running on port 8000.')
    }
  }, [])

  // Execute task
  const executeTask = useCallback(async (taskText, maxIterations = 10) => {
    if (!taskText.trim()) return

    setIsRunning(true)
    setStatus('running')
    setCurrentStep(0)
    setTotalSteps(maxIterations)
    setLogs([])
    setError(null)
    setCurrentObservation('')

    const taskData = {
      goal: taskText,
      max_iterations: maxIterations,
      timeout: 300
    }

    setCurrentTask(taskData)

    try {
      if (isConnected) {
        // Real backend execution
        const response = await agentAPI.executeTask(taskData)
        
        // Process response
        setStatus(response.status)
        setCurrentStep(response.steps?.length || 0)
        setTotalSteps(response.steps?.length || maxIterations)
        
        // Convert steps to logs
        const newLogs = response.steps?.map((step, index) => ({
          step: index + 1,
          message: step.tool_call?.tool_name || 'Unknown action',
          time: new Date().toLocaleTimeString(),
          success: step.success,
          observation: step.observation
        })) || []
        
        setLogs(newLogs)
        
        if (newLogs.length > 0) {
          setCurrentObservation(newLogs[newLogs.length - 1].observation || '')
        }

        // Add to history
        setTaskHistory(prev => [{
          id: Date.now(),
          task: taskText,
          status: response.status,
          time: 'Just now',
          executionTime: response.execution_time
        }, ...prev.slice(0, 9)]) // Keep only last 10 items

      } else {
        // Fallback simulation when backend is not available
        await simulateTaskExecution(taskText, maxIterations)
      }

    } catch (err) {
      console.error('Task execution failed:', err)
      setError(err.message)
      setStatus('failed')
      
      // Add failed task to history
      setTaskHistory(prev => [{
        id: Date.now(),
        task: taskText,
        status: 'failed',
        time: 'Just now',
        error: err.message
      }, ...prev.slice(0, 9)])
    } finally {
      setIsRunning(false)
      setCurrentTask(null)
    }
  }, [isConnected])

  // Simulate task execution (fallback when backend is not available)
  const simulateTaskExecution = async (taskText, maxIterations) => {
    const steps = [
      'Initializing browser...',
      'Navigating to target URL...',
      'Reading page content...',
      'Executing planned action...',
      'Task completed successfully!'
    ]
    
    for (let i = 0; i < Math.min(steps.length, maxIterations); i++) {
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setCurrentStep(i + 1)
      setLogs(prev => [...prev, {
        step: i + 1,
        message: steps[i],
        time: new Date().toLocaleTimeString(),
        success: true
      }])
      setCurrentObservation(`Step ${i + 1}: ${steps[i]}`)
    }
    
    setStatus('completed')
    setTaskHistory(prev => [{
      id: Date.now(),
      task: taskText,
      status: 'completed',
      time: 'Just now'
    }, ...prev.slice(0, 9)])
  }

  // Stop current task
  const stopTask = useCallback(async () => {
    try {
      if (isConnected) {
        await agentAPI.stopTask()
      }
    } catch (err) {
      console.error('Failed to stop task:', err)
    } finally {
      setIsRunning(false)
      setStatus('idle')
      setCurrentStep(0)
      setCurrentTask(null)
    }
  }, [isConnected])

  // Get agent status
  const refreshStatus = useCallback(async () => {
    if (!isConnected) return

    try {
      const statusData = await agentAPI.getStatus()
      setIsRunning(statusData.is_running || false)
      setCurrentStep(statusData.current_step || 0)
    } catch (err) {
      console.error('Failed to get status:', err)
    }
  }, [isConnected])

  // Initialize connection check
  useEffect(() => {
    checkConnection()
    
    // Check connection periodically
    const interval = setInterval(checkConnection, 30000) // Every 30 seconds
    
    return () => clearInterval(interval)
  }, [checkConnection])

  // Load task history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('agent-task-history')
    if (savedHistory) {
      try {
        setTaskHistory(JSON.parse(savedHistory))
      } catch (err) {
        console.error('Failed to load task history:', err)
      }
    }
  }, [])

  // Save task history to localStorage
  useEffect(() => {
    if (taskHistory.length > 0) {
      localStorage.setItem('agent-task-history', JSON.stringify(taskHistory))
    }
  }, [taskHistory])

  return {
    // State
    status,
    isRunning,
    currentTask,
    taskHistory,
    currentStep,
    totalSteps,
    logs,
    currentObservation,
    error,
    isConnected,
    
    // Actions
    executeTask,
    stopTask,
    refreshStatus,
    checkConnection,
    
    // Computed values
    progress: totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0,
    canExecute: !isRunning && isConnected
  }
}

