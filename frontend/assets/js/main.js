
// Fonction pour charger les tâches d'un projet via l'API
// idProjet : identifiant du projet dont on veut les tâches
function chargerTaches(idProjet) {
  // Appel à l'API backend pour récupérer les tâches du projet
  return fetch(`${API_BASE}/taches/${idProjet}`)
    .then(res => res.json())
    .catch(err => {
      // Affiche une erreur en cas de problème de chargement
      console.error('Erreur chargement tâches :', err);
      return [];
    });
}


// Fonction pour afficher les tâches d'un projet sous forme de liste
// taches : tableau de toutes les tâches du projet
// parentId : identifiant de la tâche parent (pour l'imbrication)
// niveau : niveau d'imbrication (pour l'affichage visuel)
function afficherTaches(taches, parentId = null, niveau = 0) {
  let html = '';
  // Filtre les tâches pour ne garder que celles du niveau courant
  taches.filter(t => t.idTacheParent === parentId).forEach(t => {
    // Détermination de la couleur du badge selon le statut
    let statutColor = '#e5e7eb', statutText = t.statutTache;
    if (statutText === 'À faire') statutColor = '#e5e7eb';
    else if (statutText === 'En cours') statutColor = '#facc15';
    else if (statutText === 'En révision') statutColor = '#38bdf8';
    else if (statutText === 'Terminée') statutColor = '#22c55e';

    // Détermination de la couleur du badge selon la priorité
    let prioColor = '#e5e7eb', prioText = t.prioriteTache;
    if (prioText === 'Haute') prioColor = '#ef4444';
    else if (prioText === 'Moyenne') prioColor = '#f59e42';
    else if (prioText === 'Basse') prioColor = '#22d3ee';

    // Construction du HTML pour chaque tâche
    html += `<div style="margin-left:${niveau * 24}px; border-left:${niveau ? '2px solid #e5e7eb' : 'none'}; padding-left:8px; margin-bottom:16px;">
      <div style="background:#fff;border-radius:12px;padding:18px 20px;margin-bottom:8px;box-shadow:0 1px 4px #0001;display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-weight:600;font-size:1.1em;">${t.titreTache}</span>
          <button class="btn-secondary btnSousTache" data-parent="${t.idTache}" style="margin-left:8px; font-size:0.9em; padding:2px 8px;">Ajouter une Sous-tâche</button>
        </div>
        <div style="font-size:0.98em; color:#555; margin-bottom:4px;">${t.descriptionTache || ''}</div>
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
          <span style="background:${statutColor};color:#222;padding:3px 12px;border-radius:8px;font-size:0.95em;font-weight:500;">${statutText}</span>
          <span style="background:${prioColor};color:#fff;padding:3px 12px;border-radius:8px;font-size:0.95em;font-weight:500;">${prioText}</span>
          <span style="color:#555;font-size:0.95em;">${t.heuresEstimees || 0}h estimées</span>
          <span style="color:#555;font-size:0.95em;">${t.dateDebutTache ? new Date(t.dateDebutTache).toLocaleDateString('fr-CA') : ''}</span>
          <span style="color:#555;font-size:0.95em;">${t.dateFinTache ? new Date(t.dateFinTache).toLocaleDateString('fr-CA') : ''}</span>
        </div>
      </div>
      ${afficherTaches(taches, t.idTache, niveau + 1)}
    </div>`;
  });
  return html;
}
// ===========================================================
// main.js — Frontend (connexion, inscription, projets, temps)
// ===========================================================

const API_BASE = "http://127.0.0.1:5000/api"; // backend local Flask


// ===========================================================
// 1️⃣ Vérification de la connexion au backend
// ===========================================================
fetch(`${API_BASE}/test`)
  .then(res => res.json())
  .then(data => console.log("✅ Backend connecté :", data.message))
  .catch(err => console.error("❌ Erreur de connexion :", err));


