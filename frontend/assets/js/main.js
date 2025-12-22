// ===========================================================
// MAIN.JS - Point d'entrée principal de l'application
// ===========================================================

// Configuration de l'API
// Pour accès distant via ngrok, utilisez l'URL ngrok
// Pour accès local, utilisez: "http://127.0.0.1:5000/api"
const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
    ? "http://127.0.0.1:5000/api"
    : `${window.location.protocol}//${window.location.host}/api`;

// Vérification de la connexion au backend
fetch(`${API_BASE}/test`)
    .then(res => res.json())
    .then(data => console.log(" Backend connecté :", data.message))
    .catch(err => console.error(" Erreur de connexion :", err));


// ===========================================================
// INITIALISATION DE L'APPLICATION
// ===========================================================
document.addEventListener('DOMContentLoaded', () => {
    // Récupération des informations utilisateur
    const userAccess = JSON.parse(sessionStorage.getItem('user') || '{}');
    console.log('User access info:', userAccess);
    
    const isEmployee = userAccess.idRole === 3;
    const canManage = userAccess.idRole === 1 || userAccess.idRole === 2;

    // ===========================================================
    // CONTRÔLE D'ACCÈS BASÉ SUR LES RÔLES
    // ===========================================================
    if (isEmployee) {
        console.log('Masquage des boutons pour employé');
        
        // Masquer les boutons de création
        const btnAddProject = document.getElementById('btnAddProject');
        if (btnAddProject) {
            btnAddProject.style.display = 'none';
        }

        const btnAddTask = document.getElementById('btnAddTask');
        if (btnAddTask) {
            btnAddTask.style.display = 'none';
        }

        // Désactiver les formulaires pour les employés
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

        const formTache = document.getElementById('formTache');
        if (formTache) {
            formTache.addEventListener('submit', function(e) {
                e.preventDefault();
                alert("Seuls les gestionnaires et admins peuvent créer des tâches.");
            });
        }
    }

    // ===========================================================
    // DÉCONNEXION
    // ===========================================================
    const btnLogout = document.getElementById('btnLogout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            sessionStorage.removeItem('user');
            window.location.href = '/login';
        });
    }

    // ===========================================================
    // PAGE DE CONNEXION/INSCRIPTION
    // ===========================================================
    if (document.getElementById('loginForm')) {
        switchAuth('login');
        document.getElementById('loginForm').addEventListener('submit', handleLogin);
        document.getElementById('registerForm').addEventListener('submit', handleRegister);
    }

    // ===========================================================
    // AFFICHAGE DE L'UTILISATEUR DANS LE HEADER
    // ===========================================================
    const user = sessionStorage.getItem('user');
    if (user) {
        const userObj = JSON.parse(user);
        const profileDiv = document.querySelector('.profile');
        
        if (profileDiv) {
            // Mise à jour de l'avatar
            const avatar = profileDiv.querySelector('.avatar');
            if (avatar && userObj.nomEmploye) {
                avatar.textContent = userObj.nomEmploye[0].toUpperCase();
            }
            
            // Mise à jour du nom
            const nameSpan = profileDiv.querySelector('span');
            if (nameSpan && userObj.nomEmploye) {
                nameSpan.textContent = userObj.nomEmploye;
            }
            
            // Mise à jour du rôle
            const small = profileDiv.querySelector('small');
            if (small && userObj.idRole) {
                let roleTxt = 'Employé';
                if (userObj.idRole === 1) roleTxt = 'Admin';
                else if (userObj.idRole === 2) roleTxt = 'Gestionnaire';
                small.textContent = roleTxt;
            }
        }
    }

    // ===========================================================
    // PAGE DES PROJETS
    // ===========================================================
    if (document.getElementById('liste-projets')) {
        chargerProjets();
        chargerMembresEquipe();
        
        const formProjet = document.getElementById('formProjet');
        if (formProjet) formProjet.addEventListener('submit', ajouterProjet);
        
        const formModifierProjet = document.getElementById('formModifierProjet');
        if (formModifierProjet) formModifierProjet.addEventListener('submit', enregistrerModificationProjet);
    }

    // ===========================================================
    // PAGE DE GESTION DU TEMPS
    // ===========================================================
    if (document.getElementById('liste-temps')) {
        chargerTemps();
        const formTemps = document.getElementById('form-temps');
        if (formTemps) formTemps.addEventListener('submit', ajouterTemps);
    }

    // ===========================================================
    // SÉLECTION DES COULEURS (PROJETS)
    // ===========================================================
    const colorSwatches = document.querySelectorAll(".color-swatch");
    colorSwatches.forEach((swatch) => {
        swatch.addEventListener("click", () => {
            colorSwatches.forEach(s => s.classList.remove("selected"));
            swatch.classList.add("selected");
        });
    });

    // ===========================================================
    // PAGE DE DÉTAILS DU PROJET
    // ===========================================================
    if (window.location.pathname.includes("project_details")) {
        chargerDetailsProjet();
        
        const formModifierProjet = document.getElementById('formModifierProjet');
        if (formModifierProjet) formModifierProjet.addEventListener('submit', enregistrerModificationProjet);
        
        const formModifierTache = document.getElementById('formModifierTache');
        if (formModifierTache) formModifierTache.addEventListener('submit', enregistrerModificationTache);
        
        const formTache = document.getElementById('formTache');
        if (formTache) formTache.addEventListener('submit', ajouterTache);
    }
});


// ===========================================================
// FONCTION UTILITAIRE - CHARGEMENT DU TEMPS
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
        chargerTemps();
    })
    .catch(err => console.error("Erreur ajout temps :", err));
}
