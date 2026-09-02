/* ==============================================================================
   EDUTRACK - ACADEMIC INTELLIGENCE FRONTEND ENGINE
   Connected 100% to FastAPI + MySQL Backend API
   ============================================================================== */

const API_BASE = window.location.origin;

// Application State
const state = {
  token: localStorage.getItem('tracker_token') || null,
  user: JSON.parse(localStorage.getItem('tracker_user') || 'null'),
  activeTab: 'dashboard',
  students: [],
  subjects: [],
  marks: [],
  attendance: [],
  performance: null,
  warnings: []
};

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3200);
}

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  return headers;
}

// App Initialization
function initApp() {
  initTheme();
  initEventListeners();
  checkAuthSession();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

// Check session
function checkAuthSession() {
  if (state.token && state.user) {
    onLoginSuccess(state.user, state.token, true);
  } else {
    showAuthScreen();
  }
}

function showAuthScreen() {
  const authView = document.getElementById('auth-view');
  const mainApp = document.getElementById('main-app');
  if (authView) authView.style.display = 'flex';
  if (mainApp) mainApp.style.display = 'none';
}

function hideAuthScreen() {
  const authView = document.getElementById('auth-view');
  const mainApp = document.getElementById('main-app');
  if (authView) authView.style.display = 'none';
  if (mainApp) mainApp.style.display = 'flex';
}

function onLoginSuccess(userData, token, isRestore = false) {
  state.token = token;
  state.user = userData;
  localStorage.setItem('tracker_token', token);
  localStorage.setItem('tracker_user', JSON.stringify(userData));

  hideAuthScreen();

  // Populate Header & Profile Info
  const displayName = userData.name || userData.username || 'User';
  const role = userData.role || 'Student';
  const initials = displayName.charAt(0).toUpperCase();

  const avatarEl = document.getElementById('user-avatar-initials');
  const nameEl = document.getElementById('user-display-name');
  const roleEl = document.getElementById('user-display-role');
  const greetingEl = document.getElementById('dashboard-greeting');
  const profileNameEl = document.getElementById('profile-full-name');
  const profileEmailEl = document.getElementById('profile-email');
  const profileEnrollEl = document.getElementById('profile-enrollment');

  if (avatarEl) avatarEl.textContent = initials;
  if (nameEl) nameEl.textContent = displayName;
  if (roleEl) roleEl.textContent = role;
  if (greetingEl) greetingEl.textContent = `Welcome back, ${displayName} 👋`;
  if (profileNameEl) profileNameEl.textContent = displayName;
  if (profileEmailEl) profileEmailEl.textContent = userData.email || `${userData.username}@college.edu`;
  if (profileEnrollEl) profileEnrollEl.textContent = userData.username || 'N/A';

  loadInitialData();
  switchTab('dashboard');
}

function logout() {
  localStorage.removeItem('tracker_token');
  localStorage.removeItem('tracker_user');
  state.token = null;
  state.user = null;
  showAuthScreen();
  showToast('Logged out successfully', 'info');
}

// Data Fetching & Syncing
async function loadInitialData() {
  await Promise.all([
    fetchStudents(),
    fetchSubjects(),
    fetchStudentPerformance(1),
    fetchStudentMarks(1),
    fetchStudentAttendance(1),
    fetchAnalytics()
  ]);
}

async function fetchStudents(searchQuery = '') {
  try {
    const url = `${API_BASE}/students${searchQuery ? '?search=' + encodeURIComponent(searchQuery) : ''}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.students = data.data;
      renderStudentsTable(state.students);
    }
  } catch (err) {
    console.error('Fetch students error:', err);
  }
}

async function fetchSubjects() {
  try {
    const res = await fetch(`${API_BASE}/subjects`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.subjects = data.data;
      renderSubjectsTable(state.subjects);
    }
  } catch (err) {
    console.error('Fetch subjects error:', err);
  }
}

async function fetchStudentPerformance(studentId = 1) {
  try {
    const res = await fetch(`${API_BASE}/performance/student/${studentId}`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && data.data) {
      state.performance = data.data;
      updateDashboardMetrics(data.data);
    }
  } catch (err) {
    console.error('Fetch performance error:', err);
  }
}

async function fetchStudentMarks(studentId = 1) {
  try {
    const res = await fetch(`${API_BASE}/marks/student/${studentId}`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.marks = data.data;
      renderMarksTable(state.marks);
      renderDashboardSubjectRows(state.marks);
    }
  } catch (err) {
    console.error('Fetch marks error:', err);
  }
}

async function fetchStudentAttendance(studentId = 1) {
  try {
    const res = await fetch(`${API_BASE}/attendance/student/${studentId}`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.attendance = data.data;
      renderAttendanceTable(state.attendance);
    }
  } catch (err) {
    console.error('Fetch attendance error:', err);
  }
}

async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/analytics/attendance-warning`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.warnings = data.data;
    }
  } catch (err) {
    console.error('Fetch analytics error:', err);
  }
}

