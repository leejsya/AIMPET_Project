
// ======= 추론 패아지 동작 ========

const THRESHOLD = 0.5; // 이진 분류 threshold 설정
let currentUser = null; // 로그인한 사용자
let currentId = null;      // 저장 여부를 아직 정하지 않은 결과의 id
let selectedFile = null;   // 선택된 이미지 파일
const DROP_TEXT = $('drop-text').textContent; // 안내 문구

// prob를 score로 변환
function toPercent(prob) { return (prob * 100).toFixed(1) + '%'; }

// score에 따라 benign/malignant 라벨 결정
function fillBadge(el, prob) {
  const label = prob >= THRESHOLD ? 'malignant' : 'benign';
  el.className = 'badge ' + label;
  el.textContent = label;
  return el;
}

// 원본이미지와 히트맵 이미지 표시
function camBox(r) {
  const box = document.createElement('div');
  box.className = 'cam-box small';
  const img = document.createElement('img');
  img.src = r.image;
  img.alt = '#' + r.id;
  box.appendChild(img);
  if (r.heatmap) {
    const heat = document.createElement('img');
    heat.className = 'cam-heatmap';
    heat.src = r.heatmap;
    heat.alt = '';
    box.appendChild(heat);
  }
  return box;
}

function cell(child, className) {
  const td = document.createElement('td');
  if (className) td.className = className;
  if (typeof child === 'string') td.textContent = child;
  else td.appendChild(child);
  return td;
}

// 업로드 영역과 결과 영역을 리셋
function resetUpload() {
  currentId = null;
  selectedFile = null;
  $('image-input').value = '';
  $('drop-text').textContent = DROP_TEXT;
  $('result-area').classList.add('hidden');
}

// 로그인 여부에 따라 페이지 렌더링을 다르게
function renderAuth() {
  $('login-link').classList.toggle('hidden', !!currentUser);
  $('logout-btn').classList.toggle('hidden', !currentUser);
  $('user-name').textContent = currentUser ? currentUser.username + '님' : '';
  $('save-notice').textContent = currentUser
    ? '로그인 상태: 분석 결과를 저장할 수 있습니다.'
    : '비로그인 상태: 결과만 보여 주고 저장하지 않습니다.';
}

// 서버에서 결과를 삭제
async function deleteResult(id, ask) {
  if (ask && !confirm('#' + id + ' 결과를 삭제할까요?')) return false;
  const r = await api(`${API_INF}/results/${id}/`, { method: 'DELETE' });
  if (!r.ok) { showMessage(errorText(r, '삭제하지 못했습니다.'), true); return false; }
  return true;
}

// 저장된 결과 목록을 조회
async function loadList() {
  const body = $('result-list');
  body.textContent = '';
  if (!currentUser) {
    $('count').textContent = '';
    $('result-table').classList.add('hidden');
    $('empty').textContent = '로그인하면 저장된 결과가 여기에 표시됩니다.';
    $('empty').classList.remove('hidden');
    return;
  }
  const r = await api(`${API_INF}/results/`);
  if (!r.ok) { showMessage(errorText(r, '목록을 불러오지 못했습니다.'), true); return; }
  const all = Array.isArray(r.data) ? r.data : (r.data.results || []);
  const rows = all.filter((x) => x.id !== currentId);
  rows.forEach((x) => {
    const tr = document.createElement('tr');
    tr.appendChild(cell(camBox(x)));
    tr.appendChild(cell(fillBadge(document.createElement('span'), x.malignant_prob)));
    tr.appendChild(cell(toPercent(x.malignant_prob), 'num'));
    tr.appendChild(cell(new Date(x.created_time).toLocaleString('ko-KR')));
    const del = document.createElement('button');
    del.className = 'danger';
    del.textContent = '삭제';
    del.addEventListener('click', async () => {
      if (await deleteResult(x.id, true)) { showMessage('삭제했습니다.'); loadList(); }
    });
    tr.appendChild(cell(del));
    body.appendChild(tr);
  });
  $('count').textContent = rows.length + '건';
  $('result-table').classList.toggle('hidden', rows.length === 0);
  $('empty').textContent = '아직 저장된 결과가 없습니다.';
  $('empty').classList.toggle('hidden', rows.length > 0);
}

