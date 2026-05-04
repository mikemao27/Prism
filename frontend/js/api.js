const API = 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

async function apiRequest(method, path, body = null) {
  const options = {
    method,
    headers: authHeaders()
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API}${path}`, options);

  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
    return;
  }

  return res;
}

const PrismAPI = {
  // Auth
  getMe: () => apiRequest('GET', '/auth/me'),

  // Conversations
  getConversations: () => apiRequest('GET', '/conversations'),
  createConversation: (title) => apiRequest('POST', '/conversations', { title }),

  // Messages
  getMessages: (convoId) => apiRequest('GET', `/conversations/${convoId}/messages`),
  sendMessage: (convoId, content) => apiRequest('POST', `/conversations/${convoId}/messages`, { content }),

  // API Keys
  getKeys: () => apiRequest('GET', '/keys'),
  addKey: (provider, api_key, credit_balance) =>
    apiRequest('POST', '/keys', { provider, api_key, credit_balance }),

  // Conversation management
  renameConversation: (convoId, title) =>
    apiRequest('PATCH', `/conversations/${convoId}/rename`, { title }),
  archiveConversation: (convoId, archived) =>
    apiRequest('PATCH', `/conversations/${convoId}/archive`, { archived }),
  deleteConversation: (convoId) =>
    apiRequest('DELETE', `/conversations/${convoId}`),

  // Message management
  deleteMessage: (convoId, messageId) =>
    apiRequest('DELETE', `/conversations/${convoId}/messages/${messageId}`),
  editMessage: (convoId, messageId, content) =>
    apiRequest('PATCH', `/conversations/${convoId}/messages/${messageId}/edit`, { content }),

  summarize: (convoId) => apiRequest('POST', `/conversations/${convoId}/summarize`),
  getSummaries: (convoId) => apiRequest('GET', `/conversations/${convoId}/summaries`),

  changePassword: (current_password, new_password) =>
    apiRequest('PATCH', '/auth/password', { current_password, new_password }),
  deleteKey: (keyId) => apiRequest('DELETE', `/keys/${keyId}`),
  updateBalance: (keyId, credit_balance) =>
    apiRequest('PATCH', `/keys/${keyId}/balance`, { credit_balance }),
};