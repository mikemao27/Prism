// ── State ──
let currentConvoId = null;
let allConversations = [];
let showArchived = false;

// ── Init ──
async function init() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = 'index.html'; return; }

  const res = await PrismAPI.getMe();
  if (!res) return;
  const user = await res.json();
  const email = user.email;
  document.getElementById('user-email').textContent = email;
  document.getElementById('user-avatar').textContent = email[0].toUpperCase();

  await loadConversations();
  document.addEventListener('click', closeAllMenus);
}

// ── Conversations ──
async function loadConversations() {
  const res = await PrismAPI.getConversations();
  if (!res) return;
  allConversations = await res.json();
  renderSidebar();
}

function renderSidebar() {
  const query = document.getElementById('search-input').value.toLowerCase();
  const active = allConversations.filter(c => !c.archived && c.title.toLowerCase().includes(query));
  const archived = allConversations.filter(c => c.archived && c.title.toLowerCase().includes(query));

  const list = document.getElementById('conversations-list');
  list.innerHTML = '';

  // Active conversations
  if (active.length === 0 && !query) {
    list.innerHTML += `<div style="padding:16px;font-size:12px;color:var(--text-muted);text-align:center;">No conversations yet</div>`;
  } else {
    active.forEach(c => list.appendChild(buildConvoItem(c, false)));
  }

  // Archived section
  if (archived.length > 0) {
    const label = document.createElement('div');
    label.className = 'sidebar-section-label clickable';
    label.innerHTML = `<span>Archived</span><span>${showArchived ? '▲' : '▼'}</span>`;
    label.addEventListener('click', () => { showArchived = !showArchived; renderSidebar(); });
    list.appendChild(label);

    if (showArchived) {
      const archivedDiv = document.createElement('div');
      archivedDiv.className = 'archived-list';
      archived.forEach(c => archivedDiv.appendChild(buildConvoItem(c, true)));
      list.appendChild(archivedDiv);
    }
  }
}

function buildConvoItem(convo, isArchived) {
  const item = document.createElement('div');
  item.className = 'convo-item' + (convo.id === currentConvoId ? ' active' : '');
  item.dataset.id = convo.id;
  item.innerHTML = `
    <div class="convo-title">${escapeHtml(convo.title)}</div>
    <div class="convo-meta">${convo.model_locked || 'not started'}</div>
    <div class="convo-actions">
      <button class="btn-three-dot" data-id="${convo.id}" title="Options">···</button>
    </div>
  `;

  item.addEventListener('click', (e) => {
    if (e.target.closest('.btn-three-dot')) return;
    selectConversation(convo.id, convo.title, convo.model_locked);
  });

  item.querySelector('.btn-three-dot').addEventListener('click', (e) => {
    e.stopPropagation();
    showConvoMenu(e, convo, isArchived);
  });

  return item;
}

function showConvoMenu(e, convo, isArchived) {
  closeAllMenus();
  const menu = document.createElement('div');
  menu.className = 'context-menu';
  menu.id = 'active-context-menu';

  menu.innerHTML = `
    <button class="context-menu-item" id="menu-rename">
      <span class="item-icon">✎</span> Rename
    </button>
    <button class="context-menu-item" id="menu-archive">
      <span class="item-icon">${isArchived ? '↩' : '▣'}</span>
      ${isArchived ? 'Unarchive' : 'Archive'}
    </button>
    <div class="context-menu-divider"></div>
    <button class="context-menu-item danger" id="menu-delete">
      <span class="item-icon">✕</span> Delete
    </button>
  `;

  document.body.appendChild(menu);
  positionMenu(menu, e);

  menu.querySelector('#menu-rename').addEventListener('click', () => {
    closeAllMenus();
    startRename(convo);
  });

  menu.querySelector('#menu-archive').addEventListener('click', () => {
    closeAllMenus();
    toggleArchive(convo, isArchived);
  });

  menu.querySelector('#menu-delete').addEventListener('click', () => {
    closeAllMenus();
    deleteConversation(convo.id);
  });
}

