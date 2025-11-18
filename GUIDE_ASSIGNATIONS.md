# GUIDE COMPLET : Assignation des membres aux projets et tâches

## 📋 ÉTAPES À SUIVRE

### 1️⃣ Créer la table projet_employe dans MySQL

Exécutez ce SQL dans votre base de données `project_time_gestion` :

```sql
CREATE TABLE IF NOT EXISTS projet_employe (
  idProjet INT NOT NULL,
  idEmploye INT NOT NULL,
  PRIMARY KEY (idProjet, idEmploye),
  CONSTRAINT fk_pe_projet FOREIGN KEY (idProjet) REFERENCES projet(idProjet) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pe_employe FOREIGN KEY (idEmploye) REFERENCES employe(idEmploye) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
```

### 2️⃣ Backend déjà configuré ✅

Les endpoints suivants ont été ajoutés dans `backend/app.py` :
- `GET /api/projets/<id>/membres` - Liste les membres d'un projet
- `POST /api/projets/<id>/membres` - Assigne des membres à un projet
- `GET /api/taches/<id>/membres` - Liste les membres d'une tâche  
- `POST /api/taches/<id>/membres` - Assigne des membres à une tâche

### 3️⃣ Modifications Frontend à appliquer

#### A) Remplacer la fonction `chargerMembresProjet` (ligne ~350 dans main.js)

**AVANT :**
```javascript
function chargerMembresProjet(idProjet) {
  const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
  if (!avatarsContainer) return;

  // Récupérer tous les employés
  fetch(`${API_BASE}/employes`)
    .then(res => res.json())
    .then(employes => {
      const maxDisplay = 3;
      const shuffled = employes.sort(() => 0.5 - Math.random());
      // ...
```

**APRÈS :**
```javascript
function chargerMembresProjet(idProjet) {
  const avatarsContainer = document.getElementById(`avatars-${idProjet}`);
  if (!avatarsContainer) return;

  // Charger les membres ASSIGNÉS au projet
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
      
      toDisplay.forEach(emp => {
        const initiales = getInitiales(emp.nomEmploye, emp.prenomEmploye);
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = initiales;
        avatar.title = `${emp.prenomEmploye || ''} ${emp.nomEmploye}`;
        avatarsContainer.appendChild(avatar);
      });
      
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

#### B) Modifier `ajouterProjet` pour sauvegarder les membres sélectionnés (ligne ~410)

Remplacer :
```javascript
  .then(res => res.json())
  .then(msg => {
    alert(msg.message);
    closeModal('modalProjet');
    chargerProjets();
  })
```

Par :
```javascript
  .then(res => res.json())
  .then(result => {
    const membresCheckboxes = document.querySelectorAll('#membresEquipe input[type="checkbox"]:checked');
    const membresIds = Array.from(membresCheckboxes).map(cb => parseInt(cb.value));
    
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

#### C) Modifier `enregistrerModificationProjet` pour sauvegarder les membres

Dans la fonction `enregistrerModificationProjet`, après le fetch PUT, ajouter :

```javascript
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

#### D) Modifier `modifierProjet` pour pré-cocher les membres assignés

Remplacer `chargerMembresEquipe([]);` par :

```javascript
// Charger les membres assignés au projet
fetch(`${API_BASE}/projets/${idProjet}/membres`)
  .then(res => res.json())
  .then(membres => {
    const membresIds = membres.map(m => m.idEmploye);
    chargerMembresEquipeAvecSelection(membresIds, 'modifMembresEquipe');
  })
  .catch(err => {
    console.error('Erreur chargement membres:', err);
    chargerMembresEquipeAvecSelection([], 'modifMembresEquipe');
  });
```

#### E) Créer une nouvelle fonction `chargerMembresEquipeAvecSelection`

Ajouter cette fonction après `chargerMembresEquipe` :

```javascript
function chargerMembresEquipeAvecSelection(selectedIds = [], containerId = 'modifMembresEquipe') {
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

#### F) Pour les tâches - Modifier `ajouterTache`

Même principe que pour les projets. Remplacer :
```javascript
  .then(res => res.json())
  .then(msg => {
    alert(msg.message);
    closeModal('modalTache');
    chargerDetailsProjet();
  })
```

Par :
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

#### G) Afficher les membres dans les cartes de tâches

Dans la fonction `afficherTaches`, ajouter l'affichage des membres assignés. Après avoir créé la carte de tâche, ajouter :

```javascript
// Charger et afficher les membres assignés
fetch(`${API_BASE}/taches/${t.idTache}/membres`)
  .then(res => res.json())
  .then(membres => {
    if (membres.length > 0) {
      const membresDiv = document.createElement('div');
      membresDiv.style.cssText = 'margin-top:8px;font-size:0.85rem;color:#6b7280;';
      membresDiv.innerHTML = `<i class="fa-solid fa-users"></i> ${membres.map(m => getInitiales(m.nomEmploye, m.prenomEmploye)).join(', ')}`;
      card.appendChild(membresDiv);
    }
  })
  .catch(err => console.error('Erreur chargement membres tâche:', err));
```

## 🎯 RÉSUMÉ

Après ces modifications :
1. ✅ Les initiales affichées sur les projets seront celles des membres **réellement assignés**
2. ✅ Lors de la création d'un projet/tâche, les membres cochés seront **sauvegardés** dans la BD
3. ✅ Lors de la modification, les membres déjà assignés seront **pré-cochés**
4. ✅ Les tâches afficheront également leurs membres assignés

## 📝 NOTES

- La table `affectation_tache` existe déjà dans votre schéma, donc les assignations de tâches fonctionneront immédiatement
- Pour les projets, vous devez créer la table `projet_employe` en exécutant le SQL ci-dessus
- Si vous voulez tester rapidement : créez un projet, assignez des membres, rechargez la page projets
