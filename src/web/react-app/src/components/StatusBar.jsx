import React from 'react'
import './StatusBar.css'

const StatusBar = ({ isConnected, isListening, currentLanguage }) => {
  return (
    <div className="status-bar">
      <div className="status-indicators">
        <div className={`status-item ${isConnected ? 'connected' : 'disconnected'}`}>
          <span className="indicator-dot"></span>
          <span className="status-text">
            {isConnected ? 'Connected to SHADOW' : 'Disconnected'}
          </span>
        </div>
        
        <div className={`status-item ${isListening ? 'listening' : 'idle'}`}>
          <span className="indicator-dot"></span>
          <span className="status-text">
            {isListening ? 'Listening...' : 'Ready'}
          </span>
        </div>
        
        <div className="status-item language">
          <span className="language-badge">
            {currentLanguage === 'en' ? '🇺🇸 EN' : 
             currentLanguage === 'hi' ? '🇮🇳 HI' : 
             '🌐 AUTO'}
          </span>
        </div>
      </div>
      
      <div className="wake-words-hint">
        Try: "Hey SHADOW" • "Hi SHADOW" • "क्या SHADOW" • "सुनो SHADOW"
      </div>
    </div>
  )
}

export default StatusBar
