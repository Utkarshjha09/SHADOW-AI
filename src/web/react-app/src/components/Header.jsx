import React from 'react'
import './Header.css'

const Header = ({ currentLanguage, onLanguageChange }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <h1>🤖 SHADOW</h1>
          <span className="subtitle">Personal Voice Assistant</span>
        </div>
        
        <div className="language-selector">
          <label htmlFor="language-select">Language:</label>
          <select 
            id="language-select"
            value={currentLanguage} 
            onChange={(e) => onLanguageChange(e.target.value)}
            className="language-dropdown"
          >
            <option value="auto">Auto Detect</option>
            <option value="en">English</option>
            <option value="hi">Hindi (हिंदी)</option>
          </select>
        </div>
      </div>
    </header>
  )
}

export default Header
