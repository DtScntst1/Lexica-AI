"use client";

import { useState, useRef } from 'react';

export default function Home() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Welcome to Lexica-AI. Upload a document to begin the deep analysis.', sources: [] }
  ]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [documents, setDocuments] = useState([]);
  
  const fileInputRef = useRef(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      });
      
      const data = await res.json();
      if (res.ok) {
        setDocuments(prev => [...prev, file.name]);
        setMessages(prev => [...prev, { 
          role: 'bot', 
          content: `Successfully ingested "${file.name}" (${data.chunks_processed} chunks). You may now ask questions about it.`,
          sources: [] 
        }]);
      } else {
        alert(data.detail || "Upload failed");
      }
    } catch (err) {
      alert("Backend is not running or unreachable.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg, sources: [] }]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('http://localhost:8000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg })
      });
      
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { 
          role: 'bot', 
          content: data.answer, 
          sources: data.sources || [] 
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: `Error: ${data.detail}`, sources: [] }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "Network error. Is the backend running?", sources: [] }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-container">
      
      {/* Sidebar: Library & Upload */}
      <div className="sidebar glass-panel">
        <div className="brand">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>
          Lexica-AI
        </div>
        
        <input 
          type="file" 
          accept=".pdf" 
          ref={fileInputRef} 
          onChange={handleUpload} 
          style={{ display: 'none' }} 
        />
        
        <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
          <div className="upload-icon">📄</div>
          <div className="upload-text">
            {isUploading ? "Indexing Document..." : "Click to Upload PDF"}
          </div>
        </div>

        <h4 style={{ color: 'var(--text-muted)', marginBottom: '10px', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Document Library
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {documents.length === 0 ? (
            <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.2)', fontStyle: 'italic' }}>No documents uploaded yet.</div>
          ) : (
            documents.map((doc, idx) => (
              <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '10px 14px', borderRadius: '8px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '10px', border: '1px solid var(--glass-border)' }}>
                <span style={{ color: 'var(--success)' }}>●</span> {doc}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="chat-area glass-panel">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role === 'user' ? 'msg-user' : 'msg-bot'}`}>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              
              {/* Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="citations">
                  {msg.sources.map((src, i) => (
                    <div key={i} className="citation-badge" title={src.content_preview}>
                      📄 {src.file} (Page {src.page})
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          )}
        </div>

        <div className="input-container">
          <input 
            type="text" 
            placeholder="Ask a question about your documents..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isTyping || isUploading}
          />
          <button onClick={handleSend} disabled={isTyping || isUploading || !input.trim()}>
            Send
          </button>
        </div>
      </div>

    </div>
  );
}
