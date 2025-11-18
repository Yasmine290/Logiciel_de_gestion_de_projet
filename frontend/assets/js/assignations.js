// ==================== GESTION DES ASSIGNATIONS ====================

// Sauvegarder les membres assignés lors de la création d'un projet
function sauvegarderMembresProjet(idProjet) {
  const membresCheckboxes = document.querySelectorAll('#membresEquipe input[type="checkbox"]:checked');
  const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
  
  if (membresIds.length > 0) {
    return fetch(`${API_BASE}/projets/${idProjet}/membres`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ membres: membresIds })
    });
  }
  return Promise.resolve();
}

// Charger et afficher les membres assignés à un projet
function afficherMembresProjet(idProjet) {
  fetch(`${API_BASE}/projets/${idProjet}/membres`)
    .then(res => res.json())
    .then(membres => {
      const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
      if (!avatarsContainer) return;
      
      avatarsContainer.innerHTML = '';
      
      if (membres.length === 0) {
        // Aucun membre assigné, utiliser le comportement par défaut (employés aléatoires)
        chargerMembresProjet(idProjet);
        return;
      }
      
      // Afficher jusqu'à 3 membres assignés
      const maxDisplay = 3;
      const toDisplay = membres.slice(0, maxDisplay);
      
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
    .catch(err => {
      console.error('Erreur chargement membres projet:', err);
      // En cas d'erreur, utiliser le comportement par défaut
      chargerMembresProjet(idProjet);
    });
}

// Sauvegarder les membres assignés lors de la création d'une tâche
function sauvegarderMembresTache(idTache) {
  const membresCheckboxes = document.querySelectorAll('#assigneTache input[type="checkbox"]:checked');
  const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
  
  if (membresIds.length > 0) {
    return fetch(`${API_BASE}/taches/${idTache}/membres`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ membres: membresIds })
    });
  }
  return Promise.resolve();
}

// Charger les membres assignés à une tâche (pour affichage dans la page détails)
function chargerMembresTache(idTache) {
  return fetch(`${API_BASE}/taches/${idTache}/membres`)
    .then(res => res.json())
    .then(membres => {
      if (membres.length > 0) {
        return membres.map(m => `${m.prenomEmploye || ''} ${m.nomEmploye}`.trim()).join(', ');
      }
      return 'Non assignée';
    })
    .catch(err => {
      console.error('Erreur chargement membres tâche:', err);
      return 'Erreur';
    });
}
