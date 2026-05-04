// ── Init ──
async function init() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = '/'; return; }

  const res = await PrismAPI.getMe();
  if (!res) return;
  const user = await res.json();
  document.getElementById('settings-email').textContent = user.email;

  await loadKeys();
}

// ── Password ──
document.getElementById('change-password-btn').addEventListener('click', async () => {
  const current = document.getElementById('current-password').value;
  const newPass = document.getElementById('new-password').value;
  const confirm = document.getElementById('confirm-password').value;

  hideMessages('password');

  if (!current || !newPass || !confirm) {
    showError('password', 'Please fill in all fields.');
    return;
  }
  if (newPass !== confirm) {
    showError('password', 'New passwords do not match.');
    return;
  }
  if (newPass.length < 4) {
    showError('password', 'Password must be at least 4 characters.');
    return;
  }

  const res = await PrismAPI.changePassword(current, newPass);
  if (!res) return;
  const data = await res.json();

  if (!res.ok) {
    showError('password', data.detail || 'Failed to update password.');
    return;
  }

  showSuccess('password', 'Password updated successfully.');
  document.getElementById('current-password').value = '';
  document.getElementById('new-password').value = '';
  document.getElementById('confirm-password').value = '';
});

// ── API Keys ──
async function loadKeys() {
  const res = await PrismAPI.getKeys();
  if (!res) return;
  const keys = await res.json();
  renderKeys(keys);
}

function renderKeys(keys) {
  const list = document.getElementById('keys-list');
  list.innerHTML = '';

  if (keys.length === 0) {
    list.innerHTML = `<div style="font-size:13px;color:var(--text-muted);text-align:center;padding:16px;">No API keys added yet.</div>`;
    return;
  }

  keys.forEach(key => {
    const item = document.createElement('div');
    item.className = 'key-item';
    item.innerHTML = `
      <div class="key-item-info">
        <div class="key-provider">${escapeHtml(key.provider)}</div>
        <div class="key-balance">${key.credit_balance ? 'Balance: ' + key.credit_balance : 'No balance tracked'}</div>
      </div>
      <div class="key-actions">
        <input
          type="text"
          class="key-balance-input"
          placeholder="$0.00"
          value="${key.credit_balance || ''}"
          data-id="${key.id}"
        />
        <button class="btn-update-balance" data-id="${key.id}">Update</button>
        <button class="btn-delete-key" data-id="${key.id}">✕</button>
      </div>
    `;

    item.querySelector('.btn-update-balance').addEventListener('click', async (e) => {
      const keyId = e.target.dataset.id;
      const input = item.querySelector('.key-balance-input');
      const res = await PrismAPI.updateBalance(keyId, input.value);
      if (res && res.ok) {
        showSuccess('keys', 'Balance updated.');
        await loadKeys();
      }
    });

    item.querySelector('.btn-delete-key').addEventListener('click', async (e) => {
      if (!confirm('Remove this API key?')) return;
      const keyId = e.target.dataset.id;
      await PrismAPI.deleteKey(keyId);
      await loadKeys();
    });

    list.appendChild(item);
  });
}

document.getElementById('add-key-btn').addEventListener('click', async () => {
  hideMessages('keys');
  const provider = document.getElementById('key-provider').value;
  const apiKey = document.getElementById('key-value').value.trim();
  const balance = document.getElementById('key-balance').value.trim();

  if (!apiKey) {
    showError('keys', 'Please enter an API key.');
    return;
  }

  const res = await PrismAPI.addKey(provider, apiKey, balance || null);
  if (!res) return;
  const data = await res.json();

  if (!res.ok) {
    showError('keys', data.detail || 'Failed to add key.');
    return;
  }

  showSuccess('keys', `${provider} key added successfully.`);
  document.getElementById('key-value').value = '';
  document.getElementById('key-balance').value = '';
  await loadKeys();
});

// ── Navigation ──
document.getElementById('back-btn').addEventListener('click', () => {
  window.location.href = '/app';
});

// ── Utilities ──
function showError(section, msg) {
  const el = document.getElementById(`${section}-error`);
  el.textContent = msg;
  el.style.display = 'block';
}

function showSuccess(section, msg) {
  const el = document.getElementById(`${section}-success`);
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function hideMessages(section) {
  document.getElementById(`${section}-error`).style.display = 'none';
  document.getElementById(`${section}-success`).style.display = 'none';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

// ── Start ──
init();