// 선택된 이미지 파일 검증
function selectFile(file) {
  if (!file) return;
  if (!file.type.startsWith('image/')) { showMessage('이미지 파일만 올릴 수 있습니다.', true); return; }
  selectedFile = file;
  $('drop-text').textContent = file.name;
  showMessage('');
}

// 파일 선택으로 이미지 입력 구현
$('image-input').addEventListener('change', (e) => selectFile(e.target.files[0]));

// drag & drop 으로 이미지 입력 구현
const zone = $('drop-zone');
['dragenter', 'dragover'].forEach((ev) => zone.addEventListener(ev, (e) => {
  e.preventDefault();
  zone.classList.add('over');
}));
['dragleave', 'drop'].forEach((ev) => zone.addEventListener(ev, (e) => {
  e.preventDefault();
  zone.classList.remove('over');
}));
zone.addEventListener('drop', (e) => selectFile(e.dataTransfer.files[0]));
document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', (e) => e.preventDefault());


// ======== 이미지 업로드 + 추론 ==========

$('btn-upload').addEventListener('click', async () => {
  const file = selectedFile;
  if (!file) { showMessage('이미지 파일을 먼저 선택하세요.', true); return; }
  // 이미지 파일을 FormData로 보냄
  const form = new FormData();
  form.append('image', file);
  const btn = $('btn-upload');
  btn.disabled = true; // 분석하는 동안 중복 클릭 방지
  btn.textContent = '분석 중…';
  showMessage('');
  const r = await api(`${API_INF}/results/`, { method: 'POST', body: form });
  btn.disabled = false;
  btn.textContent = '분석하기';
  if (!r.ok) { showMessage(errorText(r, '추론 실패'), true); return; }

  const result = r.data;
  // saved : 서버가 세션의 user_id를 읽고 DB에 저장했는지 여부
  const saved = !!result.saved;
  currentId = saved ? result.id : null;
  $('result-image').src = result.image || URL.createObjectURL(file);
  const hasHeatmap = !!result.heatmap;
  $('result-heatmap').src = result.heatmap || '';
  $('result-heatmap').classList.toggle('hidden', !hasHeatmap);
  $('cam-control').classList.toggle('hidden', !hasHeatmap);
  fillBadge($('result-label'), result.malignant_prob);
  $('result-prob').textContent = toPercent(result.malignant_prob);
  $('save-ask').classList.toggle('hidden', !saved);
  $('guest-note').classList.toggle('hidden', saved);
  $('result-area').classList.remove('hidden');
  loadList();
});

// 슬라이더 값을 CSS에 전달하여 히트맵 이미지 alpha를 조정
$('cam-opacity').addEventListener('input', (e) => {
  document.documentElement.style.setProperty('--cam-opacity', e.target.value);
});

// 저장된 결과를 화면 목록에 추가하여 다시 렌더링
$('btn-save').addEventListener('click', () => {
  resetUpload();
  showMessage('결과를 저장했습니다.');
  loadList();
});

// 이미 저장된 결과를 서버에서 삭제
$('btn-discard').addEventListener('click', async () => {
  if (await deleteResult(currentId, false)) {
    resetUpload();
    showMessage('저장하지 않고 삭제했습니다.');
    loadList();
  }
});

// 로그아웃 -> 서버에서 세션을 지우고 로그인 페이지로 돌아감.
$('logout-btn').addEventListener('click', async () => {
  await postJson(`${API_USERS}/logout/`, {});
  location.href = 'index.html';
});

// 페이지 접속 시 로그인 상태를 확인하고 화면을 렌더링
(async function init() {
  currentUser = await getMe();
  renderAuth();
  await loadList();
})();
