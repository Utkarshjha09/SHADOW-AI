import React, { useState } from 'react'
import './ChatInterface.css'

const ChatInterface = ({ messages, onTextInput, currentLanguage, showInput = true }) => {
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputText.trim() || isLoading) return

    setIsLoading(true)
    await onTextInput(inputText.trim())
    setInputText('')
    setIsLoading(false)
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getPlaceholder = () => {
    switch (currentLanguage) {
      case 'hi':
        return 'अपना संदेश यहाँ लिखें... या माइक बटन दबाएं'
      case 'en':
        return 'Type your message here... or use the microphone'
      default:
        return 'Type in Hindi or English... या हिंदी में लिखें'
    }
  }

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-content">
              <h2>👋 Welcome to SHADOW!</h2>
              <p>Your personal AI assistant ready to help in Hindi and English</p>
              <div className="example-queries">
                <h4>Try asking:</h4>
                <ul>
                  <li>"What's the weather today?"</li>
                  <li>"आज का मौसम कैसा है?"</li>
                  <li>"Tell me a joke"</li>
                  <li>"समय क्या है?"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-meta">
                    <span className="message-time">
                      {formatTime(message.timestamp)}
                    </span>
                    <span className="message-lang">
                      {message.language === 'hi' ? '🇮🇳' : '🇺🇸'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {showInput && (
        <form className="input-form" onSubmit={handleSubmit}>
          <div className="input-container">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={getPlaceholder()}
              className="message-input"
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? (
                <span className="loading-spinner"></span>
              ) : (
                <span className="send-icon">➤</span>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

export default ChatInterface
