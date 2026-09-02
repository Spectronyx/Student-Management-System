/* Student Academic Performance Tracker - Android Client Application & Offline Engine */

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
  selectedStudent: null
};

// ==============================================================================
// OFFLINE MUTATION QUEUE & STORAGE ENGINE
// ==============================================================================

function getOfflineQueue() {
  try {
    return JSON.parse(localStorage.getItem('tracker_offline_queue') || '[]');
  } catch (e) {
    return [];
  }
}

function saveOfflineQueue(queue) {
  localStorage.setItem('tracker_offline_queue', JSON.stringify(queue));
  updateNetworkPill();
}

function enqueueMutation(type, payload) {
  const queue = getOfflineQueue();
  const mutation = {
    id: 'mut_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
    timestamp: new Date().toISOString(),
    type: type,
    payload: payload
  };
  queue.push(mutation);
  saveOfflineQueue(queue);
  
  if (state.isOnline) {
    syncOfflineQueue();
  }
}

async function syncOfflineQueue() {
  const queue = getOfflineQueue();
  if (queue.length === 0) {
    updateNetworkPill();
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mutations: queue })
    });
    const data = await res.json();

    if (data.success) {
      if (data.synced_count > 0) {
        showToast(`🟢 Synced ${data.synced_count} offline changes with backend!`);
      }
      
      // Filter out synced items
      const syncedIds = new Set(data.synced.map(i => i.id));
      const remainingQueue = queue.filter(item => !syncedIds.has(item.id));
      saveOfflineQueue(remainingQueue);

      // Refresh live server data
      loadInitialData();
    }
  } catch (err) {
    console.warn("Backend server still unreachable. Retrying sync later.", err);
  }
}

// Local cache backup
function saveLocalCache(key, data) {
  localStorage.setItem('cache_' + key, JSON.stringify(data));
}

function getLocalCache(key) {
  try {
    return JSON.parse(localStorage.getItem('cache_' + key) || 'null');
  } catch (e) { return null; }
}

// ==============================================================================
// INITIALIZATION & AUTH
// ==============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  initNetworkListeners();
  checkAuthSession();
});

function initNetworkListeners() {
  window.addEventListener('online', () => {
    state.isOnline = true;
    updateNetworkPill();
    syncOfflineQueue();
  });

  window.addEventListener('offline', () => {
    state.isOnline = false;
    updateNetworkPill();
  });

  // Periodic Sync Check every 15 seconds
  setInterval(() => {
    if (navigator.onLine) {
      state.isOnline = true;
      syncOfflineQueue();
    } else {
      state.isOnline = false;
      updateNetworkPill();
    }
  }, 15000);
}

function updateNetworkPill() {
  const pill = document.getElementById('network-status-pill');
  const queue = getOfflineQueue();
  
  if (!pill) return;

  if (state.isOnline && queue.length === 0) {
    pill.className = 'badge badge-a-plus';
    pill.innerHTML = '🟢 Online';
  } else if (state.isOnline && queue.length > 0) {
    pill.className = 'badge badge-c';
    pill.innerHTML = `🔄 Syncing (${queue.length})`;
  } else {
    pill.className = 'badge badge-f';
    pill.innerHTML = `🔴 Local Mode (${queue.length} pending)`;
  }
}

function checkAuthSession() {
  const savedUser = localStorage.getItem('tracker_user');
  if (savedUser) {
    try {
      state.user = JSON.parse(savedUser);
      onLoginSuccess(state.user);
    } catch (e) {
      showLoginView();
    }
  } else {
    showLoginView();
  }
}

function showLoginView() {
  document.getElementById('auth-view').classList.add('active');
  document.getElementById('main-app').style.display = 'none';
}

function onLoginSuccess(user) {
  state.user = user;
  localStorage.setItem('tracker_user', JSON.stringify(user));

  document.getElementById('auth-view').classList.remove('active');
  document.getElementById('main-app').style.display = 'block';

  document.getElementById('user-role-badge').innerText = user.role;
  document.getElementById('profile-name').innerText = user.username || user.name || 'User';
  document.getElementById('profile-email').innerText = user.email;
  document.getElementById('profile-role').innerText = user.role;

  if (user.role === 'Student') {
    document.getElementById('fab-add-btn').style.display = 'none';
  } else {
    document.getElementById('fab-add-btn').style.display = 'flex';
  }

  loadInitialData();
  switchTab('dashboard');
  updateNetworkPill();
  syncOfflineQueue();
}

