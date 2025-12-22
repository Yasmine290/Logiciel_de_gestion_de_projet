// ===========================================================
// GESTION DES PROJETS
// ===========================================================

/**
 * Charge et affiche tous les projets
 */
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
                        <button class="btn-primary" onclick="openModalNouveauProjet()">
                            <i class="fa-solid fa-plus"></i> Créer mon premier projet
                        </button>
                    </div>`;
                return;
            }

            // Vérifier le rôle pour afficher le menu d'actions
            const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
            const canManage = userAccess.idRole === 1 || userAccess.idRole === 2; // Admin ou Gestionnaire

            // Utiliser la progression calculée par le backend (déjà récursive)
            data.forEach(p => {
                // Récupérer la progression depuis le backend
                p.progression = Math.round(parseFloat(p.progressionProjet) || 0);
                
                const card = creerCarteProjet(p, canManage);
                liste.appendChild(card);
                chargerMembresProjet(p.idProjet);
                card.addEventListener("click", () => afficherDetailsProjet(p.idProjet));
            });
        })
        .catch(err => console.error("Erreur chargement projets :", err));
}

/**
 * Crée une carte visuelle pour un projet
 * @param {Object} p - Objet projet
 * @param {boolean} canManage - Indique si l'utilisateur peut gérer le projet
 * @returns {HTMLElement} Élément DOM de la carte
 */
function creerCarteProjet(p, canManage) {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.style.position = 'relative';

    // Utiliser une couleur cohérente basée sur l'ID du projet
    const color = p.color || getProjectColor(p.idProjet);

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

    return card;
}

/**
 * Filtre les projets par statut
 * @param {string} filtre - Type de filtre ('aFaire', 'termines', 'enCours', 'enRetard')
 * @param {Array} projetsAnalyses - Liste des projets déjà analysés
 */
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
    
    // Afficher le bouton "Voir tous"
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
                
                // Utiliser la progression calculée par le backend (déjà récursive)
                projetsFiltres.forEach(({ projet: p }) => {
                    // Récupérer la progression depuis le backend
                    p.progression = Math.round(parseFloat(p.progressionProjet) || 0);
                    
                    const card = creerCarteProjet(p, canManage);
                    liste.appendChild(card);
                    chargerMembresProjet(p.idProjet);
                    card.addEventListener("click", () => afficherDetailsProjet(p.idProjet));
                });
            });
        })
        .catch(err => console.error("Erreur filtrage projets :", err));
}

/**
 * Charge et affiche les membres d'un projet
 * @param {number} idProjet - ID du projet
 */
function chargerMembresProjet(idProjet) {
    const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
    if (!avatarsContainer) return;

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
            
            // Afficher les avatars
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

/**
 * Charge et affiche les membres dans la page de détails
 * @param {number} idProjet - ID du projet
 */
function chargerMembresProjetDetails(idProjet) {
    const avatarsContainer = document.getElementById(`avatars-details-${idProjet}`);
    if (!avatarsContainer) return;

    fetch(`${API_BASE}/projets/${idProjet}/membres`)
        .then(res => res.json())
        .then(membres => {
            avatarsContainer.innerHTML = '';
            
            if (membres.length === 0) {
                avatarsContainer.innerHTML = '<span style="color:#9ca3af;font-size:0.9rem;">Aucun membre assigné</span>';
                return;
            }
            
            // Afficher tous les membres
            membres.forEach(emp => {
                const initiales = getInitiales(emp.nomEmploye, emp.prenomEmploye);
                const avatar = document.createElement('div');
                avatar.className = 'avatar';
                avatar.textContent = initiales;
                avatar.title = `${emp.prenomEmploye || ''} ${emp.nomEmploye}`;
                avatar.style.cssText = 'width: 40px; height: 40px; background: #3b82f6; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.95rem; cursor: default;';
                avatarsContainer.appendChild(avatar);
            });
        })
        .catch(err => console.error('Erreur chargement membres projet détails:', err));
}

/**
 * Ouvre la modale de création d'un nouveau projet avec tous les champs vides
 */
function openModalNouveauProjet() {
    // Réinitialiser tous les champs du formulaire
    document.getElementById('nomProjet').value = '';
    document.getElementById('descProjet').value = '';
    document.getElementById('dateDebut').value = '';
    document.getElementById('dateFin').value = '';
    document.getElementById('statutProjet').value = 'À faire';
    
    // Décocher toutes les cases des membres
    const checkboxes = document.querySelectorAll('#membresEquipe input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
    
    // Ouvrir la modale
    openModal('modalProjet');
}

/**
 * Ajoute un nouveau projet
 * @param {Event} event - Événement de soumission du formulaire
 */
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
        
        // Si des membres ont été sélectionnés
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
        console.error('Erreur lors de l\'ajout du projet:', err);
        alert("Erreur lors de l'ajout du projet");
    });
}

/**
 * Affiche/masque le menu d'actions d'un projet
 * @param {number} idProjet - ID du projet
 */
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

/**
 * Modifie un projet existant
 * @param {number} idProjet - ID du projet à modifier
 */
function modifierProjet(idProjet) {
    fetch(`${API_BASE}/projets/${idProjet}`)
        .then(res => res.json())
        .then(projet => {
            // Pré-remplir le formulaire
            document.getElementById('modifIdProjet').value = projet.idProjet;
            document.getElementById('modifNomProjet').value = projet.nomProjet;
            document.getElementById('modifDescProjet').value = projet.descriptionProjet || '';
            document.getElementById('modifDateDebut').value = projet.dateDebut ? projet.dateDebut.split('T')[0] : '';
            document.getElementById('modifDateFin').value = projet.dateFin ? projet.dateFin.split('T')[0] : '';
            document.getElementById('modifStatutProjet').value = projet.statutProjet || 'À faire';
            
            // Charger les membres assignés
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
            
            openModal('modalModifierProjet');
        })
        .catch(err => {
            console.error('Erreur lors du chargement du projet:', err);
            alert('Erreur lors du chargement des données du projet');
        });
}

/**
 * Enregistre les modifications d'un projet
 * @param {Event} event - Événement de soumission du formulaire
 */
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

// Variable globale pour stocker le projet à supprimer
let projetASupprimer = null;

/**
 * Demande confirmation avant suppression
 * @param {number} idProjet - ID du projet à supprimer
 */
function supprimerProjet(idProjet) {
    // Fermer tous les menus déroulants
    document.querySelectorAll('.menu-dropdown').forEach(m => m.style.display = 'none');
    
    console.log('supprimerProjet appelé avec idProjet:', idProjet, 'type:', typeof idProjet);
    projetASupprimer = idProjet;
    document.getElementById('confirmationMessage').textContent = 'Êtes-vous sûr de vouloir supprimer ce projet ?';
    openModal('modalConfirmation');
    
    // Attacher l'événement au bouton de confirmation
    const btnConfirmer = document.getElementById('btnConfirmerSuppression');
    btnConfirmer.onclick = confirmerSuppression;
}

/**
 * Confirme et exécute la suppression du projet
 */
function confirmerSuppression() {
    if (!projetASupprimer) return;
    
    console.log('confirmerSuppression - projetASupprimer:', projetASupprimer, 'type:', typeof projetASupprimer);
    console.log('URL complète:', `${API_BASE}/projets/${projetASupprimer}`);
    
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

/**
 * Annule la suppression d'un projet
 */
function annulerSuppression() {
    projetASupprimer = null;
    closeModal('modalConfirmation');
}

/**
 * Charge les membres de l'équipe depuis la base de données
 * @param {Array} membresSelectionnes - Liste des IDs des membres déjà sélectionnés
 */
function chargerMembresEquipe(membresSelectionnes = []) {
    fetch(`${API_BASE}/employes`)
        .then(res => res.json())
        .then(employes => {
            // Pour la modale de création de projet
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
                    const isChecked = membresSelectionnes.includes(emp.idEmploye) ? 'checked' : '';
                    const label = document.createElement('label');
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

// Fermer les menus si on clique ailleurs
document.addEventListener('click', (e) => {
    if (!e.target.closest('.project-menu')) {
        document.querySelectorAll('.menu-dropdown').forEach(m => m.style.display = 'none');
    }
});
