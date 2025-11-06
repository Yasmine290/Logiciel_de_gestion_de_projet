// 🧭 Basculer entre "Connexion" et "Inscription"
function switchAuth(type) {
  const tabs = document.querySelectorAll('.auth-tab');
  tabs.forEach(t => t.classList.remove('active'));

  if (type === 'login') {
    tabs[0].classList.add('active');
    document.getElementById('loginForm').classList.add('active');
    document.getElementById('registerForm').classList.remove('active');
  } else {
    tabs[1].classList.add('active');
    document.getElementById('registerForm').classList.add('active');
    document.getElementById('loginForm').classList.remove('active');
  }
}

// 🔓 Simulation de connexion
function enterApp() {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('app').style.display = 'block';
}

// 📄 Navigation entre les pages (Projets / Gantt / Temps)
function showPage(page, btn) {
  document.querySelectorAll('.app-page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');

  document.querySelectorAll('.top-nav button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// 🪟 Ouvrir et fermer les modales
function openModal(id) {
  document.getElementById(id).style.display = 'flex';
}
function closeModal(id) {
  document.getElementById(id).style.display = 'none';
}

// 💡 Fermer la modale si on clique à l’extérieur
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.style.display = 'none';
  });
});
