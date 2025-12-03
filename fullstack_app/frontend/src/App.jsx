import React, { useEffect, useState, useRef } from 'react';
import {
  sendChatCompletion,
  uploadFiles,
  getSupportedTypes,
  listAgents,
  runAgent,
  getJob,
  streamJob,
} from './services/api';

import './styles/app.css';

// Simple toast component
function Toast({ message, type }) {
  return (
    <div className={`toast toast-${type}`}>{message}</div>
  );
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [agents, setAgents] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [supportedTypes, setSupportedTypes] = useState([]);
  const [statusMessages, setStatusMessages] = useState([]);
  const [jobId, setJobId] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Fetch supported file types and agents on mount
    async function init() {
      try {
        const types = await getSupportedTypes();
        setSupportedTypes(types);
        const agentsList = await listAgents();
        setAgents(agentsList);
      } catch (err) {
        console.error(err);
      }
    }
    init();
  }, []);

  // Scroll chat to bottom when messages change
  const chatEndRef = useRef(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addStatus = (message, type = 'info') => {
    const id = Date.now();
    setStatusMessages((msgs) => [...msgs, { id, message, type }]);
    // Remove after 5 seconds
    setTimeout(() => {
      setStatusMessages((msgs) => msgs.filter((m) => m.id !== id));
    }, 5000);
  };

  const handleSend = async () => {
    if (!input.trim() && uploadedFiles.length === 0) return;
    const userMessage = { role: 'user', content: input.trim() };
    // Add user message to chat
    setMessages((msgs) => [...msgs, userMessage]);
    // Prepare files metadata for agent
    let filesMeta = [];
    if (uploadedFiles.length > 0) {
      const formData = new FormData();
      uploadedFiles.forEach((file) => {
        formData.append('files', file);
      });
      try {
        addStatus('Uploading files...', 'info');
        const uploadRes = await uploadFiles(formData);
        filesMeta = uploadRes.files;
        addStatus('Files uploaded successfully.', 'success');
      } catch (err) {
        addStatus('File upload failed.', 'error');
        console.error(err);
      }
    }
    // Run agent if selected
    if (selectedAgent) {
      addStatus(`Agent ${selectedAgent} running...`, 'info');
      try {
        const id = await runAgent(selectedAgent, input.trim(), filesMeta);
        setJobId(id);
        // Monitor job via SSE
        const evtSource = streamJob(id, (data) => {
          try {
            const parsed = JSON.parse(data);
            if (parsed.status && parsed.result) {
              addStatus(`Job ${parsed.status}`, parsed.status === 'completed' ? 'success' : 'error');
              // Render result
              let content;
              if (parsed.result.file_url) {
                content = (
                  <a href={parsed.result.file_url} target="_blank" rel="noopener noreferrer">Download Document</a>
                );
              } else if (parsed.result.result) {
                content = parsed.result.result;
              } else {
                content = JSON.stringify(parsed.result);
              }
              setMessages((msgs) => [...msgs, { role: 'assistant', content }]);
              setJobId(null);
              evtSource.close();
            }
          } catch (e) {
            // Intermediate log line
            addStatus(data, 'info');
          }
        });
      } catch (err) {
        addStatus('Agent execution failed.', 'error');
        console.error(err);
      }
    } else {
      // Normal chat completion
      try {
        addStatus('Generating response...', 'info');
        const messagesForApi = [...messages, userMessage].map((m) => ({ role: m.role, content: m.content }));
        const res = await sendChatCompletion(messagesForApi, selectedModel, false);
        addStatus('Response received.', 'success');
        setMessages((msgs) => [...msgs, { role: 'assistant', content: res.result }]);
      } catch (err) {
        addStatus('Error generating response.', 'error');
        console.error(err);
      }
    }
    // Reset input and files
    setInput('');
    setUploadedFiles([]);
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setUploadedFiles(files);
  };

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const handleAgentChange = (e) => {
    setSelectedAgent(e.target.value);
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2>AI Agents</h2>
        {/* Navigation and session management can go here */}
      </div>
      <div className="chat-area">
        <div className="header">
          <div className="controls">
            <div className="select-group">
              <label htmlFor="model-select">Model:</label>
              <select id="model-select" value={selectedModel} onChange={handleModelChange} disabled={!!selectedAgent}>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
              </select>
            </div>
            <div className="select-group">
              <label htmlFor="agent-select">Agent:</label>
              <select id="agent-select" value={selectedAgent} onChange={handleAgentChange}>
                <option value="">None</option>
                {agents.map((agent) => (
                  <option key={agent.name} value={agent.name}>{agent.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
        <div className="messages" id="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}> {msg.content} </div>
          ))}
          {uploadedFiles.length > 0 && (
            <div className="uploaded-list">
              {uploadedFiles.map((file, idx) => (
                <span key={idx} className="file-bubble">{file.name}</span>
              ))}
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="input-bar">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button className="plus-button" onClick={() => fileInputRef.current?.click()}>+
          </button>
          <button className="send-button" onClick={handleSend}>Send</button>
          <input
            type="file"
            ref={fileInputRef}
            multiple
            style={{ display: 'none' }}
            accept={supportedTypes.map((t) => SUPPORTED_EXTENSION(t)).join(',')}
            onChange={handleFileSelect}
          />
        </div>
        {/* Status toasts */}
        <div className="toast-container">
          {statusMessages.map(({ id, message, type }) => (
            <Toast key={id} message={message} type={type} />
          ))}
        </div>
      </div>
    </div>
  );
}

// Helper to convert MIME type to file extension for the accept attribute
function SUPPORTED_EXTENSION(type) {
  switch (type) {
    case 'application/pdf': return '.pdf';
    case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': return '.docx';
    case 'text/plain': return '.txt';
    case 'text/csv': return '.csv';
    case 'image/png': return '.png';
    case 'image/jpeg': return '.jpg';
    default: return '';
  }
}

export default App;