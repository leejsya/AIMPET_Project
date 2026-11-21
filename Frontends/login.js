
// 로그인 수행
// 입력받은 아이디와 비밀번호를 user_server로 보내짐.
// 로그인에 성공하면 서버가 Redis에 세션을 만들고 세션 쿠키를 할당함.
function doLogin() {
  return postJson(`${API_USERS}/login/`, {
    username: $('username').value,
    password: $('password').value,
  });
}

// 로그인 버튼
$('auth-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const r = await doLogin();
  if (r.ok) location.href = 'infer.html';
  else showMessage(errorText(r, '로그인 실패'), true);
});

// 회원가입 버튼
$('signup-btn').addEventListener('click', async () => {
  const r = await postJson(`${API_USERS}/signup/`, {
    username: $('username').value,
    password: $('password').value,
  });
  if (!r.ok) { showMessage(errorText(r, '회원가입 실패'), true); return; }
  // 회원가입에 성공하면 자동으로 로그인 됨.
  const lr = await doLogin();
  if (lr.ok) location.href = 'infer.html';
  else showMessage('가입했습니다. 로그인해 주세요.');
});

// 이미 로그인한 상태에서 이 페이지에 접속 시 바로 추론페이지로 이동됨.
getMe().then((user) => { if (user) location.href = 'infer.html'; });
