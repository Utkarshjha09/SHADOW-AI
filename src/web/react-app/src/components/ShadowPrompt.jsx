import React, { useState, useEffect, useRef } from 'react';
import { Plus, ChevronDown, Mic, Send, Image as ImageIcon, FileText, Brain, Settings } from 'lucide-react';
import './ShadowPrompt.css';

const ShadowPrompt = ({ onTextInput, onVoiceInput, isListening, onListeningChange, currentLanguage, onLanguageChange }) => {
  const [prompt, setPrompt] = useState('');
  const [isAddPopupOpen, setAddPopupOpen] = useState(false);
  const [isModelOpen, setModelOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('Ollama (phi3:mini)');
  
  // Available models for SHADOW
  const models = [
    'Ollama (phi3:mini)',
    'Ollama (llama2)', 
    'Ollama (mistral)',
    'Ollama (codellama)'
  ];

  const addPopupRef = useRef(null);
  const modelRef = useRef(null);
  const textareaRef = useRef(null);

  // Mic / recording state
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const recognitionRef = useRef(null);
  const lastWakeCheckAtRef = useRef(0);
  const lastCheckedLenRef = useRef(0);
  const [hasMicPermission, setHasMicPermission] = useState(false);
  const [wakeWords, setWakeWords] = useState([]);
  const [statusText, setStatusText] = useState('');

  // Handle clicks outside popups
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (addPopupRef.current && !addPopupRef.current.contains(event.target)) {
        setAddPopupOpen(false);
      }
      if (modelRef.current && !modelRef.current.contains(event.target)) {
        setModelOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [prompt]);

  // Fetch config (wake words)
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch('/api/config');
        const json = await res.json();
        if (json?.success) {
          setWakeWords(json.config?.wake_words || []);
        }
      } catch (e) {
        // non-fatal
      }
    };
    fetchConfig();
  }, []);

  const requestMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setHasMicPermission(true);
      return stream;
    } catch (err) {
      setHasMicPermission(false);
      setStatusText(currentLanguage === 'hi' ? 'माइक्रोफोन अनुमति अस्वीकृत' : 'Microphone permission denied');
      throw err;
    }
  };

  const stopStreamTracks = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  };

  const sendBlobToServer = async (blob) => {
    if (onVoiceInput) {
      // Parent will handle POST /api/voice
      await onVoiceInput(new File([blob], 'input.webm', { type: blob.type || 'audio/webm' }));
    }
  };

  const startRecording = async () => {
    try {
      const stream = streamRef.current || await requestMic();
      const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
      const mr = new MediaRecorder(stream, { mimeType: mime });
      audioChunksRef.current = [];
      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      mr.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: mime });
        audioChunksRef.current = [];
        setStatusText(currentLanguage === 'hi' ? 'प्रोसेसिंग...' : 'Processing...');
        await sendBlobToServer(blob);
      };
      mediaRecorderRef.current = mr;
      mr.start();
      onListeningChange?.(true);
      setStatusText(currentLanguage === 'hi' ? 'बोलिए... रुकने पर 3 सेकंड बाद मैं जवाब दूंगा' : 'Speak now... I\'ll respond 3 seconds after you stop');
      
      // Auto-stop recording after 3 seconds of silence (simulated with timer)
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          stopRecording();
        }
      }, 8000); // 8 seconds max recording time
    } catch (e) {
      onListeningChange?.(false);
      setStatusText(currentLanguage === 'hi' ? 'माइक्रोफोन त्रुटि' : 'Microphone error');
    }
  };

  const stopRecording = () => {
    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    } finally {
      onListeningChange?.(false);
      stopStreamTracks();
    }
  };

  const backendIsWakeWord = async (text) => {
    try {
      const res = await fetch('/api/wake-word', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const json = await res.json();
      return !!json?.is_wake_word;
    } catch {
      return false;
    }
  };

  const startWakeDetection = async () => {
    // Web Speech API (best-effort). Requires user gesture to start mic once.
    try {
      await requestMic();
    } catch {
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      // Fallback: directly start recording
      await startRecording();
      return;
    }

    const rec = new SpeechRecognition();
    rec.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    recognitionRef.current = rec;
    setStatusText(currentLanguage === 'hi' ? 'जागने के शब्द बोलें…' : 'Say a wake word…');
    onListeningChange?.(true);

    let buffer = '';
    rec.onresult = async (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript + ' ';
      }
      buffer = (buffer + ' ' + transcript).trim();
      // Check wake word via backend fuzzy
      const now = Date.now();
      const shouldCheck = buffer.length > 3 &&
        (now - lastWakeCheckAtRef.current > 450) &&
        (buffer.length - lastCheckedLenRef.current >= 4);
      if (shouldCheck) {
        lastWakeCheckAtRef.current = now;
        lastCheckedLenRef.current = buffer.length;
        const hit = await backendIsWakeWord(buffer);
        if (hit) {
          rec.stop();
          setStatusText(currentLanguage === 'hi' ? 'जाग गया, बोलें…' : 'Awake, start speaking…');
          // Begin actual high-quality recording for Whisper
          setTimeout(() => { startRecording(); }, 100);
        }
      }
    };
    rec.onerror = () => {
      onListeningChange?.(false);
      setStatusText('');
    };
    rec.onend = () => {
      // If we ended but never started recording, reset state
      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        onListeningChange?.(false);
        setStatusText('');
      }
    };
    rec.start();
  };

  const handleModelSelect = (model) => {
    setSelectedModel(model);
    setModelOpen(false);
  };

  const handleSendMessage = () => {
    if (!prompt.trim()) return;
    
    onTextInput(prompt.trim());
    setPrompt('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceClick = async () => {
    if (!isListening) {
      // Start wake detection first; recording follows on wake hit
      await startWakeDetection();
    } else {
      // Stop any active recognition / recording
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
        recognitionRef.current = null;
      }
      stopRecording();
    }
  };

  const getPlaceholder = () => {
    switch (currentLanguage) {
      case 'hi':
        return 'SHADOW से कुछ पूछें... या अपनी बात कहें';
      case 'en':
        return 'Ask SHADOW anything... or share your thoughts';
      default:
        return 'Ask SHADOW in Hindi or English... या हिंदी में पूछें';
    }
  };

  const getVoiceButtonText = () => {
    if (isListening) {
      return currentLanguage === 'hi' ? 'सुन रहे हैं...' : 'Listening...';
    }
    return currentLanguage === 'hi' ? 'बोलना शुरू करें' : 'Start Speaking';
  };

  const addMenuItems = [
    { 
      icon: <ImageIcon size={20} className="text-purple-500" />, 
      text: currentLanguage === 'hi' ? 'फोटो या वीडियो जोड़ें' : 'Add photos or videos' 
    },
    { 
      icon: <FileText size={20} className="text-blue-500" />, 
      text: currentLanguage === 'hi' ? 'फाइलें जोड़ें' : 'Add files (docs, txt...)' 
    },
    { 
      icon: <Settings size={20} className="text-gray-500" />, 
      text: currentLanguage === 'hi' ? 'सेटिंग्स' : 'Settings' 
    }
  ];

  return (
    <div className="shadow-prompt-container">
      <div className="shadow-prompt-card">
        {/* Header with SHADOW branding */}
        <div className="shadow-prompt-header">
          <div className="shadow-logo">
            <span className="shadow-icon">🤖</span>
            <span className="shadow-text">SHADOW</span>
          </div>
          <div className="language-indicator">
            {currentLanguage === 'hi' ? '🇮🇳 हिंदी' : 
             currentLanguage === 'en' ? '🇺🇸 English' : 
             '🌐 Auto'}
          </div>
        </div>

        {/* Main input area */}
        <div className="shadow-input-container">
          <textarea
            ref={textareaRef}
            className="shadow-textarea"
            rows={1}
            placeholder={getPlaceholder()}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          
          {/* Wake word suggestions */}
          {!prompt && (
            <div className="wake-word-suggestions">
              <span className="suggestion-label">
                {currentLanguage === 'hi' ? 'कहकर देखें:' : 'Try saying:'}
              </span>
              <div className="suggestion-pills">
                <span className="pill">"Hey SHADOW"</span>
                <span className="pill">"क्या SHADOW"</span>
                <span className="pill">"सुनो SHADOW"</span>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="shadow-controls">
          {/* Left side controls */}
          <div className="left-controls">
            {/* Add Button */}
            <div className="control-group" ref={addPopupRef}>
              <button 
                onClick={() => setAddPopupOpen(!isAddPopupOpen)}
                className="control-btn add-btn"
                title={currentLanguage === 'hi' ? 'अधिक विकल्प' : 'More options'}
              >
                <Plus size={20} />
              </button>
              
              {isAddPopupOpen && (
                <div className="popup-menu add-popup">
                  <ul>
                    {addMenuItems.map((item, index) => (
                      <li key={index} className="menu-item">
                        {item.icon}
                        <span>{item.text}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Model Selection */}
            <div className="control-group" ref={modelRef}>
              <button 
                onClick={() => setModelOpen(!isModelOpen)}
                className="control-btn model-btn"
                title={currentLanguage === 'hi' ? 'AI मॉडल चुनें' : 'Select AI Model'}
              >
                <Brain size={18} />
                <span className="model-name">{selectedModel}</span>
                <ChevronDown size={16} />
              </button>
              
              {isModelOpen && (
                <div className="popup-menu model-popup">
                  <ul>
                    {models.map((model) => (
                      <li 
                        key={model} 
                        onClick={() => handleModelSelect(model)}
                        className={`menu-item ${selectedModel === model ? 'active' : ''}`}
                      >
                        <Brain size={16} />
                        <span>{model}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Right side controls */}
          <div className="right-controls">
            {/* Voice Button */}
            <button 
              onClick={handleVoiceClick}
              className={`control-btn voice-btn ${isListening ? 'listening' : ''}`}
              title={getVoiceButtonText()}
            >
              <Mic size={20} />
              {isListening && <div className="listening-indicator"></div>}
            </button>

            {/* Send Button */}
            <button 
              onClick={handleSendMessage}
              disabled={!prompt.trim()}
              className={`control-btn send-btn ${prompt.trim() ? 'active' : 'disabled'}`}
              title={currentLanguage === 'hi' ? 'भेजें' : 'Send'}
            >
              <Send size={20} />
            </button>
          </div>
        </div>

        {/* Status bar */}
        {isListening && (
          <div className="status-bar">
            <div className="listening-animation">
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
            </div>
            <span className="status-text">{statusText || (currentLanguage === 'hi' ? 'सुन रहे हैं... बोलिए' : 'Listening... Please speak')}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ShadowPrompt;