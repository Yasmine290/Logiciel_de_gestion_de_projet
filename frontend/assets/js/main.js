
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

// Fonction pour vérifier si l'utilisateur connecté est assigné à une tâche
async function estAssigneATache(idTache) {
  try {
    const response = await fetch(`${API_BASE}/taches/${idTache}/membres`);
    const membres = await response.json();
    const userConnecte = JSON.parse(sessionStorage.getItem('user') || '{}');
    return membres.some(m => m.idEmploye === userConnecte.idEmploye);
  } catch (err) {
    console.error('Erreur vérification assignation :', err);
    return false;
  }
}

// Fonction pour marquer une tâche comme terminée
async function marquerTacheTerminee(idTache) {
  try {
    const userConnecte = JSON.parse(sessionStorage.getItem('user') || '{}');
    const estAssigne = await estAssigneATache(idTache);
    
    if (!estAssigne) {
      alert('Vous devez être assigné à cette tâche pour la marquer comme terminée.');
      return;
    }

    // Récupérer d'abord les données complètes de la tâche
    const idProjet = localStorage.getItem("selectedProjectId");
    const tachesResponse = await fetch(`${API_BASE}/taches/${idProjet}`);
    const taches = await tachesResponse.json();
    const tache = taches.find(t => t.idTache === idTache);
    
    if (!tache) {
      alert('❌ Tâche introuvable.');
      return;
    }

    // Fonction pour convertir une date au format YYYY-MM-DD
    const formatDate = (dateString) => {
      if (!dateString) return null;
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return null;
      return date.toISOString().split('T')[0];
    };
    
    // Mettre à jour avec toutes les données + le nouveau statut
    const updateData = {
      titreTache: tache.titreTache || '',
      descriptionTache: tache.descriptionTache || '',
      statutTache: 'Terminée',
      prioriteTache: tache.prioriteTache || 'Moyenne',
      dateDebutTache: formatDate(tache.dateDebutTache),
      dateFinTache: formatDate(tache.dateFinTache),
      heuresEstimees: tache.heuresEstimees || 0
    };
    
    console.log('Données envoyées pour mise à jour:', updateData);
    
    const response = await fetch(`${API_BASE}/taches/${idTache}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });

    if (response.ok) {
      // Recharger la page pour afficher les changements
      window.location.reload();
    } else {
      const errorData = await response.json();
      console.error('Erreur serveur:', errorData);
      alert(`❌ Erreur lors de la mise à jour du statut: ${errorData.message || 'Erreur inconnue'}`);
    }
  } catch (err) {
    console.error('Erreur marquage tâche :', err);
    alert(`❌ Erreur lors de la mise à jour: ${err.message}`);
  }
}

// Fonction pour afficher les boutons "Marquer comme terminée" pour les tâches assignées
async function afficherBoutonsMarquerTerminee(taches) {
  const userConnecte = JSON.parse(sessionStorage.getItem('user') || '{}');
  
  for (const tache of taches) {
    const container = document.getElementById(`btn-terminer-container-${tache.idTache}`);
    if (!container) continue;
    
    // Ne pas afficher le bouton si la tâche est déjà terminée
    if (tache.statutTache === 'Terminée') continue;
    
    try {
      // Vérifier si l'utilisateur est assigné à cette tâche
      const estAssigne = await estAssigneATache(tache.idTache);
      
      if (estAssigne) {
        // Afficher le bouton "Marquer comme terminée" compact
        container.innerHTML = `
          <button 
            onclick="marquerTacheTerminee(${tache.idTache})" 
            title="Marquer comme terminée"
            style="background:#22c55e;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:600;cursor:pointer;font-size:0.9em;display:flex;align-items:center;gap:6px;white-space:nowrap;">
            <i class="fa-solid fa-check"></i> Terminée
          </button>
        `;
      }
    } catch (err) {
      console.error(`Erreur vérification assignation tâche ${tache.idTache}:`, err);
    }
  }
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
    // Vérifier le rôle de l'utilisateur pour masquer le bouton de sous-tâche si employé
    const userAccessCheck = JSON.parse(sessionStorage.getItem('user') || '{}');
    const isEmployeeCheck = userAccessCheck.idRole === 3;
    const canManageCheck = userAccessCheck.idRole === 1 || userAccessCheck.idRole === 2;
    const btnSousTacheHTML = isEmployeeCheck ? '' : `<button class="btn-secondary btnSousTache" data-parent="${t.idTache}" style="margin-left:8px; font-size:0.9em; padding:2px 8px;">Ajouter une Sous-tâche</button>`;
    
    html += `<div style="margin-left:${niveau * 24}px; border-left:${niveau ? '2px solid #e5e7eb' : 'none'}; padding-left:8px; margin-bottom:16px;">
      <div style="background:#fff;border-radius:12px;padding:18px 20px;margin-bottom:8px;box-shadow:0 1px 4px #0001;display:flex;flex-direction:column;gap:8px;position:relative;">
        <div style="display:flex;align-items:center;gap:10px;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-weight:600;font-size:1.1em;">${t.titreTache}</span>
            ${btnSousTacheHTML}
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <div id="btn-terminer-container-${t.idTache}"></div>
            ${canManageCheck ? `
              <div style="position:relative;">
                <button class="menu-btn-tache" onclick="event.stopPropagation(); toggleTacheMenu(${t.idTache})" style="background:transparent;border:none;color:#64748b;font-size:1.2rem;cursor:pointer;padding:4px 8px;border-radius:6px;">
                  <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
                <div class="menu-dropdown-tache" id="menu-tache-${t.idTache}" style="display:none;position:absolute;top:30px;right:0;background:white;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.1);padding:8px;min-width:150px;z-index:100;">
                  <button onclick="event.stopPropagation(); modifierTache(${t.idTache})" style="display:flex;align-items:center;gap:10px;width:100%;padding:10px 14px;border:none;background:transparent;color:#374151;font-size:0.95rem;font-weight:500;text-align:left;cursor:pointer;border-radius:8px;">
                    <i class="fa-solid fa-pen"></i> Modifier
                  </button>
                  <button onclick="event.stopPropagation(); supprimerTache(${t.idTache})" style="display:flex;align-items:center;gap:10px;width:100%;padding:10px 14px;border:none;background:transparent;color:#ef4444;font-size:0.95rem;font-weight:500;text-align:left;cursor:pointer;border-radius:8px;">
                    <i class="fa-solid fa-trash"></i> Supprimer
                  </button>
                </div>
              </div>
            ` : ''}
          </div>
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
  // Récupération des valeurs du formulaire de connexion
  const email = event.target.querySelector('input[type="email"]').value;
  const password = event.target.querySelector('input[type="password"]').value;

  if (email && password) {
    // Appel à l'API backend pour la connexion
    fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({courrielEmploye: email, motDePasse: password})
    })
      .then(res => res.json())
      .then(msg => {
        if (msg.user) {
          // Stockage des infos utilisateur en sessionStorage
          sessionStorage.setItem('user', JSON.stringify(msg.user));
          window.location.href = "/projects";
        } else {
          alert(msg.message || "Identifiants invalides");
        }
      })
      .catch(err => {
        alert('Erreur lors de la connexion');
        console.error(err);
      });
  } else {
    alert("Veuillez entrer un email et un mot de passe.");
  }
}