function positionMenu(menu, e) {
  const x = e.clientX;
  const y = e.clientY;
  menu.style.left = x + 'px';
  menu.style.top = y + 'px';

  // Flip if off-screen
  requestAnimationFrame(() => {
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (x - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (y - rect.height) + 'px';
  });
}

function closeAllMenus() {
  const existing = document.getElementById('active-context-menu');
  if (existing) existing.remove();
}

async function startRename(convo) {
  const newTitle = prompt('Rename conversation:', convo.title);
  if (!newTitle || newTitle.trim() === convo.title) return;
  const res = await PrismAPI.renameConversation(convo.id, newTitle.trim());
  if (!res) return;
  
  // Update local state immediately
  const localConvo = allConversations.find(c => c.id === convo.id);
  if (localConvo) localConvo.title = newTitle.trim();

  // Update header if this is the active conversation
  if (currentConvoId === convo.id) {
    document.getElementById('chat-title').textContent = newTitle.trim();
  }

  await loadConversations();
}

async function toggleArchive(convo, isArchived) {
  await PrismAPI.archiveConversation(convo.id, !isArchived);
  if (currentConvoId === convo.id && !isArchived) {
    currentConvoId = null;
    document.getElementById('chat-title').textContent = 'Select a conversation';
    document.getElementById('model-badge').style.display = 'none';
    document.getElementById('messages-area').innerHTML = `
      <div class="empty-state" id="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">Welcome to Prism</div>
        <div class="empty-subtitle">Create a new conversation and Prism will automatically route your query to the best available model.</div>
      </div>`;
  }
  await loadConversations();
}

async function deleteConversation(convoId) {
  if (!confirm('Delete this conversation? This cannot be undone.')) return;
  await PrismAPI.deleteConversation(convoId);
  if (currentConvoId === convoId) {
    currentConvoId = null;
    document.getElementById('chat-title').textContent = 'Select a conversation';
    document.getElementById('model-badge').style.display = 'none';
    document.getElementById('send-btn').disabled = true;
    document.getElementById('messages-area').innerHTML = `
      <div class="empty-state" id="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">Welcome to Prism</div>
        <div class="empty-subtitle">Create a new conversation and Prism will automatically route your query to the best available model.</div>
      </div>`;
  }
  await loadConversations();
}

async function selectConversation(id, title, modelLocked) {
  currentConvoId = id;
  document.getElementById('chat-title').textContent = title;
  const badge = document.getElementById('model-badge');
  const badgeText = document.getElementById('model-badge-text');
  if (modelLocked) {
    badge.style.display = 'flex';
    badgeText.textContent = modelLocked;
  } else {
    badge.style.display = 'none';
  }
  document.getElementById('send-btn').disabled = false;
  renderSidebar();
  await loadMessages(id);
}

// ── Messages ──
async function loadMessages(convoId) {
  const messagesArea = document.getElementById('messages-area');
  messagesArea.innerHTML = '';
  const res = await PrismAPI.getMessages(convoId);
  if (!res) return;
  const messages = await res.json();

  if (messages.length === 0) {
    messagesArea.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">Conversation started</div>
        <div class="empty-subtitle">Send your first message and Prism will route it to the best model.</div>
      </div>`;
    return;
  }

  messages.forEach(msg => appendMessage(msg.role, msg.content, msg.model_used, msg.id));
  scrollToBottom();
}

function appendMessage(role, content, modelUsed = null, messageId = null) {
  const messagesArea = document.getElementById('messages-area');
  const emptyState = document.getElementById('empty-state');
  if (emptyState) emptyState.remove();

  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  if (messageId) msg.dataset.id = messageId;

  const actionsHtml = messageId ? `
    <div class="message-actions">
      <button class="btn-msg-action" title="Copy" onclick="copyMessage(this)">⧉</button>
      ${role === 'user' ? `<button class="btn-msg-action" title="Edit" onclick="startEditMessage(this)">✎</button>` : ''}
      <button class="btn-msg-action" title="Delete" onclick="deleteMessage(this)">✕</button>
    </div>` : '';

  if (role === 'user') {
    msg.innerHTML = `
      ${actionsHtml}
      <div class="message-content-wrap">
        <div class="message-bubble">${escapeHtml(content)}</div>
        ${modelUsed ? `<div class="message-meta">${modelUsed}</div>` : ''}
      </div>
      <div class="message-avatar">↑</div>
    `;
  } else {
    msg.innerHTML = `
      <div class="message-avatar">◈</div>
      <div class="message-content-wrap">
        <div class="message-bubble">${escapeHtml(content)}</div>
        ${modelUsed ? `<div class="message-meta">${modelUsed}</div>` : ''}
      </div>
      ${actionsHtml}
    `;
  }

  messagesArea.appendChild(msg);
  scrollToBottom();
}

function copyMessage(btn) {
  const bubble = btn.closest('.message').querySelector('.message-bubble');
  navigator.clipboard.writeText(bubble.textContent);
}

function startEditMessage(btn) {
  const msgEl = btn.closest('.message');
  console.log("Editing Message ID:", msgEl.dataset.id, "Role:", msgEl.classList);
  const bubble = msgEl.querySelector('.message-bubble');
  const originalText = bubble.textContent;
  const messageId = msgEl.dataset.id;

  const wrap = msgEl.querySelector('.message-content-wrap');
  const textarea = document.createElement('textarea');
  textarea.className = 'edit-textarea';
  textarea.rows = 3;
  textarea.value = originalText;

  const saveBtn = document.createElement('button');
  saveBtn.className = 'btn-edit-save';
  saveBtn.textContent = 'Save & Resend';

  const cancelBtn = document.createElement('button');
  cancelBtn.className = 'btn-edit-cancel';
  cancelBtn.textContent = 'Cancel';

  const editActions = document.createElement('div');
  editActions.className = 'edit-actions';
  editActions.appendChild(cancelBtn);
  editActions.appendChild(saveBtn);

  const editWrapper = document.createElement('div');
  editWrapper.className = 'edit-wrapper';
  editWrapper.appendChild(textarea);
  editWrapper.appendChild(editActions);

  wrap.innerHTML = '';
  wrap.appendChild(editWrapper);

  textarea.focus();
  textarea.setSelectionRange(textarea.value.length, textarea.value.length);

  cancelBtn.addEventListener('click', () => {
    wrap.innerHTML = `<div class="message-bubble">${escapeHtml(originalText)}</div>`;
  });

  saveBtn.addEventListener('click', async () => {
    const newContent = textarea.value.trim();
    if (!newContent) return;
    saveBtn.textContent = 'Sending...';
    saveBtn.disabled = true;
    const res = await PrismAPI.editMessage(currentConvoId, messageId, newContent);
    if (!res) return;
    await loadMessages(currentConvoId);
  });
}

function cancelEdit(btn, originalText) {
  const msgEl = btn.closest('.message');
  const wrap = msgEl.querySelector('.message-content-wrap');
  wrap.innerHTML = `<div class="message-bubble">${escapeHtml(originalText)}</div>`;
}

async function saveEdit(btn, messageId) {
  const msgEl = btn.closest('.message');
  const textarea = msgEl.querySelector('.edit-textarea');
  const newContent = textarea.value.trim();
  if (!newContent) return;

  btn.textContent = 'Sending...';
  btn.disabled = true;

  const res = await PrismAPI.editMessage(currentConvoId, messageId, newContent);
  if (!res) return;

  await loadMessages(currentConvoId);
}

async function deleteMessage(btn) {
  if (!confirm('Delete this message?')) return;
  const msgEl = btn.closest('.message');
  const messageId = msgEl.dataset.id;
  await PrismAPI.deleteMessage(currentConvoId, messageId);
  msgEl.remove();
}

function appendTypingIndicator() {
  const messagesArea = document.getElementById('messages-area');
  const indicator = document.createElement('div');
  indicator.className = 'message assistant';
  indicator.id = 'typing-indicator';
  indicator.innerHTML = `
    <div class="message-avatar">◈</div>
    <div class="message-bubble">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  messagesArea.appendChild(indicator);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ── Send Message ──
async function sendMessage() {
  const input = document.getElementById('message-input');
  const content = input.value.trim();
  if (!content || !currentConvoId) return;

  input.value = '';
  input.style.height = 'auto';
  document.getElementById('send-btn').disabled = true;

  // Optimistic user bubble (no id yet, that's fine)
  appendMessage('user', content);
  appendTypingIndicator();

  try {
    const res = await PrismAPI.sendMessage(currentConvoId, content);
    if (!res) return;
    const data = await res.json();

    removeTypingIndicator();

    // Reload all messages so every message has proper ids from DB
    await loadMessages(currentConvoId);

    const badge = document.getElementById('model-badge');
    const badgeText = document.getElementById('model-badge-text');
    badge.style.display = 'flex';
    badgeText.textContent = data.model_used;

    await loadConversations();
    const updatedConvo = allConversations.find(c => c.id === currentConvoId);
    if (updatedConvo) {
      document.getElementById('chat-title').textContent = updatedConvo.title;
    }

  } catch (err) {
    removeTypingIndicator();
    appendMessage('assistant', 'Something went wrong. Please try again.');
  } finally {
    document.getElementById('send-btn').disabled = false;
  }
}

// ── New Conversation ──
document.getElementById('new-convo-btn').addEventListener('click', async () => {
  const res = await PrismAPI.createConversation('New Conversation');
  if (!res) return;
  const convo = await res.json();
  await loadConversations();
  selectConversation(convo.id, convo.title, null);
});

// ── Search ──
document.getElementById('search-input').addEventListener('input', () => renderSidebar());

// ── Input ──
const messageInput = document.getElementById('message-input');

messageInput.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = messageInput.scrollHeight + 'px';
  document.getElementById('send-btn').disabled = messageInput.value.trim() === '';
});

messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

document.getElementById('send-btn').addEventListener('click', sendMessage);

// ── Logout ──
document.getElementById('logout-btn').addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
});

// ── Utilities ──
function scrollToBottom() {
  const area = document.getElementById('messages-area');
  area.scrollTop = area.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

document.getElementById('settings-btn').addEventListener('click', () => {
  window.location.href = '/settings';
});

// ── Start ──
init();