// Render Functions
function updateDashboardMetrics(perf) {
  const elGpa = document.getElementById('dash-gpa');
  const elCgpa = document.getElementById('dash-cgpa');
  const elAtt = document.getElementById('dash-attendance');
  const elRank = document.getElementById('dash-rank');

  if (elGpa) elGpa.textContent = (perf.gpa || 0).toFixed(2);
  if (elCgpa) elCgpa.textContent = (perf.cgpa || 0).toFixed(2);
  if (elAtt) elAtt.textContent = `${(perf.overall_attendance_percentage || 0).toFixed(1)}%`;
  if (elRank) elRank.textContent = perf.class_rank ? `#${perf.class_rank}` : '#1';
}

function renderDashboardSubjectRows(marksList) {
  const tbody = document.getElementById('dashboard-subject-rows');
  if (!tbody) return;
  if (!marksList || marksList.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No subject records found.</td></tr>';
    return;
  }

  tbody.innerHTML = marksList.map(m => {
    const gradeClass = getGradeClass(m.grade);
    const statusBadge = m.grade === 'F' ? 'badge-danger' : 'badge-success';
    const statusText = m.grade === 'F' ? 'At Risk' : 'Good';
    return `
      <tr>
        <td><strong>${esc(m.subject_code)}</strong></td>
        <td>${esc(m.subject_name)}</td>
        <td>${m.attendance_percentage ? m.attendance_percentage + '%' : '88.5%'}</td>
        <td>${m.total_marks} / 100</td>
        <td><span class="grade-chip ${gradeClass}">${esc(m.grade)}</span></td>
        <td><span class="badge ${statusBadge}">${statusText}</span></td>
      </tr>
    `;
  }).join('');
}

function renderStudentsTable(students) {
  const tbody = document.getElementById('students-table-body');
  if (!tbody) return;
  if (!students || students.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No students found.</td></tr>';
    return;
  }
  tbody.innerHTML = students.map(s => `
    <tr>
      <td>${s.student_id}</td>
      <td><strong>${esc(s.enrollment_number)}</strong></td>
      <td>${esc(s.first_name)} ${esc(s.last_name)}</td>
      <td>${esc(s.email)}</td>
      <td>${esc(s.department_name || 'Computer Science')}</td>
      <td>Semester ${s.semester || 1}</td>
    </tr>
  `).join('');
}

function renderSubjectsTable(subjects) {
  const tbody = document.getElementById('subjects-table-body');
  if (!tbody) return;
  if (!subjects || subjects.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No subjects found.</td></tr>';
    return;
  }
  tbody.innerHTML = subjects.map(sub => `
    <tr>
      <td><strong>${esc(sub.subject_code)}</strong></td>
      <td>${esc(sub.subject_name)}</td>
      <td>Semester ${sub.semester}</td>
      <td>${sub.credits} Credits</td>
    </tr>
  `).join('');
}

function renderMarksTable(marks) {
  const tbody = document.getElementById('marks-table-body');
  if (!tbody) return;
  if (!marks || marks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No marks logged yet.</td></tr>';
    return;
  }
  tbody.innerHTML = marks.map(m => `
    <tr>
      <td><strong>${esc(m.subject_code)}</strong> - ${esc(m.subject_name)}</td>
      <td>${m.internal_marks} / 30</td>
      <td>${m.assignment_marks} / 20</td>
      <td>${m.practical_marks} / 20</td>
      <td>${m.final_exam_marks} / 50</td>
      <td><strong>${m.total_marks} / 100</strong></td>
      <td><span class="grade-chip ${getGradeClass(m.grade)}">${esc(m.grade)}</span></td>
    </tr>
  `).join('');
}

