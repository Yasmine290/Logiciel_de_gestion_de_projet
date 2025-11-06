// changer connexion / inscription
function switchAuth(type) {
    const tabs = document.querySelectorAll('.auth-tab');
    tabs.forEach(t => t.classList.remove('active'));
    if (type === 'login') {
      tabs[0].classList.add('active');
      document.getElementById('loginForm')?.classList.add('active');
      document.getElementById('registerForm')?.classList.remove('active');
    } else {
      tabs[1].classList.add('active');
      document.getElementById('registerForm')?.classList.add('active');
      document.getElementById('loginForm')?.classList.remove('active');
    }
  }
  
  // entrer dans l'app (fake) — pour la version multipage, on navigue
  function enterApp() {
    if (document.getElementById('app')) {
      // mode single-page (si jamais)
      document.getElementById('authScreen').style.display = 'none';
      document.getElementById('app').style.display = 'block';
      showPage('projects', document.querySelector('.top-nav button'));
    } else {
      // mode multi-pages
      location.href = 'projects.html';
    }
  }
  
  // navigation principale (utile si tu gardes des boutons)
  function showPage(page, btn) {
    document.querySelectorAll('.app-page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');
  
    document.querySelectorAll('.top-nav button').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
  }
  
  // modales
  function openModal(id) { const el = document.getElementById(id); if (el) el.style.display = 'flex'; }
  function closeModal(id) { const el = document.getElementById(id); if (el) el.style.display = 'none'; }
  
  // fermer modal en cliquant dehors
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.style.display = 'none'; });
  });
  

