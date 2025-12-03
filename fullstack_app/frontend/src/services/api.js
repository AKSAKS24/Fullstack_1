import axios from 'axios';

// Base API instance; proxy is configured in Vite config
const api = axios.create({
  baseURL: '/',
  timeout: 60000,
});

export async function sendChatCompletion(messages, model = 'gpt-3.5-turbo', stream = false) {
  const response = await api.post('/chat/completions', {
    messages,
    model,
    stream,
  });
  return response.data;
}

export async function uploadFiles(formData) {
  const response = await api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getSupportedTypes() {
  const response = await api.get('/files/types');
  return response.data.supported_types;
}

export async function listAgents() {
  const response = await api.get('/agent/list');
  return response.data.agents;
}

export async function runAgent(agentName, inputText, files) {
  const response = await api.post('/agent/run', {
    agent: agentName,
    input_text: inputText,
    files,
  });
  return response.data.job_id;
}

export async function getJob(jobId) {
  const response = await api.get(`/job/${jobId}`);
  return response.data;
}

export function streamJob(jobId, onMessage) {
  const eventSource = new EventSource(`/job/${jobId}?stream=true`);
  eventSource.onmessage = (event) => {
    onMessage(event.data);
  };
  return eventSource;
}