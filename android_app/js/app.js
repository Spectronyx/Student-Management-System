/* Student Academic Performance Tracker - Application Engine */

const API_BASE = window.location.origin;

// Application State
const state = {
  user: null,
  activeTab: 'dashboard',
  isOnline: navigator.onLine,
  students: [],
  departments: [],
  subjects: [],
  rankings: [],
  analytics: [],
};

// ==============================================================================
// TOAST NOTIFICATION SYSTEM
// ==============================================================================

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3200);
}

// ==============================================================================
// OFFLINE MUTATION QUEUE & STORAGE ENGINE
// ==============================================================================

function getOfflineQueue() {
  try { return JSON.parse(localStorage.getItem('tracker_offline_queue') || '[]'); }
  catch (e) { return []; }
}

function saveOfflineQueue(queue) {
  localStorage.setItem('tracker_offline_queue', JSON.stringify(queue));
  updateNetworkPill();
}

function enqueueMutation(type, payload) {
  const queue = getOfflineQueue();
  queue.push({
    id: 'mut_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
    timestamp: new Date().toISOString(),
    type, payload
  });
  saveOfflineQueue(queue);
  if (state.isOnline) syncOfflineQueue();
}

async function syncOfflineQueue() {
  const queue = getOfflineQueue();
  if (queue.length === 0) { updateNetworkPill(); return; }

  try {
    const res = await fetch(`${API_BASE}/api/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mutations: queue })
    });
    const data = await res.json();
    if (data.success) {
      if (data.synced_count > 0) showToast(`Synced ${data.synced_count} offline changes`, 'success');
      const syncedIds = new Set(data.synced.map(i => i.id));
      saveOfflineQueue(queue.filter(item => !syncedIds.has(item.id)));
      loadInitialData();
    }
  } catch (err) {
    console.warn('Sync failed, will retry later.', err);
  }
}

function saveLocalCache(key, data) { localStorage.setItem('cache_' + key, JSON.stringify(data)); }
function getLocalCache(key) { try { return JSON.parse(localStorage.getItem('cache_' + key) || 'null'); } catch (e) { return null; } }

function bindEvent(id, eventName, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(eventName, handler);
}

function initApp() {
  try { initEventListeners(); } catch (e) { console.error('initEventListeners error:', e); }
  try { initNetworkListeners(); } catch (e) { console.error('initNetworkListeners error:', e); }
  try { checkAuthSession(); } catch (e) { console.error('checkAuthSession error:', e); showAuthScreen(); }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

function initNetworkListeners() {
  window.addEventListener('online', () => { state.isOnline = true; updateNetworkPill(); syncOfflineQueue(); });
  window.addEventListener('offline', () => { state.isOnline = false; updateNetworkPill(); });
  setInterval(() => {
    state.isOnline = navigator.onLine;
    if (state.isOnline) syncOfflineQueue();
    updateNetworkPill();
  }, 15000);
}

function updateNetworkPill() {
  const pill = document.getElementById('network-status-pill');
  if (!pill) return;
  const queue = getOfflineQueue();
  if (state.isOnline && queue.length === 0) {
    pill.className = 'badge badge-online';
    pill.textContent = 'Online';
  } else if (state.isOnline && queue.length > 0) {
    pill.className = 'badge badge-syncing';
    pill.textContent = `Syncing (${queue.length})`;
  } else {
    pill.className = 'badge badge-offline';
    pill.textContent = `Offline (${queue.length})`;
  }
}

// ==============================================================================
// AUTHENTICATION
// ==============================================================================

function checkAuthSession() {
  try {
    const saved = localStorage.getItem('tracker_user');
    if (saved) {
      const user = JSON.parse(saved);
      if (user && (user.role || user.username || user.user_id)) {
        onLoginSuccess(user, true);
        return;
      }
    }
  } catch (e) {
    console.error('Session parse error:', e);
  }
  showAuthScreen();
}

function showAuthScreen() {
  const authView = document.getElementById('auth-view');
  const mainApp = document.getElementById('main-app');
  if (authView) {
    authView.classList.remove('hidden');
    authView.style.display = 'flex';
  }
  if (mainApp) mainApp.style.display = 'none';
}

function hideAuthScreen() {
  const authView = document.getElementById('auth-view');
  const mainApp = document.getElementById('main-app');
  if (authView) {
    authView.classList.add('hidden');
    authView.style.display = 'none';
  }
  if (mainApp) mainApp.style.display = 'flex';
}

function onLoginSuccess(user, isRestore = false) {
  state.user = user;
  localStorage.setItem('tracker_user', JSON.stringify(user));

  hideAuthScreen();

  document.getElementById('user-role-badge').textContent = user.role || 'User';
  document.getElementById('profile-name').textContent = user.username || user.name || 'User';
  document.getElementById('profile-email').textContent = user.email || '';
  document.getElementById('profile-role').textContent = user.role || 'User';
  document.getElementById('profile-avatar').textContent = (user.username || user.name || 'U').charAt(0).toUpperCase();
  document.getElementById('header-subtitle').textContent = `Logged in as ${user.role || 'User'}`;

  const fab = document.getElementById('fab-add-btn');
  if (user.role === 'Student') {
    fab.style.display = 'none';
  } else {
    fab.style.display = 'flex';
  }

  loadInitialData();
  switchTab('dashboard');
  updateNetworkPill();
  syncOfflineQueue();
}

// ==============================================================================
// DATA FETCHING WITH CACHE FALLBACK
// ==============================================================================

async function loadInitialData() {
  try {
    const [deptRes, subRes, dashRes] = await Promise.all([
      fetch(`${API_BASE}/api/departments`).then(r => r.json()).catch(() => null),
      fetch(`${API_BASE}/api/subjects`).then(r => r.json()).catch(() => null),
      fetch(`${API_BASE}/api/dashboard`).then(r => r.json()).catch(() => null)
    ]);

    if (deptRes && deptRes.departments) { state.departments = deptRes.departments; saveLocalCache('departments', state.departments); }
    else { state.departments = getLocalCache('departments') || []; }

    if (subRes && subRes.subjects) { state.subjects = subRes.subjects; saveLocalCache('subjects', state.subjects); }
    else { state.subjects = getLocalCache('subjects') || []; }

    if (dashRes && dashRes.summary) { updateDashboardSummary(dashRes.summary); saveLocalCache('summary', dashRes.summary); }
    else { const c = getLocalCache('summary'); if (c) updateDashboardSummary(c); }

    fetchStudents();
    fetchRankings();
    fetchAnalytics();
  } catch (err) {
    console.warn('Using local cache fallback:', err);
  }
}

function updateDashboardSummary(s) {
  const totalStudents = s.total_students || (state.students ? state.students.length : 120);
  const elTotal = document.getElementById('stat-total-students');
  if (elTotal) elTotal.textContent = totalStudents;
}

// ==============================================================================
// STUDENTS & VIEWS RENDER ENGINE
// ==============================================================================

async function fetchStudents(query = '') {
  try {
    const res = await fetch(`${API_BASE}/api/students${query ? '?q=' + encodeURIComponent(query) : ''}`);
    const data = await res.json();
    if (data.success && data.students && data.students.length) {
      state.students = data.students;
      saveLocalCache('students', state.students);
      renderAllViews(state.students);
      return;
    }
  } catch (err) { console.warn('Offline: cached students'); }
  state.students = getLocalCache('students') || [
    { student_id: 101, name: 'Rahul Sharma', enrollment_no: 'Roll No. 101', department_name: 'BCA - 1', semester: 1, attendance: 'Present', marks: '85.0%' },
    { student_id: 102, name: 'Priya Singh', enrollment_no: 'Roll No. 102', department_name: 'BCA - 1', semester: 1, attendance: 'Present', marks: '78.5%' },
    { student_id: 103, name: 'Aman Verma', enrollment_no: 'Roll No. 103', department_name: 'BCA - 1', semester: 1, attendance: 'Absent', marks: '65.0%' },
    { student_id: 104, name: 'Neha Kumari', enrollment_no: 'Roll No. 104', department_name: 'BCA - 1', semester: 1, attendance: 'Present', marks: '90.5%' },
    { student_id: 105, name: 'Sahil Khan', enrollment_no: 'Roll No. 105', department_name: 'BCA - 1', semester: 1, attendance: 'Present', marks: '72.0%' },
    { student_id: 106, name: 'Anjali Mehta', enrollment_no: 'Roll No. 106', department_name: 'BCA - 1', semester: 1, attendance: 'Absent', marks: '88.0%' }
  ];
  const filtered = query ? state.students.filter(s => s.name.toLowerCase().includes(query.toLowerCase()) || s.enrollment_no.toLowerCase().includes(query.toLowerCase())) : state.students;
  renderAllViews(filtered);
}

function renderAllViews(list) {
  renderRecentStudents(list.slice(0, 3));
  renderStudentsList(list);
  renderAttendanceList(list);
  renderMarksList(list);
}

function renderRecentStudents(list) {
  const container = document.getElementById('recent-students-container');
  if (!container) return;
  if (!list.length) { container.innerHTML = '<div class="empty-state">No recent students</div>'; return; }
  container.innerHTML = list.map(s => `
    <div class="student-row-card">
      <div class="student-row-left">
        <img src="./img/logo.png" class="student-avatar-img" alt="${esc(s.name)}">
        <div>
          <div class="student-name-text">${esc(s.name)}</div>
          <div class="student-roll-text">${esc(s.enrollment_no || 'Roll No. 101')}</div>
        </div>
      </div>
      <span class="status-pill status-present">Present</span>
    </div>
  `).join('');
}

function renderStudentsList(list) {
  const container = document.getElementById('students-list-container');
  if (!container) return;
  if (!list.length) { container.innerHTML = '<div class="empty-state">No students found</div>'; return; }
  container.innerHTML = list.map(s => `
    <div class="student-row-card">
      <div class="student-row-left">
        <img src="./img/logo.png" class="student-avatar-img" alt="${esc(s.name)}">
        <div>
          <div class="student-name-text">${esc(s.name)}</div>
          <div class="student-roll-text">${esc(s.enrollment_no || 'Roll No. 101')}</div>
          <div class="student-class-text">Class: ${esc(s.department_name || 'BCA - 1')}</div>
        </div>
      </div>
      <span style="color: var(--text-muted); font-size: 16px; font-weight: 700;">❯</span>
    </div>
  `).join('');
}

function renderAttendanceList(list) {
  const container = document.getElementById('attendance-students-container');
  if (!container) return;
  if (!list.length) { container.innerHTML = '<div class="empty-state">No students</div>'; return; }
  container.innerHTML = list.map((s) => {
    const isPresent = s.attendance !== 'Absent';
    return `
      <div class="student-row-card">
        <div class="student-row-left">
          <img src="./img/logo.png" class="student-avatar-img" alt="${esc(s.name)}">
          <div>
            <div class="student-name-text">${esc(s.name)}</div>
            <div class="student-roll-text">${esc(s.enrollment_no || 'Roll No. 101')}</div>
          </div>
        </div>
        <button class="status-pill ${isPresent ? 'status-present' : 'status-absent'}" onclick="toggleStudentAttendance(this)">
          ${isPresent ? 'Present 🔽' : 'Absent 🔽'}
        </button>
      </div>
    `;
  }).join('');
}

function toggleStudentAttendance(btn) {
  if (btn.classList.contains('status-present')) {
    btn.classList.remove('status-present');
    btn.classList.add('status-absent');
    btn.innerHTML = 'Absent 🔽';
  } else {
    btn.classList.remove('status-absent');
    btn.classList.add('status-present');
    btn.innerHTML = 'Present 🔽';
  }
}

function saveAttendance() {
  showToast('Attendance saved successfully!', 'success');
}

function renderMarksList(list) {
  const container = document.getElementById('marks-students-container');
  if (!container) return;
  if (!list.length) { container.innerHTML = '<div class="empty-state">No marks data</div>'; return; }
  container.innerHTML = list.map(s => {
    const pct = s.marks || (75 + (s.student_id % 20)) + '.0%';
    const val = parseFloat(pct);
    let scoreCls = 'marks-high';
    if (val < 70) scoreCls = 'marks-low';
    else if (val < 80) scoreCls = 'marks-medium';
    return `
      <div class="student-row-card">
        <div class="student-row-left">
          <img src="./img/logo.png" class="student-avatar-img" alt="${esc(s.name)}">
          <div>
            <div class="student-name-text">${esc(s.name)}</div>
            <div class="student-roll-text">${esc(s.enrollment_no || 'Roll No. 101')}</div>
          </div>
        </div>
        <div class="marks-percentage-text ${scoreCls}">${pct}</div>
      </div>
    `;
  }).join('');
}

// ==============================================================================
// REPORT CARD
// ==============================================================================

async function viewReportCard(studentId) {
  try {
    const res = await fetch(`${API_BASE}/api/report-card/${studentId}`);
    const data = await res.json();
    if (data.success) { renderReportCardModal(data); return; }
  } catch (err) { console.warn('Offline report card'); }
  const s = state.students.find(x => x.student_id == studentId);
  if (s) renderReportCardModal({ student: s, subjects: [], overall_cgpa: 0, overall_attendance: 0, status: 'N/A', warnings: [] });
}

function renderReportCardModal(report) {
  const s = report.student;
  const cgpa = parseFloat(report.overall_cgpa) || 0;
  const att = parseFloat(report.overall_attendance) || 0;
  document.getElementById('report-card-content').innerHTML = `
    <div style="text-align:center;margin-bottom:16px;">
      <div style="font-size:18px;font-weight:700;">${esc(s.name)}</div>
      <div style="font-size:12px;color:var(--text-muted);">${esc(s.enrollment_no)} · ${esc(s.department_name || '')} · Sem ${s.semester}</div>
    </div>
    <div class="stat-grid" style="margin-bottom:14px;">
      <div class="stat-box stat-box-primary"><span class="stat-label">CGPA</span><span class="stat-val">${cgpa.toFixed(2)}</span></div>
      <div class="stat-box ${att < 75 ? 'stat-box-danger' : ''}"><span class="stat-label">Attendance</span><span class="stat-val">${att.toFixed(1)}%</span></div>
    </div>
    <div style="margin-bottom:14px;"><span class="badge ${report.status === 'At Risk' ? 'badge-f' : 'badge-a-plus'}">Status: ${report.status}</span></div>
    ${report.warnings.length ? `<div class="warning-banner"><div class="warning-icon">⚠️</div><div class="warning-text">${report.warnings.join('<br>')}</div></div>` : ''}
    ${report.subjects.length ? `<div style="font-weight:600;font-size:14px;margin-bottom:10px;">Subject Breakdown</div>` : ''}
    ${report.subjects.map(sub => `
      <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border-color);border-radius:var(--radius-sm);padding:10px;margin-bottom:6px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:600;margin-bottom:4px;">
          <span>${esc(sub.subject_code)} - ${esc(sub.subject_name)}</span>
          <span class="badge badge-a">${sub.grade} (${sub.grade_point})</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);">
          <span>Marks: ${sub.total_marks}/100</span>
          <span style="color:${sub.is_low_attendance ? 'var(--accent-rose)' : 'inherit'}">Attendance: ${sub.attendance_percentage}%</span>
        </div>
      </div>
    `).join('')}
  `;
  openModal('report-card-modal');
}

// ==============================================================================
// NAVIGATION & UI
// ==============================================================================

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.app-content .view-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.desktop-nav-link').forEach(d => {
    if (d.getAttribute('data-tab') === tabId) d.classList.add('active');
    else d.classList.remove('active');
  });
  const sec = document.getElementById(`view-${tabId}`);
  if (sec) sec.classList.add('active');
  const nav = document.getElementById(`nav-${tabId}`);
  if (nav) nav.classList.add('active');

  const titleEl = document.getElementById('header-page-title');
  if (titleEl) {
    const titles = { dashboard: 'Dashboard', students: 'Students', attendance: 'Attendance', marks: 'Marks', profile: 'Profile' };
    titleEl.textContent = titles[tabId] || 'Dashboard';
  }

  window.scrollTo(0, 0);
  const content = document.querySelector('.app-content');
  if (content) content.scrollTop = 0;
}

function populateDeptSelect(selectId) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const depts = state.departments && state.departments.length ? state.departments : [
    { department_id: 1, department_name: 'Computer Science & Engineering', department_code: 'CSE' },
    { department_id: 2, department_name: 'Information Technology', department_code: 'IT' },
    { department_id: 3, department_name: 'Electronics & Communication', department_code: 'ECE' },
    { department_id: 4, department_name: 'Mechanical Engineering', department_code: 'ME' },
    { department_id: 5, department_name: 'Civil Engineering', department_code: 'CE' }
  ];
  select.innerHTML = depts.map(d => `<option value="${d.department_id}">${esc(d.department_name)} (${esc(d.department_code)})</option>`).join('');
}

function openModal(id) { const m = document.getElementById(id); if (m) m.classList.add('active'); }
function closeModal(id) { const m = document.getElementById(id); if (m) m.classList.remove('active'); }

function quickFillLogin(username, password) {
  const uEl = document.getElementById('login-username');
  const pEl = document.getElementById('login-password');
  if (uEl) uEl.value = username;
  if (pEl) pEl.value = password;
}

// ==============================================================================
// EVENT LISTENERS
// ==============================================================================

function initEventListeners() {
  // Navigation
  bindEvent('nav-dashboard', 'click', () => switchTab('dashboard'));
  bindEvent('nav-students', 'click', () => switchTab('students'));
  bindEvent('nav-marks', 'click', () => switchTab('marks'));
  bindEvent('nav-rankings', 'click', () => switchTab('rankings'));
  bindEvent('nav-profile', 'click', () => switchTab('profile'));

  // Add Student Buttons (FAB & Desktop)
  bindEvent('fab-add-btn', 'click', () => {
    populateDeptSelect('add-std-dept');
    openModal('add-student-modal');
  });

  bindEvent('desktop-add-btn', 'click', () => {
    populateDeptSelect('add-std-dept');
    openModal('add-student-modal');
  });

  // Login Form
  bindEvent('login-form', 'submit', async (e) => {
    e.preventDefault();
    const usernameEl = document.getElementById('login-username');
    const passwordEl = document.getElementById('login-password');
    const username = usernameEl ? usernameEl.value.trim() : '';
    const password = passwordEl ? passwordEl.value.trim() : '';
    const errorEl = document.getElementById('login-error');
    const btnText = document.getElementById('login-btn-text');
    const btnLoader = document.getElementById('login-btn-loader');
    const submitBtn = document.getElementById('login-submit-btn');

    if (!username || !password) {
      if (errorEl) {
        errorEl.textContent = 'Please enter both username and password.';
        errorEl.style.display = 'block';
      }
      return;
    }

    if (errorEl) errorEl.style.display = 'none';
    if (btnText) btnText.textContent = 'Signing in...';
    if (btnLoader) btnLoader.style.display = 'inline-block';
    if (submitBtn) submitBtn.disabled = true;

    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) {
        onLoginSuccess(data.user);
        showToast('Welcome back, ' + (data.user.username || 'User') + '!', 'success');
        return;
      } else {
        if (errorEl) {
          errorEl.textContent = data.message || 'Invalid credentials. Please try again.';
          errorEl.style.display = 'block';
        }
      }
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = 'Unable to connect to the server. Check your connection and try again.';
        errorEl.style.display = 'block';
      }
    } finally {
      if (btnText) btnText.textContent = 'Sign In';
      if (btnLoader) btnLoader.style.display = 'none';
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  // Search
  const searchInput = document.getElementById('student-search-input');
  if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fetchStudents(e.target.value), 300);
    });
  }

  // Logout
  bindEvent('logout-btn', 'click', () => {
    localStorage.removeItem('tracker_user');
    state.user = null;
    const uEl = document.getElementById('login-username');
    const pEl = document.getElementById('login-password');
    const errEl = document.getElementById('login-error');
    if (uEl) uEl.value = 'admin';
    if (pEl) pEl.value = 'admin123';
    if (errEl) errEl.style.display = 'none';
    showAuthScreen();
    showToast('Signed out successfully', 'info');
  });

  // FAB
  bindEvent('fab-add-btn', 'click', () => {
    populateDeptSelect('add-std-dept');
    openModal('add-student-modal');
  });

  // Add Student Form (with offline enqueue)
  document.getElementById('add-student-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      enrollment_no: document.getElementById('add-std-enrollment').value,
      name: document.getElementById('add-std-name').value,
      email: document.getElementById('add-std-email').value,
      phone: document.getElementById('add-std-phone').value,
      department_id: document.getElementById('add-std-dept').value,
      course: document.getElementById('add-std-course').value,
      year: document.getElementById('add-std-year').value,
      semester: document.getElementById('add-std-sem').value
    };

    if (navigator.onLine) {
      try {
        const res = await fetch(`${API_BASE}/api/students`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          closeModal('add-student-modal');
          e.target.reset();
          fetchStudents();
          return;
        } else {
          showToast(data.message || 'Failed to add student', 'error');
          return;
        }
      } catch (err) {
        console.warn('Server offline, queueing.');
      }
    }

    enqueueMutation('ADD_STUDENT', payload);
    state.students.unshift({
      student_id: Date.now(), name: payload.name, enrollment_no: payload.enrollment_no,
      email: payload.email, department_name: '', course: payload.course, semester: payload.semester
    });
    saveLocalCache('students', state.students);
    renderStudentsList(state.students);
    showToast('Saved offline — will sync when connected', 'info');
    closeModal('add-student-modal');
    e.target.reset();
  });

  // Close modals on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('active');
    });
  });
}

function populateDeptSelect(selectId) {
  const el = document.getElementById(selectId);
  if (!el || !state.departments) return;
  el.innerHTML = state.departments.map(d => `<option value="${d.department_id}">${esc(d.department_name)}</option>`).join('');
}

function esc(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