// ===========================================================
// 2️⃣ Gestion Connexion / Inscription avec effet fluide
// ===========================================================
function switchAuth(mode) {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const btnLogin = document.getElementById('btnLogin');
  const btnRegister = document.getElementById('btnRegister');

  if (!loginForm || !registerForm) return;

  // Animation de transition fluide
  loginForm.style.opacity = "0";
  registerForm.style.opacity = "0";

  setTimeout(() => {
    if (mode === 'login') {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');

      btnLogin.classList.add('active');
      btnRegister.classList.remove('active');
    } else {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');

      btnRegister.classList.add('active');
      btnLogin.classList.remove('active');
    }

    // Réapparition fluide
    setTimeout(() => {
      if (mode === 'login') loginForm.style.opacity = "1";
      else registerForm.style.opacity = "1";
    }, 100);
  }, 150);
}


// ===========================================================
// 3️⃣ Simulation Connexion / Inscription
// ===========================================================
// --- Connexion sans popup ---
function handleLogin(event) {
  event.preventDefault();

  const email = event.target.querySelector('input[type="email"]').value;
  const password = event.target.querySelector('input[type="password"]').value;

  if (email && password) {
    console.log("✅ Connexion réussie");
    window.location.href = "/projects";
  } else {
    alert("Veuillez entrer un email et un mot de passe.");
  }
}

function handleRegister(event) {
  event.preventDefault();
  const nom = event.target.querySelector('input[type="text"]').value;
  const email = event.target.querySelectorAll('input[type="email"]')[1].value;
  const mdp = event.target.querySelectorAll('input[type="password"]')[1].value;

  if (nom && email && mdp) {
    alert("Compte créé avec succès ✅");
    switchAuth('login');
  } else {
    alert("Veuillez remplir tous les champs.");
  }
}


// ===========================================================
// 4️⃣ Gestion des PROJETS (projects.html)
// ===========================================================
function chargerProjets() {
  const liste = document.getElementById('liste-projets');
  if (!liste) return;

  fetch(`${API_BASE}/projets`)
    .then(res => res.json())
    .then(data => {
      liste.innerHTML = '';

      // Compteurs pour dashboard
      let aFaire = 0, terminees = 0, enCours = 0, enRetard = 0;
      const now = new Date();
      data.forEach(p => {
        // Projet à faire : statut "À faire"
        if (p.statutProjet === 'À faire') aFaire++;
        // Projet en cours : statut "En cours"
        if (p.statutProjet === 'En cours') enCours++;
        // Projet terminé : statut "Terminé" ou progression 100%
        if (p.statutProjet === 'Terminé' || p.progression === 100) terminees++;
        // Projet en retard : dateFin dépassée et non terminé
        if (p.dateFin && new Date(p.dateFin) < now && p.statutProjet !== 'Terminé') enRetard++;
      });

      // Met à jour les compteurs dans le dashboard
      const cards = document.querySelectorAll('.stats-cards .card');
      if (cards.length >= 4) {
        cards[0].querySelector('strong').textContent = aFaire;
        cards[1].querySelector('strong').textContent = terminees;
        cards[2].querySelector('strong').textContent = enCours;
        cards[3].querySelector('strong').textContent = enRetard;
      }

      if (data.length === 0) {
        liste.innerHTML = `
          <div class="no-project">
            <i class="fa-solid fa-clipboard-list icon"></i>
            <p>Aucun projet pour le moment</p>
            <button class="btn-primary" onclick="openModal('modalProjet')">
              <i class="fa-solid fa-plus"></i> Créer mon premier projet
            </button>
          </div>`;
        return;
      }

      data.forEach(p => {
        // --- Création d'une carte de projet ---
        const card = document.createElement('div');
        card.className = 'project-card';

        const color = p.color || getRandomColor();

        card.innerHTML = `
          <div class="project-header">
            <div class="color-dot" style="background:${color};"></div>
            <div class="project-info">
              <h3>${p.nomProjet}</h3>
              <p>${p.descriptionProjet || 'Aucune description'}</p>
            </div>
          </div>

          <div class="progress-section">
            <div class="progress-bar">
              <div class="progress" style="width:${p.progression || 0}%;"></div>
            </div>
            <span class="progress-text">${p.progression || 0}%</span>
          </div>

          <div class="project-footer">
            <div class="date">
              <i class="fa-solid fa-calendar"></i>
              ${p.dateFin ? new Date(p.dateFin).toLocaleDateString('fr-CA') : 'Date inconnue'}
            </div>
            <div class="avatars">
              <div class="avatar">G</div>
              <div class="avatar">AC</div>
              <div class="avatar">BM</div>
              <div class="avatar more">+1</div>
            </div>
          </div>
        `;

        liste.appendChild(card);

        // ✅ Quand on clique sur une carte → page de détails
        card.addEventListener("click", () => afficherDetailsProjet(p.idProjet));
      });
    })
    .catch(err => console.error("Erreur chargement projets :", err));
}

