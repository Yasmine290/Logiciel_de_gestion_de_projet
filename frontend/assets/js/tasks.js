// ===========================================================
// GESTION DES TÂCHES
// ===========================================================

// Variable globale pour stocker le parent ID lors de la création de sous-tâches
let tacheParentId = null;

// Variable globale pour stocker la tâche à supprimer
let tacheASupprimer = null;

/**
 * Charge les tâches d'un projet via l'API
 * @param {number} idProjet - ID du projet
 * @returns {Promise<Array>} Liste des tâches
 */
function chargerTaches(idProjet) {
    return fetch(`${API_BASE}/taches/${idProjet}`)
        .then(res => res.json())
        .catch(err => {
            console.error('Erreur chargement tâches :', err);
            return [];
        });
}

/**
 * Vérifie si l'utilisateur connecté est assigné à une tâche
 * @param {number} idTache - ID de la tâche
 * @returns {Promise<boolean>} True si assigné
 */
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

/**
 * Marque une tâche comme terminée (réservé aux membres assignés)
 * @param {number} idTache - ID de la tâche
 */
async function marquerTacheTerminee(idTache) {
    try {
        const userConnecte = JSON.parse(sessionStorage.getItem('user') || '{}');
        const isAdminOrGestionnaire = userConnecte.idRole === 1 || userConnecte.idRole === 2;
        const isEmploye = userConnecte.idRole === 3;
        
        // Vérification des permissions : Admin/Gestionnaire peuvent tout faire, Employé doit être assigné
        if (isEmploye) {
            const estAssigne = await estAssigneATache(idTache);
            if (!estAssigne) {
                alert('Vous devez être assigné à cette tâche pour la marquer comme terminée.');
                return;
            }
        }

        // Récupérer les données complètes de la tâche
        const idProjet = localStorage.getItem("selectedProjectId");
        const tachesResponse = await fetch(`${API_BASE}/taches/${idProjet}`);
        const taches = await tachesResponse.json();
        const tache = taches.find(t => t.idTache === idTache);
        
        if (!tache) {
            alert('❌ Tâche introuvable.');
            return;
        }

        // Fonction pour convertir une date au format YYYY-MM-DD
        const formatDateFn = (dateString) => {
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
            dateDebutTache: formatDateFn(tache.dateDebutTache),
            dateFinTache: formatDateFn(tache.dateFinTache),
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

/**
 * Affiche les boutons "Marquer comme terminée" pour les tâches
 * Admin et Gestionnaire : peuvent marquer TOUTES les tâches comme terminées
 * Employé : peut marquer comme terminée UNIQUEMENT les tâches qui lui sont assignées
 * @param {Array} taches - Liste des tâches
 */
async function afficherBoutonsMarquerTerminee(taches) {
    const userConnecte = JSON.parse(sessionStorage.getItem('user') || '{}');
    const isAdminOrGestionnaire = userConnecte.idRole === 1 || userConnecte.idRole === 2; // 1 = Admin, 2 = Gestionnaire
    const isEmploye = userConnecte.idRole === 3; // 3 = Employé
    
    for (const tache of taches) {
        const container = document.getElementById(`btn-terminer-container-${tache.idTache}`);
        if (!container) continue;
        
        // Ne pas afficher le bouton si la tâche est déjà terminée
        if (tache.statutTache === 'Terminée') continue;
        
        let afficherBouton = false;
        
        // Admin et Gestionnaire : toujours afficher le bouton
        if (isAdminOrGestionnaire) {
            afficherBouton = true;
        }
        // Employé : vérifier s'il est assigné
        else if (isEmploye) {
            try {
                const estAssigne = await estAssigneATache(tache.idTache);
                afficherBouton = estAssigne;
            } catch (err) {
                console.error(`Erreur vérification assignation tâche ${tache.idTache}:`, err);
                afficherBouton = false;
            }
        }
        
        if (afficherBouton) {
            container.innerHTML = `
                <button 
                    onclick="marquerTacheTerminee(${tache.idTache})" 
                    title="Marquer comme terminée"
                    style="background:#22c55e;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:600;cursor:pointer;font-size:0.9em;display:flex;align-items:center;gap:6px;white-space:nowrap;">
                    <i class="fa-solid fa-check"></i> Terminée
                </button>
            `;
        }
    }
}

/**
 * Affiche les tâches sous forme de liste avec hiérarchie
 * @param {Array} taches - Liste des tâches
 * @param {number|null} parentId - ID de la tâche parent
 * @param {number} niveau - Niveau d'imbrication
 * @returns {string} HTML généré
 */
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

        // Vérifier les permissions utilisateur
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

/**
 * Ouvre la modale pour ajouter une tâche
 * @param {number|null} parentId - ID de la tâche parent (pour sous-tâches)
 */
function openTacheModal(parentId = null) {
    tacheParentId = parentId;
    
    // Réinitialiser tous les champs du formulaire de création
    document.getElementById('titreTache').value = '';
    document.getElementById('descTache').value = '';
    document.getElementById('statutTache').value = 'À faire';
    document.getElementById('prioriteTache').value = 'Moyenne';
    document.getElementById('dateDebutTache').value = '';
    document.getElementById('dateFinTache').value = '';
    document.getElementById('heuresTache').value = '';
    
    // Décocher toutes les cases des membres
    const checkboxes = document.querySelectorAll('#assigneTache input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
    
    // Charger les membres disponibles
    chargerMembresEquipe();
    openModal('modalTache');
}

/**
 * Affiche/masque le menu d'actions d'une tâche
 * @param {number} idTache - ID de la tâche
 */
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

/**
 * Modifie une tâche existante
 * @param {number} idTache - ID de la tâche à modifier
 */
function modifierTache(idTache) {
    // Fermer les menus
    document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
    
    const idProjet = localStorage.getItem("selectedProjectId");
    fetch(`${API_BASE}/taches/${idProjet}`)
        .then(res => res.json())
        .then(taches => {
            const tache = taches.find(t => t.idTache === idTache);
            if (!tache) {
                alert('Tâche introuvable');
                return;
            }
            
            // Pré-remplir le formulaire
            document.getElementById('modifIdTache').value = tache.idTache;
            document.getElementById('modifTitreTache').value = tache.titreTache;
            document.getElementById('modifDescTache').value = tache.descriptionTache || '';
            document.getElementById('modifStatutTache').value = tache.statutTache || 'À faire';
            document.getElementById('modifPrioriteTache').value = tache.prioriteTache || 'Moyenne';
            document.getElementById('modifDateDebutTache').value = tache.dateDebutTache ? tache.dateDebutTache.split('T')[0] : '';
            document.getElementById('modifDateFinTache').value = tache.dateFinTache ? tache.dateFinTache.split('T')[0] : '';
            document.getElementById('modifHeuresTache').value = tache.heuresEstimees || '';
            
            // Charger les membres assignés
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
            
            openModal('modalModifierTache');
        })
        .catch(err => {
            console.error('Erreur lors du chargement de la tâche:', err);
            alert('Erreur lors du chargement des données de la tâche');
        });
}

/**
 * Charge les membres pour la modale de modification de tâche
 * @param {Array} membresSelectionnes - Liste des IDs des membres sélectionnés
 */
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

/**
 * Enregistre les modifications d'une tâche
 * @param {Event} event - Événement de soumission du formulaire
 */
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
        chargerDetailsProjet();
    })
    .catch(err => {
        console.error('Erreur lors de la modification:', err);
        alert('Erreur lors de la modification de la tâche');
    });
}

/**
 * Demande confirmation avant suppression
 * @param {number} idTache - ID de la tâche à supprimer
 */
function supprimerTache(idTache) {
    // Fermer tous les menus déroulants
    document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
    
    tacheASupprimer = idTache;
    document.getElementById('confirmationMessage').textContent = 'Êtes-vous sûr de vouloir supprimer cette tâche ?';
    openModal('modalConfirmation');
    
    const btnConfirmer = document.getElementById('btnConfirmerSuppression');
    btnConfirmer.onclick = confirmerSuppressionTache;
}

/**
 * Confirme et exécute la suppression de la tâche
 */
function confirmerSuppressionTache() {
    if (!tacheASupprimer) return;
    
    fetch(`${API_BASE}/taches/${tacheASupprimer}`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(msg => {
        closeModal('modalConfirmation');
        tacheASupprimer = null;
        chargerDetailsProjet();
    })
    .catch(err => {
        console.error('Erreur lors de la suppression:', err);
        alert('Erreur lors de la suppression de la tâche');
        closeModal('modalConfirmation');
        tacheASupprimer = null;
    });
}

/**
 * Ajoute une nouvelle tâche
 * @param {Event} event - Événement de soumission du formulaire
 */
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
        
        // Si des membres ont été sélectionnés
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

// Fermer les menus si on clique ailleurs
document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-btn-tache')) {
        document.querySelectorAll('.menu-dropdown-tache').forEach(m => m.style.display = 'none');
    }
});
