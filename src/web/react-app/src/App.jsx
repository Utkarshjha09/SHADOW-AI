import React, { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import VoiceControl from './components/VoiceControl'
import Header from './components/Header'
import StatusBar from './components/StatusBar'
import ShadowPrompt from './components/ShadowPrompt'
import './App.css'

function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [currentLanguage, setCurrentLanguage] = useState('en')
  const [messages, setMessages] = useState([])

  useEffect(() => {
    // Check connection to backend
    checkBackendConnection()
  }, [])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('/api/health')
      setIsConnected(response.ok)
    } catch (error) {
      setIsConnected(false)
      console.error('Backend connection failed:', error)
    }
  }

  const handleVoiceInput = async (audioData) => {
    try {
      const formData = new FormData()
      // Accept File or Blob; add filename if available
      if (audioData instanceof File) {
        formData.append('audio', audioData, audioData.name || 'input.webm')
      } else {
        formData.append('audio', new File([audioData], 'input.webm', { type: audioData?.type || 'audio/webm' }))
      }
      formData.append('language', currentLanguage)

      const response = await fetch('/api/voice', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (result.success) {
        const userMessage = {
          id: Date.now(),
          type: 'user',
          content: result.transcript,
          language: result.language || currentLanguage,
          timestamp: new Date()
        }
        
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: result.response,
          language: result.language || currentLanguage,
          timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage, assistantMessage])
        
        // Auto-detect and switch language if needed
        if (result.language && result.language !== currentLanguage) {
          setCurrentLanguage(result.language)
        }
      } else {
        // Show error message with details
        let extra = ''
        try {
          const attempts = result?.details?.attempt_errors || []
          if (attempts.length) {
            extra = `\nDetails: ${attempts.join(' | ')}`
          }
          // Windows-specific FFmpeg hint if conversion errors appear
          if (attempts.join(' ').toLowerCase().includes('ffmpeg')) {
            extra += `\nFix (Windows): Install FFmpeg and restart the terminal running Flask.`
          }
        } catch {}

        const errorMessage = {
          id: Date.now(),
          type: 'system',
          content: (result.error || 'Voice recognition failed. Please try again.') + extra,
          language: currentLanguage,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Voice input error:', error)
      const errorMessage = {
        id: Date.now(),
        type: 'system',
        content: 'Network error. Please check your connection.',
        language: currentLanguage,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const handleTextInput = async (text) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: text,
          language: currentLanguage
        })
      })

      const result = await response.json()
      
      if (result.success) {
        const userMessage = {
          id: Date.now(),
          type: 'user',
          content: text,
          language: currentLanguage,
          timestamp: new Date()
        }
        
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: result.response,
          language: result.language || currentLanguage,
          timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage, assistantMessage])
      }
    } catch (error) {
      console.error('Text input error:', error)
    }
  }

  return (
    <div className="app">
      <Header 
        currentLanguage={currentLanguage}
        onLanguageChange={setCurrentLanguage}
      />
      
      <StatusBar 
        isConnected={isConnected}
        isListening={isListening}
        currentLanguage={currentLanguage}
      />
      
      <main className="main-content">
        <ChatInterface 
          messages={messages}
          onTextInput={handleTextInput}
          currentLanguage={currentLanguage}
          showInput={false}
        />
        
        <ShadowPrompt
          onTextInput={handleTextInput}
          onVoiceInput={handleVoiceInput}
          isListening={isListening}
          onListeningChange={setIsListening}
          currentLanguage={currentLanguage}
          onLanguageChange={setCurrentLanguage}
        />
      </main>
    </div>
  )
}

export default App