// --- Génère une couleur aléatoire pour les projets ---
function getRandomColor() {
  const colors = ['#2563eb', '#8b5cf6', '#22c55e', '#fb923c', '#ec4899', '#3b82f6', '#14b8a6'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// --- Ajouter un nouveau projet ---
function ajouterProjet(event) {
  event.preventDefault();

  const data = {
    nomProjet: document.getElementById('nomProjet').value,
    descriptionProjet: document.getElementById('descProjet').value,
    dateDebut: document.getElementById('dateDebut').value,
    dateFin: document.getElementById('dateFin').value,
    heuresBudget: 0,
    coutsProjet: 0,
    idClient: null,
    idEmploye: 2,
    idTemplateProjet: 1,
    statutProjet: document.getElementById('statutProjet').value
  };

  fetch(`${API_BASE}/projets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(msg => {
      alert(msg.message);
      closeModal('modalProjet');
      chargerProjets();
    })
    .catch(err => {
      console.error('Erreur lors de l’ajout du projet:', err);
      alert("Erreur lors de l'ajout du projet");
    });
}


// ===========================================================
// 5️⃣ Gestion du TEMPS (time.html)
// ===========================================================
function chargerTemps() {
  const liste = document.getElementById('liste-temps');
  if (!liste) return;

  fetch(`${API_BASE}/temps`)
    .then(res => res.json())
    .then(data => {
      liste.innerHTML = '';
      data.forEach(t => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fa-solid fa-clock"></i> ${t.date} — <strong>${t.projet}</strong> : ${t.heures}h (${t.commentaire})`;
        liste.appendChild(li);
      });
    })
    .catch(err => console.error("Erreur chargement temps :", err));
}

function ajouterTemps(event) {
  event.preventDefault();

  const data = {
    projet_id: document.getElementById('projet_id').value,
    date: document.getElementById('date').value,
    heures: document.getElementById('heures').value,
    commentaire: document.getElementById('commentaire').value
  };

  fetch(`${API_BASE}/temps`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(msg => {
      alert(msg.message);
      event.target.reset();
      chargerTemps();
    })
    .catch(err => console.error("Erreur ajout temps :", err));
}


// ===========================================================
// 6️⃣ Utilitaires
// ===========================================================
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('hidden');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
}


// ===========================================================
// 7️⃣ Initialisation
// ===========================================================
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('loginForm')) {
    switchAuth('login');
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
  }

  if (document.getElementById('liste-projets')) {
    chargerProjets();
    const formProjet = document.getElementById('formProjet');
    if (formProjet) formProjet.addEventListener('submit', ajouterProjet);
  }

  if (document.getElementById('liste-temps')) {
    chargerTemps();
    const formTemps = document.getElementById('form-temps');
    if (formTemps) formTemps.addEventListener('submit', ajouterTemps);
  }

  const colorSwatches = document.querySelectorAll(".color-swatch");
  colorSwatches.forEach((swatch) => {
    swatch.addEventListener("click", () => {
      colorSwatches.forEach(s => s.classList.remove("selected"));
      swatch.classList.add("selected");
    });
  });

  // ✅ Si on est sur la page des détails du projet, on charge les infos
  if (window.location.pathname.includes("project_details")) {
    chargerDetailsProjet();
  }
});