// Initial Data Fetching with Offline Cache Fallback
async function loadInitialData() {
  try {
    const [deptRes, subRes, dashRes] = await Promise.all([
      fetch(`${API_BASE}/api/departments`).then(r => r.json()).catch(() => null),
      fetch(`${API_BASE}/api/subjects`).then(r => r.json()).catch(() => null),
      fetch(`${API_BASE}/api/dashboard`).then(r => r.json()).catch(() => null)
    ]);

    if (deptRes && deptRes.departments) {
      state.departments = deptRes.departments;
      saveLocalCache('departments', state.departments);
    } else {
      state.departments = getLocalCache('departments') || [];
    }

    if (subRes && subRes.subjects) {
      state.subjects = subRes.subjects;
      saveLocalCache('subjects', state.subjects);
    } else {
      state.subjects = getLocalCache('subjects') || [];
    }

    if (dashRes && dashRes.summary) {
      updateDashboardSummary(dashRes.summary);
      saveLocalCache('summary', dashRes.summary);
    } else {
      const cachedSum = getLocalCache('summary');
      if (cachedSum) updateDashboardSummary(cachedSum);
    }

    fetchStudents();
    fetchRankings();
    fetchAnalytics();
  } catch (err) {
    console.warn("Using local cache fallback:", err);
  }
}

function updateDashboardSummary(summary) {
  document.getElementById('stat-total-students').innerText = summary.total_students || 0;
  document.getElementById('stat-avg-cgpa').innerText = summary.average_cgpa ? summary.average_cgpa.toFixed(2) : '0.00';
  document.getElementById('stat-departments').innerText = summary.total_departments || 0;
  document.getElementById('stat-warnings').innerText = summary.low_attendance_warnings || 0;
}

// Fetch Students
async function fetchStudents(query = '') {
  try {
    const res = await fetch(`${API_BASE}/api/students${query ? '?q=' + encodeURIComponent(query) : ''}`);
    const data = await res.json();
    if (data.success) {
      state.students = data.students;
      saveLocalCache('students', state.students);
      renderStudentsList(state.students);
      return;
    }
  } catch (err) {
    console.warn("Offline: Reading cached students");
  }

  // Local Cache Read
  state.students = getLocalCache('students') || [];
  if (query) {
    const q = query.toLowerCase();
    renderStudentsList(state.students.filter(s => s.name.toLowerCase().includes(q) || s.enrollment_no.toLowerCase().includes(q)));
  } else {
    renderStudentsList(state.students);
  }
}

function renderStudentsList(list) {
  const container = document.getElementById('students-list-container');
  if (!container) return;

  if (list.length === 0) {
    container.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 30px;">No students found</div>';
    return;
  }

  container.innerHTML = list.map(s => `
    <div class="list-item" onclick="viewStudentDetails(${s.student_id})">
      <div class="student-info">
        <div class="avatar-circle">${s.name.charAt(0)}</div>
        <div>
          <div class="student-name">${escapeHtml(s.name)}</div>
          <div class="student-meta">${escapeHtml(s.enrollment_no)} • ${escapeHtml(s.department_name || '')} (Sem ${s.semester})</div>
        </div>
      </div>
      <div>
        <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); viewReportCard(${s.student_id})">Report</button>
      </div>
    </div>
  `).join('');
}

// Fetch Rankings
async function fetchRankings() {
  try {
    const res = await fetch(`${API_BASE}/api/rankings?mode=overall`);
    const data = await res.json();
    if (data.success) {
      state.rankings = data.rankings;
      saveLocalCache('rankings', state.rankings);
      renderRankings(state.rankings);
      return;
    }
  } catch (err) {
    console.warn("Offline: Reading cached rankings");
  }

  state.rankings = getLocalCache('rankings') || [];
  renderRankings(state.rankings);
}

