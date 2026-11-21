
// nginx proxy manager에 의해 서버 경로가 나뉘어짐.
// user_server
const API_USERS = '/api/users';
// inf_server
const API_INF = '/api/inf';
const $ = (id) => document.getElementById(id);

// 결과 응답
async function api(path, options = {}) {
  // same-origin : 같은 주소로 요청할 때, 세션 쿠기를 자동으로 함께 보냄.
  const res = await fetch(path, { credentials: 'same-origin', ...options });
  let data = null;
  try { data = await res.json(); } catch (e) { /* 본문 없음 */ }
  return { ok: res.ok, status: res.status, data };
}

// JSON을 POST하는 함수
function postJson(path, body) {
  return api(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

// 안내문구 표시
function showMessage(text, isError = false) {
  const el = $('message');
  el.textContent = text;
  el.classList.toggle('error', !!isError);
}

// 에러 응답에 대한 문구
function errorText(r, fallback) {
  const d = r.data || {};
  return (d.image && d.image[0]) || d.detail || `${fallback} (${r.status})`;
}

// 현재 로그인한 사용자 정보를 가져옴.
async function getMe() {
  const r = await api(`${API_USERS}/me/`);
  return r.ok ? r.data : null;
}