// ===========================================================
// 🔎 8️⃣ Page de détails du projet (project_details.html)
// ===========================================================
function afficherDetailsProjet(idProjet) {
  localStorage.setItem("selectedProjectId", idProjet);
  window.location.href = "/project_details";
}

function chargerDetailsProjet() {
  const container = document.getElementById("projectDetailsContainer");
  const idProjet = localStorage.getItem("selectedProjectId");
  if (!idProjet || !container) return;

  fetch(`${API_BASE}/projets/${idProjet}`)
    .then(res => res.json())
    .then(p => {
      chargerTaches(idProjet).then(taches => {
        let vueKanban = false;
        function renderKanban(taches) {
          const statuts = [
            {key: 'Actif', color: '#e5e7eb'},
            {key: 'En attente', color: '#fef9c3'},
            {key: 'En cours', color: '#dbeafe'},
            {key: 'En révision', color: '#fee2b3'},
            {key: 'Terminée', color: '#bbf7d0'}
          ];
          return `<div class="kanban-container" style="display:flex;gap:16px;flex-wrap:nowrap;overflow-x:auto;">${
            statuts.map(statut => {
              // Mapping : 'À faire' => 'En attente'
              const tachesCol = taches.filter(t => {
                if (statut.key === 'En attente') return (t.statutTache === 'En attente' || t.statutTache === 'À faire') && !t.idTacheParent;
                return t.statutTache === statut.key && !t.idTacheParent;
              });
              return `<div class="kanban-col" style="flex:0 0 220px;background:${statut.color};border-radius:10px;padding:10px;min-width:220px;max-width:220px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                  <span style="font-weight:600;color:#222;">${statut.key}</span>
                  <span style="background:#fff;color:#222;padding:2px 10px;border-radius:8px;font-size:0.95em;">${tachesCol.length}</span>
                </div>
                ${tachesCol.length === 0 ? `<div style="color:#aaa;text-align:center;">Aucune tâche</div>` : tachesCol.map(t => `
                  <div style="background:#fff;border-radius:8px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px #0001;display:flex;flex-direction:column;gap:8px;">
                    <div style="font-weight:600;font-size:1.05em;">${t.titreTache}</div>
                    <div style="font-size:0.98em;color:#555;">${t.descriptionTache || ''}</div>
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:4px;">
                      ${t.prioriteTache ? `<span style="background:${t.prioriteTache==='Haute'?'#ef4444':t.prioriteTache==='Moyenne'?'#f59e42':'#22d3ee'};color:#fff;padding:3px 12px;border-radius:8px;font-size:0.95em;font-weight:500;">${t.prioriteTache}</span>` : ''}
                      ${t.dateFinTache ? `<span style="color:#555;font-size:0.95em;"><i class="fa-regular fa-calendar"></i> ${new Date(t.dateFinTache).toLocaleDateString('fr-CA')}</span>` : ''}
                    </div>
                  </div>
                `).join('')}
              </div>`;
            }).join('')
          }</div>`;
        }

        function renderPage() {
          container.innerHTML = `
            <div class="project-detail">
              <button class="back-btn" onclick="window.location.href='/projects'">
                <i class="fa-solid fa-arrow-left"></i> Retour aux projets
              </button>

              <div class="project-header-detail">
                <div class="color-dot" style="background:${p.color || '#2563eb'};"></div>
                <div>
                  <h2>${p.nomProjet}</h2>
                  <p>${p.descriptionProjet || ''}</p>
                  <div class="avatars">
                    <div class="avatar">G</div>
                    <div class="avatar">AC</div>
                    <div class="avatar">BM</div>
                    <div class="avatar more">+1</div>
                    <span class="date"><i class="fa-solid fa-calendar"></i> Échéance: ${new Date(p.dateFin).toLocaleDateString('fr-CA')}</span>
                  </div>
                </div>
              </div>

              <div class="progress-section">
                <span>Progression globale</span>
                <div class="progress-bar"><div class="progress" style="width:${p.progression || 0}%;"></div></div>
                <p class="progress-stats">${p.terminees || 0} terminées · ${p.enCours || 0} en cours · ${p.total || 0} total</p>
              </div>

              <div class="tasks-header">
                <h3>Tâches</h3>
                <div class="task-controls">
                  <button class="btn-primary" id="btnNouvelleTache"><i class="fa-solid fa-plus"></i> Nouvelle Tâche</button>
                  <div class="view-switch">
                    <button id="btnVueListe" class="${!vueKanban ? 'active' : ''}">Liste</button>
                    <button id="btnVueKanban" class="${vueKanban ? 'active' : ''}">Kanban</button>
                  </div>
                </div>
              </div>

              <div id="listeTaches">
                ${vueKanban
                  ? renderKanban(taches)
                  : (taches.length === 0 ? `<div class="no-task"><i class="fa-solid fa-square-check"></i><p>Aucune tâche pour le moment</p><small>Créez votre première tâche en cliquant sur “Nouvelle Tâche” ci-dessus.</small><br><button class="btn-primary" id="btnPremiereTache"><i class="fa-solid fa-plus"></i> Créer ma première tâche</button></div>` : afficherTaches(taches))}
              </div>
            </div>
          `;
          // Ajout des eventListeners sur les boutons dynamiques
          const btnNouvelleTache = document.getElementById('btnNouvelleTache');
          if (btnNouvelleTache) btnNouvelleTache.addEventListener('click', () => openTacheModal());
          const btnPremiereTache = document.getElementById('btnPremiereTache');
          if (btnPremiereTache) btnPremiereTache.addEventListener('click', () => openTacheModal());
          document.querySelectorAll('.btnSousTache').forEach(btn => {
            btn.addEventListener('click', function() {
              const parentId = this.getAttribute('data-parent');
              openTacheModal(parentId);
            });
          });
          // Switch vue
          const btnVueListe = document.getElementById('btnVueListe');
          const btnVueKanban = document.getElementById('btnVueKanban');
          if (btnVueListe) btnVueListe.addEventListener('click', () => { vueKanban = false; renderPage(); });
          if (btnVueKanban) btnVueKanban.addEventListener('click', () => { vueKanban = true; renderPage(); });
        }
        renderPage();
      });
    })
    .catch(err => console.error("Erreur chargement projet :", err));
}