function handleRegister(event) {
  event.preventDefault();
  // Récupération des valeurs du formulaire d'inscription
  const nom = document.getElementById('nomRegister').value;
  const email = document.getElementById('emailRegister').value;
  const mdp = document.getElementById('mdpRegister').value;
  const role = document.getElementById('roleRegister').value;

  if (nom && email && mdp && role) {
    // Construction des données à envoyer au backend
    const data = {
      nomEmploye: nom,
      courrielEmploye: email,
      motDePasse: mdp,
      role: role
    };
    // Appel à l'API backend pour l'inscription
    fetch('http://127.0.0.1:5000/api/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(msg => {
        alert(msg.message);
        switchAuth('login');
      })
      .catch(err => {
        alert('Erreur lors de la création du compte');
        console.error(err);
      });
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

  // Retirer le bouton "Voir tous" s'il existe
  const projectsActions = document.getElementById('projects-actions');
  if (projectsActions) {
    const existingButton = projectsActions.querySelector('.btn-reset-filter');
    if (existingButton) existingButton.remove();
  }

  fetch(`${API_BASE}/projets`)
    .then(res => res.json())
    .then(data => {
      liste.innerHTML = '';

      // Compteurs pour dashboard basés sur les tâches
      let aFaire = 0, terminees = 0, enCours = 0, enRetard = 0;
      const now = new Date();
      
      // Pour chaque projet, charger ses tâches et analyser
      const promessesProjets = data.map(p => {
        return chargerTaches(p.idProjet).then(taches => {
          const projetAvecTaches = { ...p, taches };
          
          // Vérifier si le projet a des tâches en cours
          const aTachesEnCours = taches.some(t => t.statutTache === 'En cours');
          // Vérifier si toutes les tâches sont terminées
          const toutesTerminees = taches.length > 0 && taches.every(t => t.statutTache === 'Terminée');
          // Vérifier si des tâches sont en retard OU si le statut du projet est "En retard"
          const aTachesEnRetard = taches.some(t => 
            t.dateFinTache && new Date(t.dateFinTache) < now && t.statutTache !== 'Terminée'
          );
          const projetEnRetard = p.statutProjet === 'En retard' || aTachesEnRetard;
          
          // Classification du projet
          if (toutesTerminees || p.statutProjet === 'Terminé') {
            terminees++;
          } else if (projetEnRetard) {
            enRetard++;
          } else if (aTachesEnCours) {
            enCours++;
          } else {
            aFaire++;
          }
          
          return projetAvecTaches;
        });
      });

      // Attendre que tous les projets soient analysés
      Promise.all(promessesProjets).then((projetsAnalyses) => {
        // Met à jour les compteurs dans le dashboard
        const cards = document.querySelectorAll('.stats-cards .card');
        if (cards.length >= 4) {
          cards[0].querySelector('strong').textContent = aFaire;
          cards[1].querySelector('strong').textContent = terminees;
          cards[2].querySelector('strong').textContent = enCours;
          cards[3].querySelector('strong').textContent = enRetard;
          
          // Ajouter les événements de clic pour filtrer les projets
          cards[0].style.cursor = 'pointer';
          cards[1].style.cursor = 'pointer';
          cards[2].style.cursor = 'pointer';
          cards[3].style.cursor = 'pointer';
          
          cards[0].onclick = () => filtrerProjets('aFaire', projetsAnalyses);
          cards[1].onclick = () => filtrerProjets('termines', projetsAnalyses);
          cards[2].onclick = () => filtrerProjets('enCours', projetsAnalyses);
          cards[3].onclick = () => filtrerProjets('enRetard', projetsAnalyses);
        }
      });
      
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

      // Vérifier le rôle pour afficher le menu d'actions
      const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
      const canManage = userAccess.idRole === 1 || userAccess.idRole === 2; // Admin ou Gestionnaire

      // Pour chaque projet, calculer la progression basée sur les tâches
      const promessesCartes = data.map(p => {
        return chargerTaches(p.idProjet).then(taches => {
          const tachesPrincipales = taches.filter(t => !t.idTacheParent);
          const totalTaches = tachesPrincipales.length;
          const tachesTerminees = tachesPrincipales.filter(t => t.statutTache === 'Terminée').length;
          const progression = totalTaches > 0 ? Math.round((tachesTerminees / totalTaches) * 100) : 0;
          
          return { ...p, progression };
        });
      });

      Promise.all(promessesCartes).then((projetsAvecProgression) => {
        projetsAvecProgression.forEach(p => {
          // --- Création d'une carte de projet ---
          const card = document.createElement('div');
          card.className = 'project-card';
          card.style.position = 'relative';

          const color = p.color || getRandomColor();

          card.innerHTML = `
            <div class="project-header">
              <div class="color-dot" style="background:${color};"></div>
              <div class="project-info">
                <h3>${p.nomProjet}</h3>
                <p>${p.descriptionProjet || 'Aucune description'}</p>
              </div>
              ${canManage ? `
                <div class="project-menu">
                  <button class="menu-btn" onclick="event.stopPropagation(); toggleProjectMenu(${p.idProjet})">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                  </button>
                  <div class="menu-dropdown" id="menu-${p.idProjet}" style="display:none;">
                    <button onclick="event.stopPropagation(); supprimerProjet(${p.idProjet})" style="color:#ef4444;">
                      <i class="fa-solid fa-trash"></i> Supprimer
                    </button>
                  </div>
                </div>
              ` : ''}
            </div>

            <div class="progress-section">
              <div class="progress-bar">
                <div class="progress" style="width:${p.progression}%;"></div>
              </div>
              <span class="progress-text">${p.progression}%</span>
            </div>

          <div class="project-footer">
            <div class="date">
              <i class="fa-solid fa-calendar"></i>
              ${p.dateFin ? new Date(p.dateFin).toLocaleDateString('fr-CA') : 'Date inconnue'}
            </div>
            <div class="avatars" id="avatars-${p.idProjet}">
              <!-- Les avatars seront chargés dynamiquement -->
            </div>
          </div>
        `;

          liste.appendChild(card);

          // Charger les membres du projet
          chargerMembresProjet(p.idProjet);

          // ✅ Quand on clique sur une carte → page de détails
          card.addEventListener("click", () => afficherDetailsProjet(p.idProjet));
        });
      });
    })
    .catch(err => console.error("Erreur chargement projets :", err));
}

