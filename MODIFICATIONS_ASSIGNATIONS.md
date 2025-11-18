# Modifications à appliquer dans main.js pour la gestion des assignations

## 1. Modifier la fonction chargerMembresProjet (ligne ~350)

Remplacer la fonction `chargerMembresProjet` existante par celle qui charge les vrais membres assignés :

```javascript
// --- Charger et afficher les membres d'un projet ---
function chargerMembresProjet(idProjet) {
  const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
  if (!avatarsContainer) return;

  // Essayer de charger les membres assignés depuis la BD
  fetch(`${API_BASE}/projets/${idProjet}/membres`)
    .then(res => res.json())
    .then(membres => {
      avatarsContainer.innerHTML = '';
      
      if (membres.length === 0) {
        // Aucun membre assigné, afficher un message ou laisser vide
        avatarsContainer.innerHTML = '<span style="color:#9ca3af;font-size:0.85rem;">Aucun membre</span>';
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
    .catch(err => console.error('Erreur chargement membres projet:', err));
}
```

## 2. Modifier la fonction ajouterProjet (ligne ~395)

Dans la fonction `ajouterProjet`, modifier le `.then(msg =>` en `.then(result =>` et ajouter la sauvegarde des membres :

```javascript
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
```

## 3. Modifier la fonction ajouterTache

De la même manière, dans `ajouterTache`, modifier pour sauvegarder les membres assignés :

```javascript
  .then(res => res.json())
  .then(result => {
    const membresCheckboxes = document.querySelectorAll('#assigneTache input[type="checkbox"]:checked');
    const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
    
    if (membresIds.length > 0 && result.idTache) {
      fetch(`${API_BASE}/taches/${result.idTache}/membres`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ membres: membresIds })
      })
        .then(() => {
          alert(result.message);
          closeModal('modalTache');
          chargerDetailsProjet();
        })
        .catch(err => console.error('Erreur assignation membres tâche:', err));
    } else {
      alert(result.message);
      closeModal('modalTache');
      chargerDetailsProjet();
    }
  })
```

## 4. Modifier enregistrerModificationProjet

Ajouter la sauvegarde des membres dans la modification :

```javascript
fetch(`${API_BASE}/projets/${idProjet}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
  .then(res => res.json())
  .then(result => {
    // Sauvegarder les membres
    const membresCheckboxes = document.querySelectorAll('#modifMembresEquipe input[type="checkbox"]:checked');
    const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
    
    return fetch(`${API_BASE}/projets/${idProjet}/membres`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ membres: membresIds })
    });
  })
  .then(() => {
    alert('Projet modifié avec succès');
    closeModal('modalModifierProjet');
    if (window.location.pathname.includes('project_details')) {
      chargerDetailsProjet();
    } else {
      chargerProjets();
    }
  })
```

## 5. Ajouter dans modifierProjet pour pré-cocher les membres

Après `chargerMembresEquipe([]);`, remplacer par :

```javascript
// Charger les membres assignés au projet
fetch(`${API_BASE}/projets/${idProjet}/membres`)
  .then(res => res.json())
  .then(membres => {
    const membresIds = membres.map(m => m.idEmploye);
    chargerMembresEquipe(membresIds, 'modifMembresEquipe');
  })
  .catch(err => {
    console.error('Erreur chargement membres:', err);
    chargerMembresEquipe([], 'modifMembresEquipe');
  });
```

## 6. Mettre à jour chargerMembresEquipe pour accepter un containerId

```javascript
function chargerMembresEquipe(selectedIds = [], containerId = 'modifMembresEquipe') {
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch(`${API_BASE}/employes`)
    .then(res => res.json())
    .then(employes => {
      container.innerHTML = '';
      employes.forEach(emp => {
        const isChecked = selectedIds.includes(emp.idEmploye);
        const label = document.createElement('label');
        label.style.cssText = 'display:flex;align-items:center;gap:8px;cursor:pointer;';
        label.innerHTML = `
          <input type="checkbox" value="${emp.idEmploye}" ${isChecked ? 'checked' : ''} 
            style="width:16px;height:16px;cursor:pointer;">
          <span>${emp.prenomEmploye || ''} ${emp.nomEmploye}</span>
        `;
        container.appendChild(label);
      });
    })
    .catch(err => console.error('Erreur chargement membres:', err));
}
```
