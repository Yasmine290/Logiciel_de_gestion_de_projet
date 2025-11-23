// ===========================================================
// UTILITAIRES - Fonctions réutilisables
// ===========================================================

/**
 * Formate une date au format YYYY-MM-DD
 * @param {Date} date - La date à formater
 * @returns {string} Date formatée
 */
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Génère une couleur aléatoire en hexadécimal
 * @returns {string} Couleur hex (#RRGGBB)
 */
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

/**
 * Génère les initiales à partir d'un nom et prénom
 * @param {string} nom - Nom de famille
 * @param {string} prenom - Prénom
 * @returns {string} Initiales (ex: "JD")
 */
function getInitiales(nom, prenom) {
    const initialeNom = nom ? nom.charAt(0).toUpperCase() : '';
    const initialePrenom = prenom ? prenom.charAt(0).toUpperCase() : '';
    return initialePrenom + initialeNom;
}

/**
 * Ouvre un modal par son ID
 * @param {string} id - ID du modal à ouvrir
 */
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        // Ajouter l'animation d'apparition
        setTimeout(() => modal.style.opacity = '1', 10);
    }
}

/**
 * Ferme un modal par son ID
 * @param {string} id - ID du modal à fermer
 */
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.style.display = 'none', 300);
    }
}

/**
 * Calcule la progression d'un projet ou d'une tâche
 * @param {Object} item - Objet projet ou tâche
 * @returns {number} Pourcentage de progression (0-100)
 */
function calculerProgression(item) {
    // Si le statut est "Terminé", retourner 100%
    if (item.statutProjet === 'Terminé' || item.statutTache === 'Terminé') {
        return 100;
    }

    // Calcul basé sur les heures travaillées vs estimées
    const heuresTravaillees = parseFloat(item.heuresTravaillees) || 0;
    const heuresEstimees = parseFloat(item.heuresEstimees) || parseFloat(item.heuresAllouees) || 1;
    
    if (heuresEstimees > 0) {
        return Math.min(Math.round((heuresTravaillees / heuresEstimees) * 100), 100);
    }

    // Fallback sur le statut si pas d'heures
    if (item.statutProjet === 'En cours' || item.statutTache === 'En cours') {
        return 50;
    }
    
    return 0;
}

/**
 * Obtient la classe CSS pour la couleur de progression
 * @param {number} progression - Pourcentage de progression
 * @returns {string} Classe CSS
 */
function getProgressionColorClass(progression) {
    if (progression >= 100) return 'progress-complete';
    if (progression >= 75) return 'progress-high';
    if (progression >= 50) return 'progress-medium';
    if (progression >= 25) return 'progress-low';
    return 'progress-critical';
}

/**
 * Obtient la couleur pour la barre de progression
 * @param {number} progression - Pourcentage de progression
 * @returns {string} Couleur CSS
 */
function getProgressionColor(progression) {
    if (progression >= 100) return '#10b981'; // Vert
    if (progression >= 75) return '#84cc16'; // Vert clair
    if (progression >= 50) return '#eab308'; // Jaune
    if (progression >= 25) return '#f97316'; // Orange
    return '#ef4444'; // Rouge
}