// ===========================================================
// 🧱 GESTION DES TÂCHES (project_details.html)
// ===========================================================
let tacheParentId = null;
function openTacheModal(parentId = null) {
  tacheParentId = parentId;
  openModal('modalTache');
}

function ajouterTache(event) {
  event.preventDefault();
  const idProjet = localStorage.getItem("selectedProjectId");

  let statut = document.getElementById('statutTache').value;
  const statutsValid = ['À faire', 'En cours', 'En révision', 'Terminée'];
  if (!statutsValid.includes(statut)) statut = 'À faire';
  let priorite = document.getElementById('prioriteTache').value;
  const prioritesValid = ['Basse', 'Moyenne', 'Haute'];
  if (!prioritesValid.includes(priorite)) priorite = 'Moyenne';
  const data = {
    idProjet,
    idTacheParent: tacheParentId,
    titreTache: document.getElementById('titreTache').value,
    descriptionTache: document.getElementById('descTache').value,
    statutTache: statut,
    prioriteTache: priorite,
    dateDebutTache: document.getElementById('dateDebutTache').value,
    dateFinTache: document.getElementById('dateFinTache').value,
    heuresEstimees: document.getElementById('heuresTache').value
  };

  fetch(`${API_BASE}/taches`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(msg => {
      alert(msg.message);
  closeModal('modalTache');
  tacheParentId = null;
  chargerDetailsProjet();
    })
    .catch(err => console.error('Erreur ajout tâche:', err));
}

document.addEventListener('DOMContentLoaded', () => {
  const formTache = document.getElementById('formTache');
  if (formTache) formTache.addEventListener('submit', ajouterTache);
});