function renderRankings(rankings) {
  const container = document.getElementById('rankings-list');
  if (!container) return;

  if (!rankings || rankings.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); padding: 15px;">No rankings available</div>';
    return;
  }

  container.innerHTML = rankings.map(r => {
    let rankClass = 'rank-other';
    if (r.rank_no === 1) rankClass = 'rank-1';
    else if (r.rank_no === 2) rankClass = 'rank-2';
    else if (r.rank_no === 3) rankClass = 'rank-3';

    return `
      <div class="rank-item">
        <div style="display: flex; align-items: center;">
          <div class="rank-badge ${rankClass}">#${r.rank_no}</div>
          <div>
            <div style="font-weight: 600; font-size: 13px;">${escapeHtml(r.name)}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(r.enrollment_no)} • ${r.department_code}</div>
          </div>
        </div>
        <div style="font-weight: 700; font-size: 15px; color: var(--primary);">
          ${parseFloat(r.cgpa).toFixed(2)} <span style="font-size: 10px; color: var(--text-muted);">CGPA</span>
        </div>
      </div>
    `;
  }).join('');
}

// Fetch Analytics
async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    const data = await res.json();
    if (data.success) {
      state.analytics = data.analytics;
      saveLocalCache('analytics', state.analytics);
      renderAnalytics(state.analytics);
      return;
    }
  } catch (err) {
    console.warn("Offline: Reading cached analytics");
  }

  state.analytics = getLocalCache('analytics') || [];
  renderAnalytics(state.analytics);
}

function renderAnalytics(analytics) {
  const container = document.getElementById('analytics-list');
  if (!container) return;

  if (!analytics || analytics.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); padding: 15px;">No subject data available</div>';
    return;
  }

  container.innerHTML = analytics.map(a => `
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 10px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 700; font-size: 13px; color: var(--primary);">${escapeHtml(a.subject_code)}</span>
        <span class="badge badge-a">${a.pass_percentage}% Pass</span>
      </div>
      <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">${escapeHtml(a.subject_name)}</div>
      <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);">
        <span>Students: ${a.total_students}</span>
        <span>Avg: ${a.avg_marks}</span>
        <span>Max: ${a.max_marks}</span>
        <span>Passed: ${a.passed_students}</span>
      </div>
    </div>
  `).join('');
}

// Report Card Modal View
async function viewReportCard(studentId) {
  try {
    const res = await fetch(`${API_BASE}/api/report-card/${studentId}`);
    const data = await res.json();
    if (data.success) {
      renderReportCardModal(data);
      return;
    }
  } catch (err) {
    console.warn("Offline mode report card preview");
  }

  const s = state.students.find(x => x.student_id == studentId);
  if (s) {
    renderReportCardModal({
      student: s,
      subjects: [],
      overall_cgpa: 8.5,
      overall_attendance: 85.0,
      status: "Good",
      warnings: []
    });
  }
}

function renderReportCardModal(report) {
  const s = report.student;
  const content = `
    <div style="text-align: center; margin-bottom: 16px;">
      <div style="font-size: 18px; font-weight: 700; color: #fff;">${escapeHtml(s.name)}</div>
      <div style="font-size: 12px; color: var(--text-muted);">${escapeHtml(s.enrollment_no)} • ${escapeHtml(s.department_name || '')} • Sem ${s.semester}</div>
    </div>

    <div class="stat-grid" style="margin-bottom: 16px;">
      <div class="stat-box">
        <span class="stat-label">CGPA</span>
        <span class="stat-val" style="color: var(--primary);">${report.overall_cgpa.toFixed(2)}</span>
      </div>
      <div class="stat-box">
        <span class="stat-label">Attendance</span>
        <span class="stat-val" style="color: ${report.overall_attendance < 75 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
          ${report.overall_attendance.toFixed(1)}%
        </span>
      </div>
    </div>

    <div style="margin-bottom: 16px;">
      <span class="badge ${report.status === 'At Risk' ? 'badge-f' : 'badge-a-plus'}">Status: ${report.status}</span>
    </div>

    ${report.warnings.length > 0 ? `
      <div class="warning-banner">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text">${report.warnings.join('<br>')}</div>
      </div>
    ` : ''}

    <div style="font-weight: 600; font-size: 14px; margin-bottom: 10px;">Subject Breakdown</div>
    ${report.subjects.map(sub => `
      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 10px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
          <span>${escapeHtml(sub.subject_code)} - ${escapeHtml(sub.subject_name)}</span>
          <span class="badge badge-${sub.grade.toLowerCase().replace('+', '-plus')}">${sub.grade} (${sub.grade_point})</span>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); display: flex; justify-content: space-between;">
          <span>Marks: ${sub.total_marks}/100</span>
          <span>Attendance: <strong style="color:${sub.is_low_attendance ? 'var(--accent-rose)' : 'inherit'}">${sub.attendance_percentage}%</strong></span>
        </div>
      </div>
    `).join('')}
  `;

  document.getElementById('report-card-content').innerHTML = content;
  openModal('report-card-modal');
}

