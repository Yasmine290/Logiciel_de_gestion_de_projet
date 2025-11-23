// ===========================================================
// DÉTAILS D'UN PROJET
// ===========================================================

/**
 * Affiche la page de détails d'un projet
 * @param {number} idProjet - ID du projet à afficher
 */
function afficherDetailsProjet(idProjet) {
    localStorage.setItem("selectedProjectId", idProjet);
    window.location.href = "/project_details";
}

/**
 * Charge et affiche les détails complets d'un projet
 */
function chargerDetailsProjet() {
    const container = document.getElementById("projectDetailsContainer");
    const idProjet = localStorage.getItem("selectedProjectId");
    if (!idProjet || !container) return;

    fetch(`${API_BASE}/projets/${idProjet}`)
        .then(res => res.json())
        .then(p => {
            chargerTaches(idProjet).then(taches => {
                // Calculer les statistiques du projet
                const tachesPrincipales = taches.filter(t => !t.idTacheParent);
                const totalTaches = tachesPrincipales.length;
                const tachesTerminees = tachesPrincipales.filter(t => t.statutTache === 'Terminée').length;
                const tachesEnCours = tachesPrincipales.filter(t => (t.statutTache === 'En cours' || t.statutTache === 'En révision')).length;
                
                let progression = calculerProgressionProjet(p, taches);
                
                // Mettre à jour les données du projet
                p.total = totalTaches;
                p.terminees = tachesTerminees;
                p.enCours = tachesEnCours;
                p.progression = progression;
                
                let vueKanban = false;
                
                /**
                 * Rend la vue Kanban des tâches
                 * @param {Array} taches - Liste des tâches
                 * @returns {string} HTML généré
                 */
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

                /**
                 * Rend la page complète des détails du projet
                 */
                function renderPage() {
                    const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
                    const canManage = userAccess.idRole === 1 || userAccess.idRole === 2;
                    
                    container.innerHTML = `
                        <div class="project-detail">
                            <button class="back-btn" onclick="window.location.href='/projects'">
                                <i class="fa-solid fa-arrow-left"></i> Retour aux projets
                            </button>

                            <div class="project-header-detail" style="position:relative;">
                                <div class="color-dot" style="background:${p.color || '#2563eb'};"></div>
                                <div style="flex:1;">
                                    <h2>${p.nomProjet}</h2>
                                    <p style="color:#6b7280; margin-bottom: 16px;">${p.descriptionProjet || 'Aucune description'}</p>
                                    
                                    <div style="display: flex; flex-direction: column; gap: 12px;">
                                        <!-- Dates du projet -->
                                        <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <i class="fa-solid fa-calendar-days" style="color: #3b82f6; font-size: 1rem;"></i>
                                                <span style="color: #374151; font-size: 0.95rem; font-weight: 500;">Début: ${p.dateDebut ? new Date(p.dateDebut).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' }) : 'Non défini'}</span>
                                            </div>
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <i class="fa-solid fa-calendar-check" style="color: #ef4444; font-size: 1rem;"></i>
                                                <span style="color: #374151; font-size: 0.95rem; font-weight: 500;">Échéance: ${p.dateFin ? new Date(p.dateFin).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' }) : 'Non défini'}</span>
                                            </div>
                                        </div>
                                        
                                        <!-- Membres assignés -->
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <div id="avatars-details-${p.idProjet}" style="display: flex; gap: 8px;">
                                                <!-- Les avatars seront chargés dynamiquement -->
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                ${canManage ? `
                                    <button class="edit-btn" onclick="modifierProjet(${p.idProjet})" style="position:absolute;top:0;right:0;">
                                        <i class="fa-solid fa-pen"></i>
                                    </button>
                                ` : ''}
                            </div>

                            <div class="stats-row">
                                <div class="stat-box">
                                    <i class="fa-solid fa-list-check"></i>
                                    <div class="stat-info">
                                        <span>Total des tâches</span>
                                        <strong>${p.total || 0}</strong>
                                    </div>
                                </div>
                                <div class="stat-box">
                                    <i class="fa-solid fa-check-circle"></i>
                                    <div class="stat-info">
                                        <span>Tâches terminées</span>
                                        <strong>${p.terminees || 0}</strong>
                                    </div>
                                </div>
                                <div class="stat-box">
                                    <i class="fa-solid fa-spinner"></i>
                                    <div class="stat-info">
                                        <span>Tâches en cours</span>
                                        <strong>${p.enCours || 0}</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="progress-section-detail">
                                <span>Progression du projet</span>
                                <div class="progress-bar-detail">
                                    <div class="progress-fill" style="width:${p.progression || 0}%;background:${getProgressionColor(p.progression || 0)};"></div>
                                </div>
                                <strong>${p.progression || 0}%</strong>
                            </div>

                            <div class="tasks-header">
                                <h3>Tâches du projet</h3>
                                <div style="display:flex;gap:12px;align-items:center;">
                                    <div class="view-toggle">
                                        <button class="toggle-btn ${!vueKanban ? 'active' : ''}" onclick="toggleView(false)">
                                            <i class="fa-solid fa-list"></i> Liste
                                        </button>
                                        <button class="toggle-btn ${vueKanban ? 'active' : ''}" onclick="toggleView(true)">
                                            <i class="fa-solid fa-table-columns"></i> Kanban
                                        </button>
                                    </div>
                                    ${canManage ? `
                                        <button class="btn-primary" id="btnAddTask" onclick="openTacheModal()" style="display:flex;align-items:center;gap:8px;">
                                            <i class="fa-solid fa-plus"></i> Nouvelle tâche
                                        </button>
                                    ` : ''}
                                </div>
                            </div>

                            <div id="tasksContainer">
                                ${vueKanban ? renderKanban(taches) : afficherTaches(taches)}
                            </div>
                        </div>
                    `;

                    // Charger les membres du projet
                    chargerMembresProjetDetails(idProjet);
                    
                    // Afficher les boutons "Marquer comme terminée"
                    afficherBoutonsMarquerTerminee(taches);
                    
                    // Ajouter les événements pour les sous-tâches
                    const sousTacheButtons = document.querySelectorAll('.btnSousTache');
                    sousTacheButtons.forEach(btn => {
                        btn.addEventListener('click', function() {
                            const parentId = parseInt(this.getAttribute('data-parent'));
                            openTacheModal(parentId);
                        });
                    });
                }

                /**
                 * Bascule entre la vue Liste et Kanban
                 * @param {boolean} kanban - True pour Kanban, false pour Liste
                 */
                window.toggleView = function(kanban) {
                    vueKanban = kanban;
                    const tasksContainer = document.getElementById('tasksContainer');
                    if (!tasksContainer) return;
                    
                    tasksContainer.innerHTML = vueKanban ? renderKanban(taches) : afficherTaches(taches);
                    
                    // Mettre à jour les boutons actifs
                    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
                    document.querySelectorAll('.toggle-btn')[kanban ? 1 : 0].classList.add('active');
                    
                    // Réafficher les boutons "Marquer comme terminée"
                    afficherBoutonsMarquerTerminee(taches);
                    
                    // Réattacher les événements des sous-tâches
                    const sousTacheButtons = document.querySelectorAll('.btnSousTache');
                    sousTacheButtons.forEach(btn => {
                        btn.addEventListener('click', function() {
                            const parentId = parseInt(this.getAttribute('data-parent'));
                            openTacheModal(parentId);
                        });
                    });
                };

                renderPage();
            });
        })
        .catch(err => console.error("Erreur chargement projet :", err));
}