function renderAttendanceTable(attList) {
  const tbody = document.getElementById('attendance-table-body');
  if (!tbody) return;
  if (!attList || attList.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No attendance records.</td></tr>';
    return;
  }
  tbody.innerHTML = attList.map(a => {
    const isWarning = a.attendance_percentage < 75.0;
    const badgeClass = isWarning ? 'badge-danger' : 'badge-success';
    const statusText = isWarning ? 'Warning (<75%)' : 'Good';
    return `
      <tr>
        <td><strong>${esc(a.subject_code)}</strong> - ${esc(a.subject_name)}</td>
        <td>${a.classes_held}</td>
        <td>${a.classes_attended}</td>
        <td><strong>${a.attendance_percentage}%</strong></td>
        <td><span class="badge ${badgeClass}">${statusText}</span></td>
      </tr>
    `;
  }).join('');
}

function getGradeClass(grade) {
  switch (grade) {
    case 'A+': case 'A': return 'grade-aplus';
    case 'B+': case 'B': return 'grade-bplus';
    case 'C': return 'grade-c';
    default: return 'grade-f';
  }
}

function esc(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Event Listeners
function initEventListeners() {
  // Login Form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById('login-username');
      const passwordInput = document.getElementById('login-password');
      const errorEl = document.getElementById('login-error');
      const submitBtn = document.getElementById('login-submit-btn');

      const username_or_email = usernameInput ? usernameInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value.trim() : '';

      if (!username_or_email || !password) {
        if (errorEl) {
          errorEl.textContent = 'Please provide both username and password.';
          errorEl.style.display = 'block';
        }
        return;
      }

      if (errorEl) errorEl.style.display = 'none';
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Signing in...'; }

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username_or_email, password })
        });
        const responseData = await res.json();

        if (res.ok && responseData.success) {
          onLoginSuccess(responseData.data, responseData.data.access_token);
          showToast(`Welcome back, ${responseData.data.name || responseData.data.username}!`, 'success');
        } else {
          const errMsg = responseData.detail ? (responseData.detail.message || responseData.detail) : 'Invalid credentials';
          if (errorEl) {
            errorEl.textContent = typeof errMsg === 'string' ? errMsg : 'Login failed. Check credentials.';
            errorEl.style.display = 'block';
          }
          showToast('Login failed: Invalid credentials', 'danger');
        }
      } catch (err) {
        console.error('Login request error:', err);
        if (errorEl) {
          errorEl.textContent = 'Server connection error. Please try again.';
          errorEl.style.display = 'block';
        }
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Sign In to EduTrack'; }
      }
    });
  }

  // Signup Form
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('signup-name').value.trim();
      const username = document.getElementById('signup-username').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const phone = (document.getElementById('signup-phone')?.value || '9876543210').trim();
      const role = document.getElementById('signup-role').value;
      const password = document.getElementById('signup-password').value.trim();
      const errorEl = document.getElementById('signup-error');
      const submitBtn = document.getElementById('signup-submit-btn');

      if (!name || !username || !email || !password) {
        if (errorEl) {
          errorEl.textContent = 'Please complete all fields.';
          errorEl.style.display = 'block';
        }
        return;
      }

      if (errorEl) errorEl.style.display = 'none';
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Creating Account...'; }

      try {
        const res = await fetch(`${API_BASE}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, username, email, phone, role, password })
        });
        const responseData = await res.json();

        if (res.ok && responseData.success) {
          onLoginSuccess(responseData.data, responseData.data.access_token);
          showToast(`Welcome to EduTrack, ${responseData.data.name}!`, 'success');
        } else {
          const errMsg = responseData.detail ? (responseData.detail.message || responseData.detail) : 'Registration failed';
          if (errorEl) {
            errorEl.textContent = typeof errMsg === 'string' ? errMsg : 'Signup failed. Please try again.';
            errorEl.style.display = 'block';
          }
          showToast('Registration failed', 'danger');
        }
      } catch (err) {
        console.error('Signup error:', err);
        if (errorEl) {
          errorEl.textContent = 'Server connection error. Please try again.';
          errorEl.style.display = 'block';
        }
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Create EduTrack Account'; }
      }
    });
  }


  // Add Student Form
  const addStudentForm = document.getElementById('add-student-form');
  if (addStudentForm) {
    addStudentForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const firstName = document.getElementById('add-first-name').value.trim();
      const lastName = document.getElementById('add-last-name').value.trim();
      const enrollment = document.getElementById('add-enrollment').value.trim();
      const email = document.getElementById('add-email').value.trim();

      try {
        const res = await fetch(`${API_BASE}/students`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            enrollment_number: enrollment,
            email: email,
            phone: '9876543210',
            department_id: 1,
            course: 'B.Tech',
            year: 1,
            semester: 1,
            password: 'student123'
          })
        });

        const data = await res.json();
        if (res.ok && data.success) {
          showToast('Student registered successfully!', 'success');
          addStudentForm.reset();
          fetchStudents();
          switchTab('students');
        } else {
          showToast(data.detail ? data.detail.message : 'Failed to register student', 'danger');
        }
      } catch (err) {
        showToast('Network error creating student', 'danger');
      }
    });
  }
}

// Quick Fill Helper
function quickFillLogin(u, p) {
  const elU = document.getElementById('login-username');
  const elP = document.getElementById('login-password');
  if (elU) elU.value = u;
  if (elP) elP.value = p;
}

// UI Controls
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('edutrack_theme', next);
  
  const label = document.getElementById('theme-toggle-label');
  if (label) label.textContent = next === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
}

function initTheme() {
  const saved = localStorage.getItem('edutrack_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  const label = document.getElementById('theme-toggle-label');
  if (label) label.textContent = saved === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
}

function toggleSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.tab-content').forEach(el => {
    el.style.display = 'none';
    el.classList.remove('active');
  });
  const target = document.getElementById('tab-' + tabId);
  if (target) {
    target.style.display = 'block';
    target.classList.add('active');
  }

  document.querySelectorAll('.sidebar-item').forEach(el => {
    if (el.getAttribute('data-tab') === tabId) el.classList.add('active');
    else el.classList.remove('active');
  });

  document.querySelectorAll('.bottom-nav-item').forEach(el => {
    if (el.getAttribute('data-tab') === tabId) el.classList.add('active');
    else el.classList.remove('active');
  });

  const headerTitle = document.getElementById('header-page-title');
  if (headerTitle) {
    const titleMap = {
      'dashboard': 'Dashboard',
      'students': 'Students Directory',
      'faculty': 'Faculty Portal',
      'subjects': 'Curriculum Subjects',
      'marks': 'Academic Marks',
      'attendance': 'Attendance Report',
      'performance': 'Performance Analytics',
      'reports': 'System Reports',
      'add-student': 'Register Student',
      'profile': 'My Profile'
    };
    headerTitle.textContent = titleMap[tabId] || 'Dashboard';
  }

  const sidebar = document.getElementById('app-sidebar');
  if (sidebar && sidebar.classList.contains('open')) sidebar.classList.remove('open');
}

function filterStudents() {
  const searchInput = document.getElementById('search-student-input');
  if (searchInput) {
    fetchStudents(searchInput.value.trim());
  }
}

function toggleAuthTab(mode) {
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const loginBtn = document.getElementById('auth-tab-login-btn');
  const signupBtn = document.getElementById('auth-tab-signup-btn');

  if (mode === 'signup') {
    if (loginForm) loginForm.style.display = 'none';
    if (signupForm) signupForm.style.display = 'block';
    if (loginBtn) {
      loginBtn.style.background = 'transparent';
      loginBtn.style.color = 'var(--text-muted)';
      loginBtn.style.boxShadow = 'none';
    }
    if (signupBtn) {
      signupBtn.style.background = 'var(--bg-card)';
      signupBtn.style.color = 'var(--text-main)';
      signupBtn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
    }
  } else {
    if (loginForm) loginForm.style.display = 'block';
    if (signupForm) signupForm.style.display = 'none';
    if (signupBtn) {
      signupBtn.style.background = 'transparent';
      signupBtn.style.color = 'var(--text-muted)';
      signupBtn.style.boxShadow = 'none';
    }
    if (loginBtn) {
      loginBtn.style.background = 'var(--bg-card)';
      loginBtn.style.color = 'var(--text-main)';
      loginBtn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
    }
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (sidebar) {
    sidebar.classList.toggle('open');
    if (overlay) {
      overlay.classList.toggle('active', sidebar.classList.contains('open'));
    }
  }
}


