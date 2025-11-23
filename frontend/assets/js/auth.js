// ===========================================================
// AUTHENTIFICATION - Connexion et inscription
// ===========================================================

/**
 * Bascule entre les formulaires de connexion et d'inscription
 * @param {string} mode - 'login' ou 'register'
 */
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

/**
 * Gère la soumission du formulaire de connexion
 * @param {Event} event - Événement de soumission du formulaire
 */
function handleLogin(event) {
    event.preventDefault();
    
    // Récupération des valeurs du formulaire de connexion
    const email = event.target.querySelector('input[type="email"]').value;
    const password = event.target.querySelector('input[type="password"]').value;

    if (email && password) {
        // Appel à l'API backend pour la connexion
        fetch(`${API_BASE}/login`, {
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

/**
 * Gère la soumission du formulaire d'inscription
 * @param {Event} event - Événement de soumission du formulaire
 */
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
        fetch(`${API_BASE}/register`, {
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

/**
 * Vérifie si un utilisateur est connecté
 * @returns {Object|null} Les données de l'utilisateur ou null
 */
function getUtilisateurConnecte() {
    const userData = sessionStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

/**
 * Déconnecte l'utilisateur
 */
function logout() {
    sessionStorage.removeItem('user');
    window.location.href = "/login";
}

/**
 * Redirige vers la page de connexion si non authentifié
 */
function verifierAuthentification() {
    const user = getUtilisateurConnecte();
    if (!user && !window.location.pathname.includes('/login')) {
        window.location.href = "/login";
    }
}
