import React, { useState, useRef } from 'react'
import './VoiceControl.css'

const VoiceControl = ({ isListening, onListeningChange, onVoiceInput, currentLanguage }) => {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef(null)
  const timerRef = useRef(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      const audioChunks = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        onVoiceInput(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      onListeningChange(true)
      
      // Start timer
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Unable to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      onListeningChange(false)
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      setRecordingTime(0)
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getButtonText = () => {
    if (currentLanguage === 'hi') {
      return isRecording ? 'रिकॉर्डिंग रोकें' : 'बोलना शुरू करें'
    }
    return isRecording ? 'Stop Recording' : 'Start Speaking'
  }

  const getHintText = () => {
    if (currentLanguage === 'hi') {
      return isRecording ? 
        'बोल रहे हैं... बटन दबाकर रोकें' : 
        'माइक बटन दबाकर बोलना शुरू करें'
    }
    return isRecording ? 
      'Listening... Click to stop' : 
      'Click microphone to start voice input'
  }

  return (
    <div className="voice-control">
      <div className="voice-interface">
        <div className="microphone-container">
          <button 
            className={`mic-button ${isRecording ? 'recording' : ''}`}
            onClick={toggleRecording}
            aria-label={getButtonText()}
          >
            <div className="mic-icon">
              {isRecording ? (
                <div className="stop-icon">⏹</div>
              ) : (
                <div className="microphone-icon">🎤</div>
              )}
            </div>
            
            {isRecording && (
              <div className="recording-indicator">
                <div className="pulse-ring"></div>
                <div className="pulse-ring pulse-ring-delay"></div>
              </div>
            )}
          </button>
          
          {isRecording && (
            <div className="recording-timer">
              {formatTime(recordingTime)}
            </div>
          )}
        </div>

        <div className="voice-status">
          <p className="voice-hint">{getHintText()}</p>
          
          <div className="wake-word-examples">
            <h4>Wake Words:</h4>
            <div className="wake-word-list">
              <span className="wake-word">"Hey SHADOW"</span>
              <span className="wake-word">"Hi SHADOW"</span>
              <span className="wake-word">"क्या SHADOW"</span>
              <span className="wake-word">"सुनो SHADOW"</span>
            </div>
          </div>
        </div>
      </div>

      {/* Voice Visualizer */}
      {isRecording && (
        <div className="voice-visualizer">
          <div className="sound-wave">
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default VoiceControl