// --- Filtrer les projets par statut ---
function filtrerProjets(filtre, projetsAnalyses) {
  const liste = document.getElementById('liste-projets');
  if (!liste) return;
  
  liste.innerHTML = '';
  const now = new Date();
  const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
  const canManage = userAccess.idRole === 1 || userAccess.idRole === 2;
  
  // Déterminer le titre du filtre
  const titres = {
    'aFaire': 'Projets Actifs',
    'termines': 'Projets Terminés',
    'enCours': 'Projets En Cours',
    'enRetard': 'Projets En Retard'
  };
  
  // Afficher le bouton "Voir tous" au même niveau que "Nouveau Projet"
  const projectsActions = document.getElementById('projects-actions');
  if (projectsActions) {
    const existingButton = projectsActions.querySelector('.btn-reset-filter');
    if (existingButton) existingButton.remove();
    
    const resetButton = document.createElement('button');
    resetButton.className = 'btn-reset-filter';
    resetButton.onclick = () => chargerProjets();
    resetButton.style.cssText = 'background:#e5e7eb;color:#374151;border:none;padding:10px 20px;border-radius:10px;font-weight:600;cursor:pointer;';
    resetButton.innerHTML = '<i class="fa-solid fa-filter-circle-xmark"></i> Voir tous';
    projectsActions.appendChild(resetButton);
  }
  
  // Afficher le titre du filtre
  const header = document.createElement('h2');
  header.style.cssText = 'color:#0b0b20;font-size:1.5rem;font-weight:700;margin-bottom:20px;';
  header.textContent = titres[filtre];
  liste.appendChild(header);
  
  // Filtrer les projets
  fetch(`${API_BASE}/projets`)
    .then(res => res.json())
    .then(data => {
      const promessesFiltrees = data.map(p => {
        return chargerTaches(p.idProjet).then(taches => {
          const aTachesEnCours = taches.some(t => t.statutTache === 'En cours');
          const toutesTerminees = taches.length > 0 && taches.every(t => t.statutTache === 'Terminée');
          const aTachesEnRetard = taches.some(t => 
            t.dateFinTache && new Date(t.dateFinTache) < now && t.statutTache !== 'Terminée'
          );
          const projetEnRetard = p.statutProjet === 'En retard' || aTachesEnRetard;
          
          let categorie = '';
          if (toutesTerminees || p.statutProjet === 'Terminé') {
            categorie = 'termines';
          } else if (projetEnRetard) {
            categorie = 'enRetard';
          } else if (aTachesEnCours) {
            categorie = 'enCours';
          } else {
            categorie = 'aFaire';
          }
          
          return { projet: p, categorie };
        });
      });
      
      Promise.all(promessesFiltrees).then(resultats => {
        const projetsFiltres = resultats.filter(r => r.categorie === filtre);
        
        if (projetsFiltres.length === 0) {
          liste.innerHTML += `<p style="text-align:center;color:#9ca3af;padding:40px;">Aucun projet dans cette catégorie</p>`;
          return;
        }
        
        // Calculer la progression pour chaque projet filtré
        const promessesProgressions = projetsFiltres.map(({ projet: p }) => {
          return chargerTaches(p.idProjet).then(taches => {
            const tachesPrincipales = taches.filter(t => !t.idTacheParent);
            const totalTaches = tachesPrincipales.length;
            const tachesTerminees = tachesPrincipales.filter(t => t.statutTache === 'Terminée').length;
            const progression = totalTaches > 0 ? Math.round((tachesTerminees / totalTaches) * 100) : 0;
            return { ...p, progression };
          });
        });
        
        Promise.all(promessesProgressions).then(projetsAvecProgression => {
          projetsAvecProgression.forEach(p => {
            const card = document.createElement('div');
            card.className = 'project-card';
            card.style.position = 'relative';
            const color = p.color || getRandomColor();
            
            card.innerHTML = `
              <div class="project-header">
                <div class="color-dot" style="background:${color};"></div>
                <div class="project-info">
                  <h3>${p.nomProjet}</h3>
                  <p>${p.descriptionProjet || 'Aucune description'}</p>
                </div>
                ${canManage ? `
                  <div class="project-menu">
                    <button class="menu-btn" onclick="event.stopPropagation(); toggleProjectMenu(${p.idProjet})">
                      <i class="fa-solid fa-ellipsis-vertical"></i>
                    </button>
                    <div class="menu-dropdown" id="menu-${p.idProjet}" style="display:none;">
                      <button onclick="event.stopPropagation(); supprimerProjet(${p.idProjet})" style="color:#ef4444;">
                        <i class="fa-solid fa-trash"></i> Supprimer
                      </button>
                    </div>
                  </div>
                ` : ''}
              </div>
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress" style="width:${p.progression}%;"></div>
                </div>
                <span class="progress-text">${p.progression}%</span>
              </div>
            <div class="project-footer">
              <div class="date">
                <i class="fa-solid fa-calendar"></i>
                ${p.dateFin ? new Date(p.dateFin).toLocaleDateString('fr-CA') : 'Date inconnue'}
              </div>
              <div class="avatars" id="avatars-${p.idProjet}">
                <!-- Les avatars seront chargés dynamiquement -->
              </div>
            </div>
          `;
          
            liste.appendChild(card);
            chargerMembresProjet(p.idProjet);
            card.addEventListener("click", () => afficherDetailsProjet(p.idProjet));
          });
        });
      });
    })
    .catch(err => console.error("Erreur filtrage projets :", err));
}

