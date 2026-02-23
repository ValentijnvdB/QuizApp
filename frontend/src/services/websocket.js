// WebSocket service for real-time quiz sessions
class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectInterval = 3000
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.messageHandlers = new Map()
  }

  connect(sessionCode, participantName = null, isHost = false) {
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const token = localStorage.getItem('authToken')
    
    let wsUrl = `${WS_URL}/ws/session/${sessionCode}`
    
    if (isHost && token) {
      wsUrl += `?token=${token}`
    } else if (participantName) {
      wsUrl += `?name=${encodeURIComponent(participantName)}`
    }

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.attemptReconnect(sessionCode, participantName, isHost)
    }
  }

  attemptReconnect(sessionCode, participantName, isHost) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(sessionCode, participantName, isHost)
      }, this.reconnectInterval)
    } else {
      console.error('Max reconnect attempts reached')
      this.handleMessage({ type: 'connection_lost' })
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.messageHandlers.clear()
  }

  send(type, data = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  // Register a handler for a specific message type
  on(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType).push(handler)
  }

  // Remove a handler
  off(messageType, handler) {
    if (this.messageHandlers.has(messageType)) {
      const handlers = this.messageHandlers.get(messageType)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  // Handle incoming messages
  handleMessage(data) {
    const handlers = this.messageHandlers.get(data.type) || []
    handlers.forEach(handler => handler(data))
  }

  // Convenience methods for common actions
  submitAnswer(questionId, answer) {
    this.send('submit_answer', { question_id: questionId, answer })
  }

  nextQuestion() {
    this.send('next_question')
  }

  endSession() {
    this.send('end_session')
  }

  scoreAnswer(participantId, questionId, score) {
    this.send('score_answer', { participant_id: participantId, question_id: questionId, score })
  }
}

// Export singleton instance
export default new WebSocketService()
