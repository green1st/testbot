// API service untuk komunikasi dengan backend Autonomous Agent

const API_BASE_URL = 'http://localhost:8000'

class AgentAPI {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Health check endpoint
  async healthCheck() {
    return this.request('/')
  }

  // Execute agent task
  async executeTask(taskData) {
    return this.request('/agent/execute', {
      method: 'POST',
      body: JSON.stringify(taskData)
    })
  }

  // Get agent status
  async getStatus() {
    return this.request('/agent/status')
  }

  // Stop current task
  async stopTask() {
    return this.request('/agent/stop', {
      method: 'POST'
    })
  }

  // WebSocket connection for real-time updates
  createWebSocket(onMessage, onError, onClose) {
    const wsUrl = this.baseURL.replace('http', 'ws') + '/ws'
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('WebSocket message parsing error:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }
    
    ws.onclose = (event) => {
      console.log('WebSocket connection closed:', event)
      if (onClose) onClose(event)
    }
    
    return ws
  }
}

export const agentAPI = new AgentAPI()
export default agentAPI

