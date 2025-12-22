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
 * Génère une couleur cohérente basée sur un ID (pour éviter les changements aléatoires)
 * @param {number} id - ID du projet/élément
 * @returns {string} Couleur hex (#RRGGBB)
 */
function getProjectColor(id) {
    // Palette de couleurs prédéfinies professionnelles
    const colors = [
        '#3b82f6', // Bleu
        '#8b5cf6', // Violet
        '#ec4899', // Rose
        '#f59e0b', // Orange
        '#10b981', // Vert
        '#06b6d4', // Cyan
        '#6366f1', // Indigo
        '#84cc16', // Lime
        '#f97316', // Orange foncé
        '#14b8a6', // Teal
        '#a855f7', // Violet clair
        '#22c55e'  // Vert clair
    ];
    
    // Utiliser l'ID pour sélectionner une couleur de manière cohérente
    return colors[id % colors.length];
}

/**
 * @deprecated Utiliser getProjectColor(id) à la place pour une cohérence
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