// --- Génère une couleur aléatoire pour les projets ---
function getRandomColor() {
  const colors = ['#2563eb', '#8b5cf6', '#22c55e', '#fb923c', '#ec4899', '#3b82f6', '#14b8a6'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// --- Charger et afficher les membres d'un projet ---
function chargerMembresProjet(idProjet) {
  const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
  if (!avatarsContainer) return;

  // Charger les membres ASSIGNÉS au projet depuis la base de données
  fetch(`${API_BASE}/projets/${idProjet}/membres`)
    .then(res => res.json())
    .then(membres => {
      avatarsContainer.innerHTML = '';
      
      if (membres.length === 0) {
        avatarsContainer.innerHTML = '<span style="color:#9ca3af;font-size:0.85rem;">Aucun membre</span>';
        return;
      }
      
      const maxDisplay = 3;
      const toDisplay = membres.slice(0, maxDisplay);
      
      // Afficher les avatars avec les initiales des membres assignés
      toDisplay.forEach(emp => {
        const initiales = getInitiales(emp.nomEmploye, emp.prenomEmploye);
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = initiales;
        avatar.title = `${emp.prenomEmploye || ''} ${emp.nomEmploye}`;
        avatarsContainer.appendChild(avatar);
      });
      
      // Afficher "+X" s'il y a plus de membres
      const remaining = membres.length - toDisplay.length;
      if (remaining > 0) {
        const moreAvatar = document.createElement('div');
        moreAvatar.className = 'avatar more';
        moreAvatar.textContent = `+${remaining}`;
        moreAvatar.title = `${remaining} autre(s) membre(s)`;
        avatarsContainer.appendChild(moreAvatar);
      }
    })
    .catch(err => console.error('Erreur chargement membres projet:', err));
}

// --- Fonction utilitaire pour obtenir les initiales ---
function getInitiales(nom, prenom) {
  const initialeNom = nom ? nom.charAt(0).toUpperCase() : '';
  const initialePrenom = prenom ? prenom.charAt(0).toUpperCase() : '';
  return initialePrenom + initialeNom;
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
    .then(result => {
      // Récupérer les membres sélectionnés
      const membresCheckboxes = document.querySelectorAll('#membresEquipe input[type="checkbox"]:checked');
      const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
      
      // Si des membres ont été sélectionnés et qu'on a un idProjet, les assigner
      if (membresIds.length > 0 && result.idProjet) {
        fetch(`${API_BASE}/projets/${result.idProjet}/membres`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ membres: membresIds })
        })
          .then(() => {
            alert(result.message);
            closeModal('modalProjet');
            chargerProjets();
          })
          .catch(err => console.error('Erreur assignation membres:', err));
      } else {
        alert(result.message);
        closeModal('modalProjet');
        chargerProjets();
      }
    })
    .catch(err => {
      console.error('Erreur lors de l’ajout du projet:', err);
      alert("Erreur lors de l'ajout du projet");
    });
}

