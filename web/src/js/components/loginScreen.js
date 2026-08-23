/**
 * NEXUS MIND - AUTHENTICATION & LOGIN/REGISTRATION GATEWAY
 * Supports:
 * 1. Standard JWT Sign-In with email & password
 * 2. New User Registration / Sign-Up with role and skill specification
 * 3. 1-Click Instant Demo Login for fast examiner review & viva presentations
 */
import { store } from '../state.js';

export function mountLoginScreen(onSuccess) {
  document.getElementById('nexusLoginOverlay')?.remove();

  const overlay = document.createElement('div');
  overlay.id = 'nexusLoginOverlay';
  overlay.innerHTML = `
    <style>
      #nexusLoginOverlay {
        position: fixed; inset: 0; z-index: 9999;
        display: flex; align-items: center; justify-content: center;
        background: radial-gradient(circle at 30% 20%, #161b33 0%, #060913 75%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        overflow-y: auto; padding: 20px;
      }
      #nexusLoginOverlay .login-card {
        width: 440px; max-width: 95vw; padding: 30px;
        background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 20px; backdrop-filter: blur(20px);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 35px rgba(0, 242, 254, 0.12);
      }
      #nexusLoginOverlay h1 {
        color: #fff; font-size: 1.55rem; margin: 0 0 4px; font-weight: 800;
        letter-spacing: -0.5px; text-align: center;
      }
      #nexusLoginOverlay p.sub { color: #94A3B8; font-size: 0.825rem; margin: 0 0 16px; text-align: center; }

      .auth-tabs-row {
        display: flex; gap: 6px; background: rgba(0, 0, 0, 0.35); padding: 4px;
        border-radius: 10px; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
      }
      .auth-tab-btn {
        flex: 1; padding: 8px; border-radius: 7px; border: none; background: transparent;
        color: #94A3B8; font-weight: 700; font-size: 0.8rem; cursor: pointer; transition: all 0.2s ease;
      }
      .auth-tab-btn.active {
        background: linear-gradient(90deg, rgba(0, 242, 254, 0.25), rgba(127, 0, 255, 0.25));
        color: #00F2FE; border: 1px solid rgba(0, 242, 254, 0.4);
      }

      .demo-section {
        background: rgba(127, 0, 255, 0.08); border: 1px solid rgba(127, 0, 255, 0.3);
        border-radius: 12px; padding: 12px; margin-bottom: 16px;
      }
      .demo-title {
        font-size: 0.75rem; font-weight: 800; color: #00F2FE;
        letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
      }
      .demo-roles-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
      }
      .demo-role-btn {
        padding: 7px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.05); color: #F1F5F9; font-size: 0.75rem; font-weight: 600;
        cursor: pointer; text-align: left; transition: all 0.2s ease;
      }
      .demo-role-btn:hover {
        background: rgba(0, 242, 254, 0.18); border-color: #00F2FE; transform: translateY(-1px);
      }

      .divider {
        display: flex; align-items: center; text-align: center; color: #64748B;
        font-size: 0.72rem; margin: 14px 0;
      }
      .divider::before, .divider::after {
        content: ''; flex: 1; border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      .divider:not(:empty)::before { margin-right: .5em; }
      .divider:not(:empty)::after { margin-left: .5em; }

      #nexusLoginOverlay label { color: #CBD5E1; font-size: 0.775rem; display: block; margin: 8px 0 3px; font-weight: 600; }
      #nexusLoginOverlay input, #nexusLoginOverlay select {
        width: 100%; box-sizing: border-box; padding: 9px 12px; border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.15); background: rgba(0,0,0,0.35); color: #fff; font-size: 0.825rem;
      }
      #nexusLoginOverlay button.btn-submit {
        margin-top: 14px; width: 100%; padding: 10px; border: none; border-radius: 8px;
        background: linear-gradient(90deg, #00F2FE, #7F00FF); color: #fff; font-weight: 700;
        cursor: pointer; font-size: 0.85rem; box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
      }
      #nexusLoginOverlay button:disabled { opacity: 0.6; cursor: default; }
      #nexusLoginOverlay .error-msg { color: #EF4444; font-size: 0.775rem; margin-top: 8px; min-height: 1.2em; text-align: center; }
    </style>
    
    <div class="login-card">
      <h1>NEXUS<span style="color:#00F2FE">MIND</span></h1>
      <p class="sub">Unified AI Workspace & Live Task Graph Platform</p>

      <!-- 1-Click Instant Demo Section -->
      <div class="demo-section">
        <div class="demo-title">⚡ 1-CLICK EXAMINER & DEMO ACCESS</div>
        <div class="demo-roles-grid">
          <button class="demo-role-btn" data-role="team_lead">👩‍💼 Sarah (Team Lead)</button>
          <button class="demo-role-btn" data-role="employee">👨‍💻 Alex (Lead Dev)</button>
          <button class="demo-role-btn" data-role="project_manager">📊 Marcus (Proj Mgr)</button>
          <button class="demo-role-btn" data-role="admin">🛡️ Elena (Admin)</button>
        </div>
      </div>

      <div class="divider">OR USE AUTHENTICATION CREDENTIALS</div>

      <!-- Tabs: Sign In / Create Account -->
      <div class="auth-tabs-row">
        <button class="auth-tab-btn active" id="tabBtnSignIn">Sign In</button>
        <button class="auth-tab-btn" id="tabBtnRegister">Create Account</button>
      </div>

      <!-- FORM 1: SIGN IN -->
      <form id="nexusLoginForm">
        <label for="nexusLoginEmail">Email Address</label>
        <input id="nexusLoginEmail" type="email" required autocomplete="username" placeholder="sarah.jenkins@nexusmind.ai" value="sarah.jenkins@nexusmind.ai" />
        
        <label for="nexusLoginPassword">Password</label>
        <input id="nexusLoginPassword" type="password" required autocomplete="current-password" placeholder="••••••••" value="nexus-demo-2026" />
        
        <button type="submit" id="nexusLoginSubmit" class="btn-submit">Sign In to Workspace</button>
        <div class="error-msg" id="nexusLoginError"></div>
      </form>

      <!-- FORM 2: CREATE ACCOUNT (REGISTER) -->
      <form id="nexusRegisterForm" class="hidden">
        <label for="nexusRegName">Full Name</label>
        <input id="nexusRegName" type="text" required placeholder="e.g. Jordan Miller" />

        <label for="nexusRegEmail">Email Address</label>
        <input id="nexusRegEmail" type="email" required placeholder="jordan.miller@nexusmind.ai" />

        <label for="nexusRegPassword">Password (min 8 characters)</label>
        <input id="nexusRegPassword" type="password" required minlength="8" placeholder="Create strong password" />

        <label for="nexusRegRole">Organization Role</label>
        <select id="nexusRegRole">
          <option value="employee">👨‍💻 Software Engineer (Employee)</option>
          <option value="team_lead">👩‍💼 Team Lead</option>
          <option value="project_manager">📊 Project Manager</option>
          <option value="admin">🛡️ System Administrator</option>
        </select>

        <label for="nexusRegSkills">Skills & Domain Expertise (comma separated)</label>
        <input id="nexusRegSkills" type="text" placeholder="e.g. React, Python, PostgreSQL, Security" value="Python, React, FastApi" />

        <button type="submit" id="nexusRegisterSubmit" class="btn-submit">Create Account & Enter Workspace</button>
        <div class="error-msg" id="nexusRegisterError"></div>
      </form>
    </div>
  `;
  document.body.appendChild(overlay);

  // Tab switching
  const tabSignIn = overlay.querySelector('#tabBtnSignIn');
  const tabRegister = overlay.querySelector('#tabBtnRegister');
  const loginForm = overlay.querySelector('#nexusLoginForm');
  const registerForm = overlay.querySelector('#nexusRegisterForm');
  const loginError = overlay.querySelector('#nexusLoginError');
  const regError = overlay.querySelector('#nexusRegisterError');

  tabSignIn.addEventListener('click', () => {
    tabSignIn.classList.add('active');
    tabRegister.classList.remove('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.classList.add('active');
    tabSignIn.classList.remove('active');
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
  });

  // Demo role buttons
  overlay.querySelectorAll('.demo-role-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const role = e.currentTarget.getAttribute('data-role');
      store.loginDemo(role);
      overlay.remove();
      onSuccess();
    });
  });

  // Login handler
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.textContent = '';
    const submitBtn = overlay.querySelector('#nexusLoginSubmit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in…';

    const email = overlay.querySelector('#nexusLoginEmail').value.trim();
    const password = overlay.querySelector('#nexusLoginPassword').value;

    try {
      await store.login(email, password);
      overlay.remove();
      onSuccess();
    } catch (err) {
      loginError.textContent = err.message || 'Login failed. Check your credentials.';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In to Workspace';
    }
  });

  // Register handler
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    regError.textContent = '';
    const submitBtn = overlay.querySelector('#nexusRegisterSubmit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account…';

    const name = overlay.querySelector('#nexusRegName').value.trim();
    const email = overlay.querySelector('#nexusRegEmail').value.trim();
    const password = overlay.querySelector('#nexusRegPassword').value;
    const app_role = overlay.querySelector('#nexusRegRole').value;
    const roleLabels = {
      employee: 'Senior Engineer',
      team_lead: 'Engineering Team Lead',
      project_manager: 'Technical Project Manager',
      admin: 'Organization Administrator'
    };
    const role = roleLabels[app_role] || 'Software Engineer';
    const skillsRaw = overlay.querySelector('#nexusRegSkills').value;
    const skills = skillsRaw.split(',').map(s => s.trim()).filter(Boolean);

    try {
      await store.register({ name, email, password, role, app_role, skills });
      overlay.remove();
      onSuccess();
    } catch (err) {
      regError.textContent = err.message || 'Registration failed.';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Account & Enter Workspace';
    }
  });
}