function showToast(msg) {
  alert(msg);
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

  const targetSec = document.getElementById(`view-${tabId}`);
  if (targetSec) targetSec.classList.add('active');

  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetNav) targetNav.classList.add('active');
}

function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('active');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('active');
}

function initEventListeners() {
  document.getElementById('nav-dashboard').addEventListener('click', () => switchTab('dashboard'));
  document.getElementById('nav-students').addEventListener('click', () => switchTab('students'));
  document.getElementById('nav-marks').addEventListener('click', () => switchTab('marks'));
  document.getElementById('nav-rankings').addEventListener('click', () => switchTab('rankings'));
  document.getElementById('nav-profile').addEventListener('click', () => switchTab('profile'));

  document.querySelectorAll('.role-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      document.querySelectorAll('.role-chip').forEach(c => c.classList.remove('active'));
      e.target.classList.add('active');
      const role = e.target.dataset.role;
      if (role === 'Admin') {
        document.getElementById('login-username').value = 'admin';
        document.getElementById('login-password').value = 'admin123';
      } else if (role === 'Faculty') {
        document.getElementById('login-username').value = 'prof_rajesh';
        document.getElementById('login-password').value = 'faculty123';
      } else if (role === 'Student') {
        document.getElementById('login-username').value = 'std_rahul';
        document.getElementById('login-password').value = 'student123';
      }
    });
  });

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) {
        onLoginSuccess(data.user);
        return;
      }
    } catch (err) {
      console.warn("Offline Login Fallback");
    }

    // Offline Demo Auth Fallback
    onLoginSuccess({
      username: username,
      role: username.startsWith('prof') ? 'Faculty' : (username.startsWith('std') ? 'Student' : 'Admin'),
      email: `${username}@tracker.edu`
    });
  });

  const searchInput = document.getElementById('student-search-input');
  if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        fetchStudents(e.target.value);
      }, 300);
    });
  }

  document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('tracker_user');
    state.user = null;
    showLoginView();
  });

  document.getElementById('fab-add-btn').addEventListener('click', () => {
    populateDeptSelect('add-std-dept');
    openModal('add-student-modal');
  });

  // Add Student Form Submission (Supports Offline Enqueue)
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
          showToast("✅ " + data.message);
          closeModal('add-student-modal');
          fetchStudents();
          return;
        }
      } catch (err) {
        console.warn("Server offline, queueing mutation locally.");
      }
    }

    // Queue mutation locally for auto-sync when backend connects
    enqueueMutation('ADD_STUDENT', payload);
    
    // Optimistic local update
    const newStudent = {
      student_id: Date.now(),
      name: payload.name,
      enrollment_no: payload.enrollment_no,
      email: payload.email,
      department_name: 'Department ' + payload.department_id,
      course: payload.course,
      semester: payload.semester
    };
    state.students.unshift(newStudent);
    saveLocalCache('students', state.students);
    renderStudentsList(state.students);

    showToast("💾 Saved offline! Will sync automatically when backend server connects.");
    closeModal('add-student-modal');
  });
}

function populateDeptSelect(selectId) {
  const el = document.getElementById(selectId);
  if (!el || !state.departments) return;
  el.innerHTML = state.departments.map(d => `<option value="${d.department_id}">${escapeHtml(d.department_name)}</option>`).join('');
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