// --- Afficher/masquer le menu d'actions d'un projet ---
function toggleProjectMenu(idProjet) {
  const menu = document.getElementById(`menu-${idProjet}`);
  if (!menu) return;
  
  // Fermer tous les autres menus
  document.querySelectorAll('.menu-dropdown').forEach(m => {
    if (m.id !== `menu-${idProjet}`) m.style.display = 'none';
  });
  
  // Toggle le menu actuel
  menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

// Fermer les menus si on clique ailleurs
document.addEventListener('click', (e) => {
  if (!e.target.closest('.project-menu')) {
    document.querySelectorAll('.menu-dropdown').forEach(m => m.style.display = 'none');
  }
});

// --- Modifier un projet ---
function modifierProjet(idProjet) {
  // Récupérer les données du projet depuis l'API
  fetch(`${API_BASE}/projets/${idProjet}`)
    .then(res => res.json())
    .then(projet => {
      // Pré-remplir le formulaire de modification
      document.getElementById('modifIdProjet').value = projet.idProjet;
      document.getElementById('modifNomProjet').value = projet.nomProjet;
      document.getElementById('modifDescProjet').value = projet.descriptionProjet || '';
      document.getElementById('modifDateDebut').value = projet.dateDebut ? projet.dateDebut.split('T')[0] : '';
      document.getElementById('modifDateFin').value = projet.dateFin ? projet.dateFin.split('T')[0] : '';
      document.getElementById('modifStatutProjet').value = projet.statutProjet || 'À faire';
      
      // Charger les membres assignés au projet depuis la BD
      fetch(`${API_BASE}/projets/${idProjet}/membres`)
        .then(res => res.json())
        .then(membres => {
          const membresIds = membres.map(m => m.idEmploye);
          chargerMembresEquipe(membresIds);
        })
        .catch(err => {
          console.error('Erreur chargement membres:', err);
          chargerMembresEquipe([]);
        });
      
      // Ouvrir la modale de modification
      openModal('modalModifierProjet');
    })
    .catch(err => {
      console.error('Erreur lors du chargement du projet:', err);
      alert('Erreur lors du chargement des données du projet');
    });
}

// --- Enregistrer les modifications d'un projet ---
function enregistrerModificationProjet(event) {
  event.preventDefault();
  
  const idProjet = document.getElementById('modifIdProjet').value;
  
  // Récupérer les membres sélectionnés
  const membresCheckboxes = document.querySelectorAll('#modifMembresEquipe input[type="checkbox"]:checked');
  const membresSelectionnes = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
  
  const data = {
    nomProjet: document.getElementById('modifNomProjet').value,
    descriptionProjet: document.getElementById('modifDescProjet').value,
    dateDebut: document.getElementById('modifDateDebut').value,
    dateFin: document.getElementById('modifDateFin').value,
    statutProjet: document.getElementById('modifStatutProjet').value,
    membres: membresSelectionnes
  };

  fetch(`${API_BASE}/projets/${idProjet}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(result => {
      // Sauvegarder les membres assignés
      return fetch(`${API_BASE}/projets/${idProjet}/membres`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ membres: membresSelectionnes })
      });
    })
    .then(() => {
      alert('Projet modifié avec succès');
      closeModal('modalModifierProjet');
      
      // Recharger la page appropriée
      if (document.getElementById('liste-projets')) {
        chargerProjets();
      } else if (document.getElementById('projectDetailsContainer')) {
        chargerDetailsProjet();
      }
    })
    .catch(err => {
      console.error('Erreur lors de la modification:', err);
      alert('Erreur lors de la modification du projet');
    });
}

// --- Supprimer un projet ---
let projetASupprimer = null;

function supprimerProjet(idProjet) {
  // Fermer tous les menus déroulants avant d'ouvrir la modale
  document.querySelectorAll('.menu-dropdown').forEach(m => m.style.display = 'none');
  
  projetASupprimer = idProjet;
  document.getElementById('confirmationMessage').textContent = 'Êtes-vous sûr de vouloir supprimer ce projet ?';
  openModal('modalConfirmation');
  
  // Attacher l'événement au bouton de confirmation
  const btnConfirmer = document.getElementById('btnConfirmerSuppression');
  btnConfirmer.onclick = confirmerSuppression;
}

function confirmerSuppression() {
  if (!projetASupprimer) return;
  
  fetch(`${API_BASE}/projets/${projetASupprimer}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(msg => {
      closeModal('modalConfirmation');
      projetASupprimer = null;
      chargerProjets();
    })
    .catch(err => {
      console.error('Erreur lors de la suppression:', err);
      alert('Erreur lors de la suppression du projet');
      closeModal('modalConfirmation');
      projetASupprimer = null;
    });
}

function annulerSuppression() {
  projetASupprimer = null;
  closeModal('modalConfirmation');
}

// --- Charger les membres de l'équipe depuis la base de données ---
function chargerMembresEquipe(membresSelectionnes = []) {
  fetch(`${API_BASE}/employes`)
    .then(res => res.json())
    .then(employes => {
      // Pour la modale de projet (création)
      const membresEquipeDiv = document.getElementById('membresEquipe');
      if (membresEquipeDiv) {
        membresEquipeDiv.innerHTML = '';
        employes.forEach(emp => {
          const label = document.createElement('label');
          label.innerHTML = `<input type="checkbox" value="${emp.idEmploye}"> ${emp.nomEmploye} <small>(${emp.nomRole || 'Employé'})</small>`;
          membresEquipeDiv.appendChild(label);
        });
      }

      // Pour la modale de modification de projet
      const modifMembresEquipeDiv = document.getElementById('modifMembresEquipe');
      if (modifMembresEquipeDiv) {
        modifMembresEquipeDiv.innerHTML = '';
        employes.forEach(emp => {
          const label = document.createElement('label');
          const isChecked = membresSelectionnes.includes(emp.idEmploye) ? 'checked' : '';
          label.innerHTML = `<input type="checkbox" value="${emp.idEmploye}" ${isChecked}> ${emp.nomEmploye} <small>(${emp.nomRole || 'Employé'})</small>`;
          modifMembresEquipeDiv.appendChild(label);
        });
      }

      // Pour la modale de tâche
      const assigneTacheDiv = document.getElementById('assigneTache');
      if (assigneTacheDiv) {
        assigneTacheDiv.innerHTML = '';
        employes.forEach(emp => {
          const label = document.createElement('label');
          label.innerHTML = `<input type="checkbox" value="${emp.idEmploye}"> ${emp.nomEmploye} <small>(${emp.courrielEmploye})</small>`;
          assigneTacheDiv.appendChild(label);
        });
      }
    })
    .catch(err => console.error('Erreur chargement membres:', err));
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
  if (modal) {
    modal.classList.remove('hidden');
    // Charger les membres de l'équipe lors de l'ouverture de la modale
    if (id === 'modalProjet' || id === 'modalTache') {
      chargerMembresEquipe();
    }
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
}


// ===========================================================
// 7️⃣ Initialisation
// ===========================================================
document.addEventListener('DOMContentLoaded', () => {
  // Contrôle d'accès selon le rôle de l'utilisateur
  const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
  console.log('User access info:', userAccess); // Debug
  
  // Vérifier si l'utilisateur est employé (idRole === 3)
  const isEmployee = userAccess.idRole === 3;
  console.log('Is employee:', isEmployee); // Debug

  if (isEmployee) {
    console.log('Masquage des boutons pour employé'); // Debug
    
    // Masquer le bouton de création de projet
    const btnAddProject = document.getElementById('btnAddProject');
    if (btnAddProject) {
      btnAddProject.style.display = 'none';
      console.log('Bouton Nouveau Projet masqué'); // Debug
    }

    // Masquer le bouton de création de tâche
    const btnAddTask = document.getElementById('btnAddTask');
    if (btnAddTask) {
      btnAddTask.style.display = 'none';
      console.log('Bouton Nouvelle Tâche masqué'); // Debug
    }

    // Désactiver la soumission du formulaire de projet
    const btnSubmitProject = document.getElementById('btnSubmitProject');
    if (btnSubmitProject) {
      btnSubmitProject.disabled = true;
      btnSubmitProject.title = "Seuls les gestionnaires et admins peuvent créer des projets.";
    }
    const formProjet = document.getElementById('formProjet');
    if (formProjet) {
      formProjet.addEventListener('submit', function(e) {
        e.preventDefault();
        alert("Seuls les gestionnaires et admins peuvent créer des projets.");
      });
    }

    // Désactiver la soumission du formulaire de tâche
    const formTache = document.getElementById('formTache');
    if (formTache) {
      formTache.addEventListener('submit', function(e) {
        e.preventDefault();
        alert("Seuls les gestionnaires et admins peuvent créer des tâches.");
      });
    }
  }
  // Ajout de la logique de déconnexion
  const btnLogout = document.getElementById('btnLogout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      sessionStorage.removeItem('user');
      window.location.href = '/login';
    });
  }
  if (document.getElementById('loginForm')) {
    switchAuth('login');
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
  }

  // Affichage dynamique de l'utilisateur connecté dans le header
  const user = sessionStorage.getItem('user');
  if (user) {
    const userObj = JSON.parse(user);
    // Recherche du header (profil à droite)
    const profileDiv = document.querySelector('.profile');
    if (profileDiv) {
      // Mise à jour du nom et du rôle
      const avatar = profileDiv.querySelector('.avatar');
      if (avatar && userObj.nomEmploye) avatar.textContent = userObj.nomEmploye[0].toUpperCase();
      const nameSpan = profileDiv.querySelector('span');
      if (nameSpan && userObj.nomEmploye) nameSpan.textContent = userObj.nomEmploye;
      const small = profileDiv.querySelector('small');
      if (small && userObj.idRole) {
        let roleTxt = 'Employé';
        if (userObj.idRole === 1) roleTxt = 'Admin';
        else if (userObj.idRole === 2) roleTxt = 'Gestionnaire';
        small.textContent = roleTxt;
      }
    }
  }

  if (document.getElementById('liste-projets')) {
    chargerProjets();
    chargerMembresEquipe(); // Charger les membres pour la modale de projet
    const formProjet = document.getElementById('formProjet');
    if (formProjet) formProjet.addEventListener('submit', ajouterProjet);
    
    // Formulaire de modification de projet
    const formModifierProjet = document.getElementById('formModifierProjet');
    if (formModifierProjet) formModifierProjet.addEventListener('submit', enregistrerModificationProjet);
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

  // Chargement des détails du projet si sur la page correspondante
  if (window.location.pathname.includes("project_details")) {
    chargerDetailsProjet();
    
    // Formulaire de modification de projet (dans la page de détails)
    const formModifierProjet = document.getElementById('formModifierProjet');
    if (formModifierProjet) formModifierProjet.addEventListener('submit', enregistrerModificationProjet);
    
    // Formulaire de modification de tâche
    const formModifierTache = document.getElementById('formModifierTache');
    if (formModifierTache) formModifierTache.addEventListener('submit', enregistrerModificationTache);
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
        // Calculer la progression basée sur les tâches
        const totalTaches = taches.filter(t => !t.idTacheParent).length;
        const tachesTerminees = taches.filter(t => !t.idTacheParent && t.statutTache === 'Terminée').length;
        const tachesEnCours = taches.filter(t => !t.idTacheParent && (t.statutTache === 'En cours' || t.statutTache === 'En révision')).length;
        const progression = totalTaches > 0 ? Math.round((tachesTerminees / totalTaches) * 100) : 0;
        
        // Mettre à jour les données du projet avec les vraies valeurs
        p.total = totalTaches;
        p.terminees = tachesTerminees;
        p.enCours = tachesEnCours;
        p.progression = progression;
        
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
                  <div style="background:#fff;border-radius:8px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px #0001;display:flex;flex-direction:column;gap:8px;position:relative;">
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;">
                      <div style="font-weight:600;font-size:1.05em;flex:1;">${t.titreTache}</div>
                      <div id="btn-terminer-container-${t.idTache}"></div>
                    </div>
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

              <div class="project-header-detail" style="position:relative;">
                <div class="color-dot" style="background:${p.color || '#2563eb'};"></div>
                <div style="flex:1;">
                  <h2>${p.nomProjet}</h2>
                  <p>${p.descriptionProjet || ''}</p>
                  <div class="avatars">
                    <div class="avatar">AD</div>
                    <span class="date"><i class="fa-solid fa-calendar"></i> Échéance: ${new Date(p.dateFin).toLocaleDateString('fr-CA')}</span>
                  </div>
                </div>
                <button class="btn-modifier-projet" id="btnModifierProjet" style="position:absolute;top:0;right:0;background:#f3f4f6;border:none;padding:10px 18px;border-radius:10px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:8px;color:#374151;">
                  <i class="fa-solid fa-gear"></i> Modifier le projet
                </button>
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
          
          // Contrôle d'accès pour les boutons de tâches et modification
          const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
          const isEmployee = userAccess.idRole === 3;
          const canManage = userAccess.idRole === 1 || userAccess.idRole === 2;
          
          // Bouton Modifier le projet
          const btnModifierProjet = document.getElementById('btnModifierProjet');
          if (btnModifierProjet) {
            if (!canManage) {
              btnModifierProjet.style.display = 'none';
            } else {
              btnModifierProjet.addEventListener('click', () => modifierProjet(idProjet));
            }
          }
          
          // Ajout des eventListeners sur les boutons dynamiques
          const btnNouvelleTache = document.getElementById('btnNouvelleTache');
          if (btnNouvelleTache) {
            if (isEmployee) {
              btnNouvelleTache.style.display = 'none';
            } else {
              btnNouvelleTache.addEventListener('click', () => openTacheModal());
            }
          }
          
          const btnPremiereTache = document.getElementById('btnPremiereTache');
          if (btnPremiereTache) {
            if (isEmployee) {
              btnPremiereTache.style.display = 'none';
            } else {
              btnPremiereTache.addEventListener('click', () => openTacheModal());
            }
          }
          
          document.querySelectorAll('.btnSousTache').forEach(btn => {
            btn.addEventListener('click', function() {
              const parentId = this.getAttribute('data-parent');
              openTacheModal(parentId);
            });
          });
          
          // Afficher les boutons "Marquer comme terminée" pour les utilisateurs assignés
          afficherBoutonsMarquerTerminee(taches);
          
          // Fermer les menus de tâches si on clique ailleurs
          document.addEventListener('click', (e) => {
            if (!e.target.closest('.menu-btn-tache') && !e.target.closest('.menu-dropdown-tache')) {
              document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
            }
          });
          // Switch vue
          const btnVueListe = document.getElementById('btnVueListe');
          const btnVueKanban = document.getElementById('btnVueKanban');
          if (btnVueListe) btnVueListe.addEventListener('click', () => { 
            vueKanban = false; 
            renderPage(); 
            setTimeout(() => afficherBoutonsMarquerTerminee(taches), 100);
          });
          if (btnVueKanban) btnVueKanban.addEventListener('click', () => { 
            vueKanban = true; 
            renderPage(); 
            setTimeout(() => afficherBoutonsMarquerTerminee(taches), 100);
          });
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
  chargerMembresEquipe(); // Charger les membres lors de l'ouverture
  openModal('modalTache');
}

// --- Afficher/masquer le menu d'actions d'une tâche ---
function toggleTacheMenu(idTache) {
  const menu = document.getElementById(`menu-tache-${idTache}`);
  if (!menu) return;
  
  // Fermer tous les autres menus
  document.querySelectorAll('.menu-dropdown-tache').forEach(m => {
    if (m.id !== `menu-tache-${idTache}`) m.style.display = 'none';
  });
  
  // Toggle le menu actuel
  menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

// --- Modifier une tâche ---
function modifierTache(idTache) {
  // Fermer les menus
  document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
  
  // Récupérer les données de la tâche depuis l'API
  const idProjet = localStorage.getItem("selectedProjectId");
  fetch(`${API_BASE}/taches/${idProjet}`)
    .then(res => res.json())
    .then(taches => {
      const tache = taches.find(t => t.idTache === idTache);
      if (!tache) {
        alert('Tâche introuvable');
        return;
      }
      
      // Pré-remplir le formulaire de modification
      document.getElementById('modifIdTache').value = tache.idTache;
      document.getElementById('modifTitreTache').value = tache.titreTache;
      document.getElementById('modifDescTache').value = tache.descriptionTache || '';
      document.getElementById('modifStatutTache').value = tache.statutTache || 'À faire';
      document.getElementById('modifPrioriteTache').value = tache.prioriteTache || 'Moyenne';
      document.getElementById('modifDateDebutTache').value = tache.dateDebutTache ? tache.dateDebutTache.split('T')[0] : '';
      document.getElementById('modifDateFinTache').value = tache.dateFinTache ? tache.dateFinTache.split('T')[0] : '';
      document.getElementById('modifHeuresTache').value = tache.heuresEstimees || '';
      
      // Charger les membres assignés à la tâche depuis la BD
      fetch(`${API_BASE}/taches/${idTache}/membres`)
        .then(res => res.json())
        .then(membres => {
          const membresIds = membres.map(m => m.idEmploye);
          chargerMembresEquipeTache(membresIds);
        })
        .catch(err => {
          console.error('Erreur chargement membres tâche:', err);
          chargerMembresEquipeTache([]);
        });
      
      // Ouvrir la modale de modification
      openModal('modalModifierTache');
    })
    .catch(err => {
      console.error('Erreur lors du chargement de la tâche:', err);
      alert('Erreur lors du chargement des données de la tâche');
    });
}

// --- Charger les membres pour la modale de modification de tâche ---
function chargerMembresEquipeTache(membresSelectionnes = []) {
  fetch(`${API_BASE}/employes`)
    .then(res => res.json())
    .then(employes => {
      const modifAssigneTacheDiv = document.getElementById('modifAssigneTache');
      if (modifAssigneTacheDiv) {
        modifAssigneTacheDiv.innerHTML = '';
        employes.forEach(emp => {
          const label = document.createElement('label');
          const isChecked = membresSelectionnes.includes(emp.idEmploye) ? 'checked' : '';
          label.innerHTML = `<input type="checkbox" value="${emp.idEmploye}" ${isChecked}> ${emp.nomEmploye} <small>(${emp.courrielEmploye})</small>`;
          modifAssigneTacheDiv.appendChild(label);
        });
      }
    })
    .catch(err => console.error('Erreur chargement membres:', err));
}

// --- Enregistrer les modifications d'une tâche ---
function enregistrerModificationTache(event) {
  event.preventDefault();
  
  const idTache = document.getElementById('modifIdTache').value;
  const data = {
    titreTache: document.getElementById('modifTitreTache').value,
    descriptionTache: document.getElementById('modifDescTache').value,
    statutTache: document.getElementById('modifStatutTache').value,
    prioriteTache: document.getElementById('modifPrioriteTache').value,
    dateDebutTache: document.getElementById('modifDateDebutTache').value,
    dateFinTache: document.getElementById('modifDateFinTache').value,
    heuresEstimees: document.getElementById('modifHeuresTache').value
  };

  fetch(`${API_BASE}/taches/${idTache}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(result => {
      // Récupérer les membres sélectionnés
      const membresCheckboxes = document.querySelectorAll('#modifAssigneTache input[type="checkbox"]:checked');
      const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
      
      // Sauvegarder les membres assignés
      return fetch(`${API_BASE}/taches/${idTache}/membres`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ membres: membresIds })
      });
    })
    .then(() => {
      alert('Tâche modifiée avec succès');
      closeModal('modalModifierTache');
      chargerDetailsProjet(); // Recharger les tâches
    })
    .catch(err => {
      console.error('Erreur lors de la modification:', err);
      alert('Erreur lors de la modification de la tâche');
    });
}

// --- Supprimer une tâche ---
let tacheASupprimer = null;

function supprimerTache(idTache) {
  // Fermer tous les menus déroulants avant d'ouvrir la modale
  document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
  
  tacheASupprimer = idTache;
  document.getElementById('confirmationMessage').textContent = 'Êtes-vous sûr de vouloir supprimer cette tâche ?';
  openModal('modalConfirmation');
  
  // Attacher l'événement au bouton de confirmation
  const btnConfirmer = document.getElementById('btnConfirmerSuppression');
  btnConfirmer.onclick = confirmerSuppressionTache;
}

function confirmerSuppressionTache() {
  if (!tacheASupprimer) return;
  
  fetch(`${API_BASE}/taches/${tacheASupprimer}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(msg => {
      closeModal('modalConfirmation');
      tacheASupprimer = null;
      chargerDetailsProjet(); // Recharger les tâches
    })
    .catch(err => {
      console.error('Erreur lors de la suppression:', err);
      alert('Erreur lors de la suppression de la tâche');
      closeModal('modalConfirmation');
      tacheASupprimer = null;
    });
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
    .then(result => {
      // Récupérer les membres sélectionnés
      const membresCheckboxes = document.querySelectorAll('#assigneTache input[type="checkbox"]:checked');
      const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
      
      // Si des membres ont été sélectionnés et qu'on a un idTache, les assigner
      if (membresIds.length > 0 && result.idTache) {
        fetch(`${API_BASE}/taches/${result.idTache}/membres`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ membres: membresIds })
        })
          .then(() => {
            alert(result.message);
            closeModal('modalTache');
            tacheParentId = null;
            chargerDetailsProjet();
          })
          .catch(err => console.error('Erreur assignation membres tâche:', err));
      } else {
        alert(result.message);
        closeModal('modalTache');
        tacheParentId = null;
        chargerDetailsProjet();
      }
    })
    .catch(err => console.error('Erreur ajout tâche:', err));
}

document.addEventListener('DOMContentLoaded', () => {
  const formTache = document.getElementById('formTache');
  if (formTache) formTache.addEventListener('submit', ajouterTache);
});
