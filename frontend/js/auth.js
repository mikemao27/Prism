const API = 'http://127.0.0.1:8000';

// ── View toggling ──
document.getElementById('go-register').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('login-view').style.display = 'none';
  document.getElementById('register-view').style.display = 'block';
  clearError();
});

document.getElementById('go-login').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('register-view').style.display = 'none';
  document.getElementById('login-view').style.display = 'block';
  clearError();
});

// ── Error display ──
function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent = msg;
  el.style.display = 'block';
}

function clearError() {
  const el = document.getElementById('error-msg');
  el.textContent = '';
  el.style.display = 'none';
}

// ── Login ──
document.getElementById('login-btn').addEventListener('click', async () => {
  clearError();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) {
    showError('Please fill in all fields.');
    return;
  }

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || 'Login failed.');
      return;
    }

    localStorage.setItem('token', data.access_token);
    window.location.href = 'app.html';

  } catch (err) {
    showError('Could not connect to Prism server.');
  }
});

// ── Register ──
document.getElementById('register-btn').addEventListener('click', async () => {
  clearError();
  const email = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;

  if (!email || !password) {
    showError('Please fill in all fields.');
    return;
  }

  if (password.length < 4) {
    showError('Password must be at least 4 characters.');
    return;
  }

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || 'Registration failed.');
      return;
    }

    localStorage.setItem('token', data.access_token);
    window.location.href = 'app.html';

  } catch (err) {
    showError('Could not connect to Prism server.');
  }
});

// ── Enter key support ──
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;
  const loginVisible = document.getElementById('login-view').style.display !== 'none';
  if (loginVisible) {
    document.getElementById('login-btn').click();
  } else {
    document.getElementById('register-btn').click();
  }
});

// ── Auto-redirect if already logged in ──
if (localStorage.getItem('token')) {
  window.location.href = '/app';
}