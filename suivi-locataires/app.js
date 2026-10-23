// ============================================================
// MON BUDGET - Logique de l'application
// v3.0 = v2.1 + Comptes de suivi + LOCATIF (logements, compteurs,
//        charges, avis d'échéance, régularisations)
// ============================================================
// ============ DÉBOGAGE ============
window.onerror = function(message, source, lineno, colno, error) {
  const banner = document.createElement('div');
  banner.style.cssText = `
    position: fixed; top: 0; left: 0; right: 0;
    background: #ef4444; color: white; padding: 15px;
    z-index: 99999; font-family: monospace; font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  `;
  banner.innerHTML = `
    <strong>⚠️ ERREUR JAVASCRIPT</strong><br>
    <strong>Message :</strong> ${message}<br>
    <strong>Fichier :</strong> ${source.split('/').pop()}<br>
    <strong>Ligne :</strong> ${lineno} — <strong>Colonne :</strong> ${colno}<br>
    <button onclick="this.parentElement.remove()" style="
      margin-top:10px; padding:5px 10px; background:white; color:#ef4444;
      border:none; border-radius:4px; font-weight:bold; cursor:pointer;
    ">Fermer</button>
  `;
  document.body.appendChild(banner);
  return false;
};

// ============ ÉTAT ============
let state = {
  banks: [],
  transactions: [],
  categories: [
    { id: 'c1', name: 'Alimentation', budget: 400, color: '#667eea' },
    { id: 'c2', name: 'Logement', budget: 900, color: '#11998e' },
    { id: 'c3', name: 'Transport', budget: 200, color: '#f7971e' },
    { id: 'c4', name: 'Loisirs', budget: 150, color: '#eb3349' },
    { id: 'c5', name: 'Santé', budget: 80, color: '#8b5cf6' },
    { id: 'c6', name: 'Salaire', budget: 0, color: '#10b981' },
    { id: 'c7', name: 'Aides', budget: 0, color: '#06b6d4' },
    { id: 'c8', name: 'Virement', budget: 0, color: '#f59e0b' },
  ],
  recurring: [],
  forecastParams: { revGrowth: 0, inflation: 0, yield: 0, variable: 0 },
  // NOUVEAU : comptes de suivi
  accounts: [],       // { id, name, type: 'tenant'|'group', categoryIds: [] }
  accountPosts: [],   // { id, accountId, month: 'YYYY-MM', label, amount, auto? (poste créé par le Locatif), checked? }
  accountView: null,  // { accountId, month: 'YYYY-MM' } pour la vue détail

  // ---------- NOUVEAU : LOCATIF ----------
  // Un logement = un locataire. Il est relié à un compte de suivi (type 'tenant'),
  // donc les règlements viennent des transactions bancaires pointées : aucun doublon.
  logements: [],      // { id, code, locataire, adresse, surface, loyers:[{from,montant}], om:[{from,montant}],
                      //   modeCharges:'reel'|'avance', avance, elec:'releves'|'deduite',
                      //   entree, caution, irlRef, accountId, actif }
  compteurs: [],      // { id, nom, nature:'eau'|'elec', canal:'unique'|'hp'|'hc', logementId ('' = compteur général) }
  releves: {},        // { compteurId: { 'YYYY-MM': index lu à la fin du mois } }
  tarifs: [],         // [{ from:'YYYY-MM', eau, eauAbo, hc, hp, moyen, tcfe, elecAbo }]
  proprietaire: { nom: '', adresse: '', ville: '', email: '', tel: '', iban: '', bic: '', lieu: '' },
  regul: {
    om:  { annee: new Date().getFullYear(), cotisation: 0, mois: 8, surfaceTotale: 0 },
    eau: { debut: '', fin: '', totalFacture: 0, totalM3: 0, prixApplique: 0, aboReel: 0, aboFacture: 0 }
  },
  factureEdf: {}      // dernière facture EDF saisie (voir l'onglet « Facture EDF »)
};

// ============ PERSISTANCE ============
function save() {
  localStorage.setItem('budgetApp', JSON.stringify(state));
}

// S'assure que tous les champs (anciens et nouveaux) existent, quelle que soit l'origine des données
function migrate() {
  if (!Array.isArray(state.accounts)) state.accounts = [];
  if (!Array.isArray(state.accountPosts)) state.accountPosts = [];
  if (state.accountView === undefined) state.accountView = null;
  if (!Array.isArray(state.logements)) state.logements = [];
  if (!Array.isArray(state.compteurs)) state.compteurs = [];
  if (!state.releves || typeof state.releves !== 'object' || Array.isArray(state.releves)) state.releves = {};
  if (!Array.isArray(state.tarifs)) state.tarifs = [];
  state.factureEdf = { numero: '', debut: '', fin: '', hcHT: '', hpHT: '', acciseHT: '', tcfeHT: '', aboHT: '', ctaHT: '', tva: 20, nbLogements: 4, kwhFacture: '', montantHT: '', moisAbo: '', excludeLast: true, parts: {}, init: false, ...(state.factureEdf || {}) };
  state.proprietaire = { nom: '', adresse: '', ville: '', email: '', tel: '', iban: '', bic: '', lieu: '', ...(state.proprietaire || {}) };
  const r = state.regul || {};
  state.regul = {
    om:  { annee: new Date().getFullYear(), cotisation: 0, mois: 8, surfaceTotale: 0, ...(r.om || {}) },
    eau: { debut: '', fin: '', totalFacture: 0, totalM3: 0, prixApplique: 0, aboReel: 0, aboFacture: 0, ...(r.eau || {}) }
  };
}

function load() {
  const d = localStorage.getItem('budgetApp');
  if (d) try {
    const parsed = JSON.parse(d);
    state = { ...state, ...parsed };
  } catch(e) {}
  migrate();
}

// ============ OUTILS ============
const uid = () => Date.now() + Math.random().toString(36).slice(2, 7);
const fmt = n => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n || 0);
const today = () => new Date().toISOString().slice(0, 10);
const monthKey = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
const monthKeyLabel = (key) => {
  const [y, m] = key.split('-').map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
};
const addMonths = (key, n) => {
  const [y, m] = key.split('-').map(Number);
  const d = new Date(y, m - 1 + n, 1);
  return monthKey(d);
};

// ============ ACCORDÉONS ============
function toggleAccordion(id) {
  const content = document.getElementById('content-' + id);
  const icon = document.getElementById('icon-' + id);
  if (!content || !icon) return;
  
  if (content.style.display === 'none') {
    content.style.display = 'block';
    icon.textContent = '▲';
    
    // --- CORRECTION DU BUG : On nettoie le formulaire à l'ouverture ---
    if (id === 'accCreate') {
      document.getElementById('accName').value = '';
      document.querySelectorAll('.acc-cat-check').forEach(c => c.checked = false);
    }
    // ------------------------------------------------------------------
    
  } else {
    content.style.display = 'none';
    icon.textContent = '▼';
  }
}
// ============ TABS ============
document.querySelectorAll('.tab').forEach(t => {
  t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.tab).classList.add('active');
    renderAll();
  };
});
// ============ BANQUES ============
function addBank() {
  const name = bankName.value.trim();
  const acc = accountName.value.trim();
  const bal = parseFloat(bankBalance.value) || 0;
  if (!name || !acc) return alert('Remplis tous les champs');
  state.banks.push({ id: uid(), name, account: acc, balance: bal });
  bankName.value = accountName.value = bankBalance.value = '';
  save(); renderAll();
}

function editBank(id) {
  const b = state.banks.find(x => x.id === id);
  if (!b) return;
  const newName = prompt("Nom de la banque :", b.name);
  if (newName === null) return;
  const newAccount = prompt("Nom du compte :", b.account);
  if (newAccount === null) return;
  const newBalanceStr = prompt("Solde initial (€) :", b.balance);
  if (newBalanceStr === null) return;

  b.name = newName.trim() || b.name;
  b.account = newAccount.trim() || b.account;
  b.balance = parseFloat(newBalanceStr) || 0;
  
  save(); renderAll();
}

function deleteBank(id) {
  if (!confirm('Supprimer ce compte et ses transactions ?')) return;
  state.banks = state.banks.filter(b => b.id !== id);
  state.transactions = state.transactions.filter(t => t.bankId !== id);
  save(); renderAll();
}

function renderBanks() {
  const el = document.getElementById('banksList');
  if (!state.banks.length) return el.innerHTML = '<div class="empty">Aucun compte</div>';
  const now = new Date();
  el.innerHTML = state.banks.map(b => {
    const txs = state.transactions.filter(t => t.bankId === b.id);
    const balancePrevu = b.balance + txs.reduce((s, t) => s + t.amount, 0);
    const balanceReel = b.balance + txs.filter(t => t.checked).reduce((s, t) => s + t.amount, 0);
    const monthTxs = txs.filter(t => {
      const d = new Date(t.date);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    });
    const monthIncome = monthTxs.filter(t => t.amount > 0).reduce((s, t) => s + t.amount, 0);
    const monthExpense = Math.abs(monthTxs.filter(t => t.amount < 0).reduce((s, t) => s + t.amount, 0));
    const monthNet = monthIncome - monthExpense;
    const unchecked = txs.filter(t => !t.checked);
    const uncheckedTotal = unchecked.reduce((s, t) => s + t.amount, 0);
    const monthLabel = now.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });

    return `<div class="list-item" style="flex-direction:column;align-items:stretch;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div><strong>${b.name}</strong> — <span class="badge">${b.account}</span></div>
        <div style="display:flex;gap:15px;align-items:center;">
          <button class="primary" onclick="editBank('${b.id}')" style="padding:6px 10px; font-size:0.8rem;">✏️</button>
<button class="danger" onclick="deleteBank('${b.id}')">✕</button>
        </div>
      </div>
      <div style="margin-top:8px;font-size:0.9rem;">
        <div style="display:flex;justify-content:space-between;padding:2px 0;">
          <span style="color:#555;">Solde réel (pointé)</span>
          <strong class="${balanceReel >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(balanceReel)}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;padding:2px 0;">
          <span style="color:#555;">Solde prévisionnel (tout inclus)</span>
          <strong class="${balancePrevu >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(balancePrevu)}</strong>
        </div>
      </div>
      <div style="margin-top:8px;font-size:0.85rem;color:#555;">
        📅 ${monthLabel} :
        <strong class="${monthNet >= 0 ? 'amount-pos' : 'amount-neg'}">${monthNet >= 0 ? '+' : ''}${fmt(monthNet)}</strong>
        <span style="color:#888;font-size:0.8rem;">
          (${fmt(monthIncome)} entrées / ${fmt(monthExpense)} sorties)
        </span>
      </div>
      <div style="margin-top:4px;font-size:0.8rem;">
        ${unchecked.length
          ? `<span style="color:#92400e;">⬜ ${unchecked.length} à pointer (${fmt(uncheckedTotal)})</span>`
          : '<span style="color:#10b981;">✅ Tout pointé</span>'}
      </div>
    </div>`;
  }).join('');
}

// ============ BANDEAU D'ALERTE ============
function countPendingFlux() {
  const now = new Date();
  const todayDay = now.getDate();
  const mKey = monthKey(now);
  const result = { passed: 0, upcoming: 0, dueItems: [], upcomingItems: [] };

  state.recurring.forEach(r => {
    if (r.active === false) return;
    const start = new Date(r.start);
    const end = r.end ? new Date(r.end) : null;
    const currentMonthStart = new Date(now.getFullYear(), now.getMonth(), 1);
    const currentMonthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    if (start > currentMonthEnd) return;
    if (end && end < currentMonthStart) return;

    let occurrenceDay = null;
    for (let d = 1; d <= currentMonthEnd.getDate(); d++) {
      const testDate = new Date(now.getFullYear(), now.getMonth(), d);
      if (occursOn(r, testDate)) { occurrenceDay = d; break; }
    }
    if (occurrenceDay === null) return;
    if (r.lastGenerated === mKey) return;

    const isPassed = occurrenceDay <= todayDay;
    const item = { label: r.label, amount: r.amount, type: r.type, day: occurrenceDay, bankId: r.bankId };
    if (isPassed) { result.passed++; result.dueItems.push(item); }
    else { result.upcoming++; result.upcomingItems.push(item); }
  });
  return result;
}

function renderAlertBanner() {
  const el = document.getElementById('alertBanner');
  if (!el) return;
  const pending = countPendingFlux();
  if (pending.passed > 0) {
    el.className = 'alert-banner warning';
    el.innerHTML = `
      <span>⚠️ <strong>${pending.passed} opération(s) planifiée(s) à valider</strong> pour ce mois.</span>
      <button onclick="generateMonthTransactions()">✅ Valider maintenant</button>
    `;
    return;
  }
  if (pending.upcoming > 0) {
    const label = pending.upcoming === 1 ? 'opération' : 'opérations';
    el.className = 'alert-banner info';
    el.innerHTML = `<span>📅 <strong>${pending.upcoming} ${label} planifiée(s)</strong> à venir ce mois-ci.</span>`;
    return;
  }
  el.className = 'alert-banner';
  el.innerHTML = '';
}

function renderTxBanksSummary() {
  const el = document.getElementById('txBanksSummary');
  if (!el) return;
  if (!state.banks.length) { el.innerHTML = '<div class="empty">Aucun compte bancaire</div>'; return; }
  const now = new Date();
  const monthLabel = now.toLocaleDateString('fr-FR', { month: 'long' });
  el.innerHTML = state.banks.map(b => {
    const txs = state.transactions.filter(t => t.bankId === b.id);
    const balancePrevu = b.balance + txs.reduce((s, t) => s + t.amount, 0);
    const balanceReel = b.balance + txs.filter(t => t.checked).reduce((s, t) => s + t.amount, 0);
    const monthTxs = txs.filter(t => {
      const d = new Date(t.date);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    });
    const monthNet = monthTxs.reduce((s, t) => s + t.amount, 0);
    return `<div class="list-item" style="flex-direction:column;align-items:stretch;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div><strong>${b.name}</strong> <span class="badge">${b.account}</span></div>
        <div style="font-size:0.85rem;color:#666;">
          ${monthLabel} : <strong class="${monthNet >= 0 ? 'amount-pos' : 'amount-neg'}">${monthNet >= 0 ? '+' : ''}${fmt(monthNet)}</strong>
        </div>
      </div>
      <div style="margin-top:6px;font-size:0.9rem;">
        <div style="display:flex;justify-content:space-between;padding:2px 0;">
          <span style="color:#555;">Solde réel (pointé)</span>
          <strong class="${balanceReel >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(balanceReel)}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;padding:2px 0;">
          <span style="color:#555;">Solde prévisionnel (tout inclus)</span>
          <strong class="${balancePrevu >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(balancePrevu)}</strong>
        </div>
      </div>
    </div>`;
  }).join('');
}
// ============ CATÉGORIES ============
function addCategory() {
  const name = catName.value.trim();
  const budget = parseFloat(catBudget.value) || 0;
  if (!name) return;
  const colors = ['#667eea','#11998e','#f7971e','#eb3349','#8b5cf6','#06b6d4','#ec4899','#84cc16'];
  state.categories.push({ id: uid(), name, budget, color: colors[state.categories.length % colors.length] });
  catName.value = catBudget.value = '';
  save(); renderAll();
}
function editCategory(id) {
  const c = state.categories.find(x => x.id === id);
  if (!c) return;

  const newName = prompt("Nom de la catégorie :", c.name);
  if (newName === null) return;
  const cleanName = newName.trim();
  if (!cleanName) return alert("Le nom ne peut pas être vide");

  // Vérifie qu'il n'y a pas déjà une autre catégorie avec ce nom
  const doublon = state.categories.find(x =>
    x.id !== id && x.name.trim().toLowerCase() === cleanName.toLowerCase()
  );
  if (doublon) {
    if (!confirm(`Une catégorie "${doublon.name}" existe déjà.\n\nFusionner les deux ? (les transactions de l'ancienne seront rattachées à celle-ci)`)) return;
    // Fusion : on réaffecte tout ce qui pointait vers le doublon, puis on supprime le doublon
    state.transactions.forEach(t => { if (t.categoryId === doublon.id) t.categoryId = c.id; });
    state.recurring.forEach(r => { if (r.categoryId === doublon.id) r.categoryId = c.id; });
    state.accounts.forEach(a => {
      a.categoryIds = (a.categoryIds || []).map(cid => cid === doublon.id ? c.id : cid);
      a.categoryIds = [...new Set(a.categoryIds)]; // dédoublonne
    });
    state.accountPosts.forEach(p => {
      if (p.sourceId === doublon.id) p.sourceId = c.id;
    });
    state.categories = state.categories.filter(x => x.id !== doublon.id);
  }

  c.name = cleanName;
  save();
  renderAll();
}

function deleteCategory(id) {
  if (state.categories.length <= 1) return alert('Garde au moins une catégorie');
  state.categories = state.categories.filter(c => c.id !== id);
  state.recurring = state.recurring.filter(r => r.categoryId !== id);
  // Retirer la catégorie des comptes de suivi
  state.accounts.forEach(a => {
    a.categoryIds = (a.categoryIds || []).filter(cid => cid !== id);
  });
  save(); renderAll();
}

function renderCategories() {
  const el = document.getElementById('categoriesList');
  if (!state.categories.length) return el.innerHTML = '<div class="empty">Aucune catégorie</div>';
  const sorted = [...state.categories].sort((a, b) =>
    a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
  );
  el.innerHTML = sorted.map(c => {
    const now = new Date();
    const monthTxs = state.transactions.filter(t => {
      const d = new Date(t.date);
      return t.categoryId === c.id && t.amount < 0 && !t.transferId
        && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    });
    const spent = Math.abs(monthTxs.reduce((s, t) => s + t.amount, 0));
    const pct = c.budget > 0 ? Math.min(100, (spent / c.budget) * 100) : 0;
    return `<div class="list-item">
      <div style="flex:1;">
        <div style="display:flex;justify-content:space-between;">
          <strong>${c.name}</strong>
          <span style="font-size:0.85rem;">${fmt(spent)} ${c.budget > 0 ? '/ ' + fmt(c.budget) : ''}</span>
        </div>
        ${c.budget > 0 ? `<div style="background:#eee;height:6px;border-radius:3px;margin-top:6px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:${pct > 90 ? '#ef4444' : c.color};"></div>
        </div>` : ''}
      </div>
      <div style="display:flex;gap:8px;margin-left:15px;">
  <button class="primary" style="padding:6px 10px;font-size:0.8rem;" onclick="editCategory('${c.id}')">✏️</button>
  <button class="danger" onclick="deleteCategory('${c.id}')">✕</button>
</div>
    </div>`;
  }).join('');
}

// ============ TRANSACTIONS ============
function populateSelects() {
  const keep = {
    txBank: txBank.value,
    txCat: txCat.value,
    txType: txType.value,
    txDate: txDate.value,
    rcBank: rcBank.value,
    rcCat: rcCat.value,
    trFrom: trFrom.value,
    trTo: trTo.value,
    trCat: trCat.value,
    mcBank: mcBank.value,
    filterBank: filterBank.value,
    filterStatus: document.getElementById('filterStatus').value,
    filterType: document.getElementById('filterType').value
  };

  const bankOpts = state.banks.length
    ? state.banks.map(b => `<option value="${b.id}">${b.name} - ${b.account}</option>`).join('')
    : '<option value="">Aucun compte</option>';
  txBank.innerHTML = bankOpts;
  rcBank.innerHTML = bankOpts;
  trFrom.innerHTML = bankOpts;
  trTo.innerHTML = bankOpts;
  mcBank.innerHTML = bankOpts;

  const sortedCats = [...state.categories].sort((a, b) =>
    a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
  );
  const catOpts = sortedCats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  txCat.innerHTML = catOpts;
  rcCat.innerHTML = catOpts;
  trCat.innerHTML = '<option value="">Aucune</option>' + catOpts;

  filterBank.innerHTML = '<option value="">Toutes les banques</option>'
    + state.banks.map(b => `<option value="${b.id}">${b.name} - ${b.account}</option>`).join('');

  const restore = (el, val) => {
    if (!el || val === undefined || val === null) return;
    if (el.tagName === 'SELECT') {
      const exists = Array.from(el.options).some(o => o.value === val);
      if (exists) el.value = val;
    } else {
      el.value = val;
    }
  };

  restore(txBank, keep.txBank);
  restore(txCat, keep.txCat);
  restore(txType, keep.txType);
  restore(txDate, keep.txDate);
  restore(rcBank, keep.rcBank);
  restore(rcCat, keep.rcCat);
  restore(trFrom, keep.trFrom);
  restore(trTo, keep.trTo);
  restore(trCat, keep.trCat);
  restore(mcBank, keep.mcBank);
  restore(filterBank, keep.filterBank);
  restore(document.getElementById('filterStatus'), keep.filterStatus);
  restore(document.getElementById('filterType'), keep.filterType);
}

function addTransaction() {
  if (!state.banks.length) return alert("Ajoute d'abord un compte bancaire");
  const type = document.getElementById('txType').value;
  const bankId = txBank.value;
  const label = txLabel.value.trim();
  const amountRaw = parseFloat(txAmount.value);
  const categoryId = txCat.value;
  const date = txDate.value || today();
  if (isNaN(amountRaw) || amountRaw <= 0) return alert('Montant (> 0) requis');

  if (date > today()) {
    const ok = confirm(
      "⚠️ Cette transaction est datée dans le FUTUR.\n\n" +
      "Elle apparaîtra dans l'historique, mais ne sera PAS comptée dans le solde réel (pointé) tant que vous ne l'aurez pas pointée.\n\n" +
      "Pour les opérations qui se répètent (loyer, pension…), préférez le bouton 🔁 Planifier.\n\n" +
      "Continuer quand même ?"
    );
    if (!ok) return;
  }

  const amount = type === 'income' ? Math.abs(amountRaw) : -Math.abs(amountRaw);
  state.transactions.push({ id: uid(), bankId, label: label || '(sans libellé)', amount, categoryId, date, checked: false });

  const keepBank = txBank.value;
  const keepDate = txDate.value;
  const keepCat = txCat.value;
  const keepType = txType.value;

  txLabel.value = '';
  txAmount.value = '';

  save();
  renderAll();

  txBank.value = keepBank;
  txDate.value = keepDate;
  txCat.value = keepCat;
  txType.value = keepType;
}

function toggleCheck(id) {
  const t = state.transactions.find(x => x.id === id);
  if (!t) return;
  
  // On bascule simplement l'état (coché / décoché)
  t.checked = !t.checked;
  
  save(); renderAll();
}

function editTransaction(id) {
  openEditTransactionModal(id);
}

function openEditTransactionModal(id) {
  const t = state.transactions.find(x => x.id === id);
  if (!t) return;

  document.getElementById('editTransactionModal').dataset.txId = id;

  // Remplir les listes
  const sortedCats = [...state.categories].sort((a, b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' }));
  document.getElementById('etCat').innerHTML = sortedCats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  document.getElementById('etBank').innerHTML = state.banks.map(b => `<option value="${b.id}">${b.name} - ${b.account}</option>`).join('');

  // Remplir les champs avec les valeurs actuelles
  document.getElementById('etDate').value = t.date;
  document.getElementById('etLabel').value = t.label === '(sans libellé)' ? '' : t.label;
  document.getElementById('etBank').value = t.bankId;
  document.getElementById('etCat').value = t.categoryId || '';
  
  // Gérer le type et le montant
  document.getElementById('etType').value = t.amount >= 0 ? 'income' : 'expense';
  document.getElementById('etAmount').value = Math.abs(t.amount);

  document.getElementById('editTransactionModal').classList.add('active');
}

function closeEditTransactionModal() {
  document.getElementById('editTransactionModal').classList.remove('active');
}

function saveEditTransaction() {
  const id = document.getElementById('editTransactionModal').dataset.txId;
  const t = state.transactions.find(x => x.id === id);
  if (!t) return;

  const type = document.getElementById('etType').value;
  const amountRaw = parseFloat(document.getElementById('etAmount').value);
  const date = document.getElementById('etDate').value;
  const label = document.getElementById('etLabel').value.trim();
  const bankId = document.getElementById('etBank').value;
  const categoryId = document.getElementById('etCat').value;

  if (isNaN(amountRaw) || amountRaw <= 0) return alert('Montant (> 0) requis');
  if (!date) return alert('La date est requise');

  // Mise à jour
  t.amount = type === 'income' ? Math.abs(amountRaw) : -Math.abs(amountRaw);
  t.date = date;
  t.label = label || '(sans libellé)';
  t.bankId = bankId;
  t.categoryId = categoryId;

  closeEditTransactionModal();
  save(); renderAll();
}

function deleteTransaction(id) {
  const t = state.transactions.find(x => x.id === id);
  if (!t) return;
  if (t.transferId) {
    if (!confirm("Cette transaction fait partie d'un virement. Supprimer les DEUX côtés ?")) return;
    state.transactions = state.transactions.filter(x => x.transferId !== t.transferId);
  } else {
    if (!confirm('Supprimer cette transaction ?')) return;
    state.transactions = state.transactions.filter(x => x.id !== id);
  }
  save(); renderAll();
}

// ============ REGROUPEMENT PAR MOIS DANS L'HISTORIQUE ============
let openTxMonths = []; // mois actuellement dépliés (mémoire uniquement)

// Ouvre / ferme un mois dans l'historique
function toggleTxMonth(mKey) {
  if (openTxMonths.includes(mKey)) {
    openTxMonths = openTxMonths.filter(k => k !== mKey);
  } else {
    openTxMonths.push(mKey);
  }
  renderTransactions();
}

// Construit l'HTML d'un bloc mois (en-tête + table des transactions)
function renderTxMonthBlock(mKey, txs, allTxsForFilter, bankFilterId) {
  const isOpen = openTxMonths.includes(mKey);
  const label = monthKeyLabel(mKey);

  // Net du mois (recettes - dépenses), calculé sur les transactions filtrées
  const net = txs.reduce((s, t) => s + t.amount, 0);

  // Solde de fin de mois = solde initial de la banque (ou des banques)
  // + toutes les transactions jusqu'à la fin de ce mois inclus
  let soldeFin = 0;
  if (bankFilterId) {
    const b = state.banks.find(x => x.id === bankFilterId);
    if (b) {
      soldeFin = b.balance + allTxsForFilter
        .filter(t => t.bankId === bankFilterId && t.date.slice(0, 7) <= mKey)
        .reduce((s, t) => s + t.amount, 0);
    }
  } else {
    // Toutes banques : somme des soldes initiaux + toutes les transactions jusqu'à fin du mois
    soldeFin = state.banks.reduce((s, b) => s + b.balance, 0)
      + allTxsForFilter
        .filter(t => t.date.slice(0, 7) <= mKey)
        .reduce((s, t) => s + t.amount, 0);
  }

  const netClass = net >= 0 ? 'amount-pos' : 'amount-neg';
  const soldeClass = soldeFin >= 0 ? 'amount-pos' : 'amount-neg';

  const rows = txs.map(t => {
    const cat = state.categories.find(c => c.id === t.categoryId);
    const bank = state.banks.find(b => b.id === t.bankId);
    const rowClass = [t.transferId ? 'row-transfer' : '', !t.checked ? 'row-unchecked' : ''].filter(Boolean).join(' ');
    return `<tr class="${rowClass}">
      <td><span class="check ${t.checked ? 'done' : 'todo'}" onclick="toggleCheck('${t.id}')">${t.checked ? '✅' : '⬜'}</span></td>
      <td>${new Date(t.date).toLocaleDateString('fr-FR')}</td>
      <td>${cat ? `<span class="badge ${t.amount >= 0 ? 'income' : 'expense'}">${cat.name}</span>` : '-'}</td>
      <td>${t.label} ${t.transferId ? '<span class="badge transfer">🔄</span>' : ''}</td>
      <td>${bank ? bank.name : '-'}</td>
      <td class="${t.amount >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(t.amount)}</td>
      <td>
        <button class="primary" onclick="editTransaction('${t.id}')" style="padding:6px 10px; font-size:0.8rem;">✏️</button>
        <button class="danger" onclick="deleteTransaction('${t.id}')">✕</button>
      </td>
    </tr>`;
  }).join('');

  return `<div class="tx-month-block" style="margin-bottom:12px;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;">
    <div class="tx-month-header" style="display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#f9fafb;cursor:pointer;gap:15px;flex-wrap:wrap;" onclick="toggleTxMonth('${mKey}')">
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:1rem;">${isOpen ? '▼' : '▶'}</span>
        <strong style="font-size:1rem;color:#16213e;">${label}</strong>
        <span style="font-size:0.8rem;color:#888;">${txs.length} transaction(s)</span>
      </div>
      <div style="display:flex;gap:20px;font-size:0.9rem;flex-wrap:wrap;">
        <span>Net du mois : <strong class="${netClass}">${net >= 0 ? '+' : ''}${fmt(net)}</strong></span>
        <span>Solde fin de mois : <strong class="${soldeClass}">${fmt(soldeFin)}</strong></span>
      </div>
    </div>
    ${isOpen ? `<div style="padding:0 15px 15px;">
      <table><thead><tr>
        <th style="width:40px;"></th>
        <th>Date</th><th>Catégorie</th><th>Libellé</th><th>Banque</th><th>Montant</th><th></th>
      </tr></thead><tbody>${rows}</tbody></table>
    </div>` : ''}
  </div>`;
}

function renderTransactions() {
  const el = document.getElementById('transactionsList');
  let txs = [...state.transactions].sort((a, b) => b.date.localeCompare(a.date));
  const fBank = document.getElementById('filterBank').value;
  const fStatus = document.getElementById('filterStatus').value;
  const fType = document.getElementById('filterType').value;

  // On garde une copie complète pour le calcul du solde de fin de mois,
  // car le solde doit tenir compte de TOUTES les transactions jusqu'au mois affiché,
  // même celles masquées par le filtre statut/type.
  const allTxsForFilter = [...state.transactions];

  // Application des filtres pour l'affichage des lignes
  if (fBank) txs = txs.filter(t => t.bankId === fBank);
  if (fStatus === 'unchecked') txs = txs.filter(t => !t.checked);
  if (fStatus === 'checked') txs = txs.filter(t => t.checked);
  if (fType === 'transfer') txs = txs.filter(t => t.transferId);
  if (fType === 'income') txs = txs.filter(t => t.amount > 0 && !t.transferId);
  if (fType === 'expense') txs = txs.filter(t => t.amount < 0 && !t.transferId);

  if (!txs.length) return el.innerHTML = '<div class="empty">Aucune transaction</div>';

  // Regroupement par mois (clé 'YYYY-MM')
  const byMonth = {};
  txs.forEach(t => {
    const mKey = t.date.slice(0, 7);
    if (!byMonth[mKey]) byMonth[mKey] = [];
    byMonth[mKey].push(t);
  });

  // Tri des mois du plus récent au plus ancien
  const monthsSorted = Object.keys(byMonth).sort((a, b) => b.localeCompare(a));

  // Par défaut, on ouvre le mois le plus récent s'il n'y a aucun mois ouvert
  if (openTxMonths.length === 0 && monthsSorted.length > 0) {
    openTxMonths.push(monthsSorted[0]);
  }

  el.innerHTML = monthsSorted.map(mKey =>
    renderTxMonthBlock(mKey, byMonth[mKey], allTxsForFilter, fBank)
  ).join('');
}
// ============ VIREMENTS ============
function openTransferModal() {
  if (state.banks.length < 2) return alert('Il faut au moins 2 comptes bancaires');
  trDate.value = today();
  document.getElementById('transferModal').classList.add('active');
}

function closeTransferModal() {
  document.getElementById('transferModal').classList.remove('active');
}

function saveTransfer() {
  const fromBankId = trFrom.value;
  const toBankId = trTo.value;
  const amount = parseFloat(trAmount.value);
  const label = trLabel.value.trim() || 'Virement';
  const date = trDate.value || today();
  const categoryId = trCat.value || null;
  if (fromBankId === toBankId) return alert('Les comptes source et destination doivent être différents');
  if (isNaN(amount) || amount <= 0) return alert('Montant invalide');
  const fromBank = state.banks.find(b => b.id === fromBankId);
  const toBank = state.banks.find(b => b.id === toBankId);
  const transferId = 'tr-' + uid();
  state.transactions.push({
    id: uid(), bankId: fromBankId, label: `${label} → ${toBank.name}`,
    amount: -Math.abs(amount), categoryId, date, checked: false, transferId
  });
  state.transactions.push({
    id: uid(), bankId: toBankId, label: `${label} ← ${fromBank.name}`,
    amount: Math.abs(amount), categoryId, date, checked: false, transferId
  });
  trAmount.value = ''; trLabel.value = '';
  closeTransferModal();
  save(); renderAll();
}

// ============ RÉCURRENT (depuis formulaire) ============
let pendingTransaction = null;

function openRecurringFromForm() {
  const type = document.getElementById('txType').value;
  const bankId = txBank.value;
  const label = txLabel.value.trim();
  const amountRaw = parseFloat(txAmount.value);
  const categoryId = txCat.value;
  const date = txDate.value || today();

  if (!bankId) return alert("Sélectionne d'abord un compte bancaire");
  if (isNaN(amountRaw) || amountRaw <= 0) return alert('Remplis le montant (> 0)');

  const amount = type === 'income' ? Math.abs(amountRaw) : -Math.abs(amountRaw);
  const finalLabel = label || '(sans libellé)';
  pendingTransaction = { bankId, label: finalLabel, amount, categoryId, date };

  document.getElementById('recDescription').innerHTML =
    `<strong>${finalLabel}</strong><br>` +
    `Montant : ${fmt(amount)}<br>` +
    `Banque : ${state.banks.find(b => b.id === bankId)?.name || '?'}<br>` +
    `Type : ${type === 'income' ? '💰 Recette' : '💸 Dépense'}`;

  const d = new Date(date);
  document.getElementById('recDay').value = d.getDate();
  document.getElementById('recFreq').value = 'monthly';
  document.getElementById('recEnd').value = '';
  document.getElementById('recurringModal').classList.add('active');
}

function closeRecurringModal() {
  document.getElementById('recurringModal').classList.remove('active');
  pendingTransaction = null;
}

function saveRecurringFromTransaction() {
  if (!pendingTransaction) return;
  const freq = document.getElementById('recFreq').value;
  const day = Math.min(31, Math.max(1, parseInt(document.getElementById('recDay').value) || 1));
  const end = document.getElementById('recEnd').value || null;
  const { bankId, label, amount, categoryId, date } = pendingTransaction;
  const type = amount >= 0 ? 'income' : 'expense';

  state.recurring.push({
    id: uid(), type, label, amount: Math.abs(amount),
    categoryId, bankId, freq, day, start: date, end
  });

  state.transactions.push({
    id: uid(), bankId, label, amount, categoryId, date, checked: false
  });

  const keepBank = txBank.value;
  const keepDate = txDate.value;
  const keepCat = txCat.value;
  const keepType = txType.value;

  txLabel.value = '';
  txAmount.value = '';

  closeRecurringModal();
  save();
  renderAll();

  txBank.value = keepBank;
  txDate.value = keepDate;
  txCat.value = keepCat;
  txType.value = keepType;

  alert('✅ Flux récurrent créé !\n\nLa transaction a été ajoutée à l\'historique.');
}

// ============ POINTAGE EN MASSE ============
function openMassCheckModal() {
  document.getElementById('massCheckModal').classList.add('active');
  updateMassCheckOptions();
}

function closeMassCheckModal() {
  document.getElementById('massCheckModal').classList.remove('active');
}

function updateMassCheckOptions() {
  const type = document.getElementById('mcType').value;
  document.getElementById('mcBankOpts').style.display = type === 'bank' ? 'block' : 'none';
}

function executeMassCheck() {
  const type = document.getElementById('mcType').value;
  let count = 0;
  if (type === 'month') {
    const now = new Date();
    state.transactions.forEach(t => {
      const d = new Date(t.date);
      if (!t.checked && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()) {
        t.checked = true; count++;
      }
    });
  } else {
    const bankId = document.getElementById('mcBank').value;
    state.transactions.forEach(t => {
      if (!t.checked && t.bankId === bankId) { t.checked = true; count++; }
    });
  }
  closeMassCheckModal();
  save(); renderAll();
  alert(`✅ ${count} transaction(s) pointée(s)`);
}

// ============ RÉCURRENTS (onglet) ============
function addRecurring() {
  if (!state.banks.length) return alert("Ajoute d'abord un compte bancaire");
  const type = rcType.value;
  const label = rcLabel.value.trim();
  const amount = parseFloat(rcAmount.value);
  const categoryId = rcCat.value;
  const bankId = rcBank.value;
  const freq = rcFreq.value;
  const day = Math.min(31, Math.max(1, parseInt(rcDay.value) || 1));
  const start = rcStart.value || today();
  const end = rcEnd.value || null;
  if (isNaN(amount) || amount <= 0) return alert('Montant (> 0) requis');
  state.recurring.push({ id: uid(), type, label: label || '(sans libellé)', amount: Math.abs(amount), categoryId, bankId, freq, day, start, end });
  rcLabel.value = rcAmount.value = '';
  save(); renderAll();
}
let recurringToEdit = null;

function openEditRecurring(id) {
  const r = state.recurring.find(x => x.id === id);
  if (!r) return;
  recurringToEdit = id;

  const sortedCats = [...state.categories].sort((a, b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' }));
  document.getElementById('erCat').innerHTML = sortedCats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  document.getElementById('erBank').innerHTML = state.banks.map(b => `<option value="${b.id}">${b.name} - ${b.account}</option>`).join('');

  document.getElementById('erType').value = r.type;
  document.getElementById('erLabel').value = r.label === '(sans libellé)' ? '' : r.label;
  document.getElementById('erAmount').value = r.amount;
  document.getElementById('erCat').value = r.categoryId || '';
  document.getElementById('erBank').value = r.bankId;
  document.getElementById('erFreq').value = r.freq;
  document.getElementById('erDay').value = r.day;
  document.getElementById('erStart').value = r.start;
  document.getElementById('erEnd').value = r.end || '';

  document.getElementById('editRecurringModal').classList.add('active');
}

function saveEditRecurring() {
  if (!recurringToEdit) return;
  const r = state.recurring.find(x => x.id === recurringToEdit);
  if (!r) return;

  const type = document.getElementById('erType').value;
  const label = document.getElementById('erLabel').value.trim();
  const amount = parseFloat(document.getElementById('erAmount').value);
  const categoryId = document.getElementById('erCat').value;
  const bankId = document.getElementById('erBank').value;
  const freq = document.getElementById('erFreq').value;
  const day = Math.min(31, Math.max(1, parseInt(document.getElementById('erDay').value) || 1));
  const start = document.getElementById('erStart').value || today();
  const end = document.getElementById('erEnd').value || null;

  if (isNaN(amount) || amount <= 0) return alert('Montant (> 0) requis');

  // Mise à jour du flux existant
  r.type = type;
  r.label = label || '(sans libellé)';
  r.amount = Math.abs(amount);
  r.categoryId = categoryId;
  r.bankId = bankId;
  r.freq = freq;
  r.day = day;
  r.start = start;
  r.end = end;

  // Mise à jour automatique des postes futurs dans les comptes de suivi
  const mKeyNow = monthKey(new Date());
  state.accountPosts.forEach(p => {
    // Si le poste a été créé à partir de ce flux et qu'il concerne un mois futur
    if (p.label === r.label && p.month >= mKeyNow) {
      p.amount = type === 'income' ? r.amount : -r.amount;
    }
  });

  document.getElementById('editRecurringModal').classList.remove('active');
  recurringToEdit = null;
  save(); renderAll();
}

function deleteRecurring(id) {
  const r = state.recurring.find(x => x.id === id);
  if (r && r.transferRecurringId) {
    if (!confirm("Ce flux fait partie d'un virement récurrent. Supprimer les DEUX flux ?")) return;
    state.recurring = state.recurring.filter(x => x.transferRecurringId !== r.transferRecurringId);
  } else {
    state.recurring = state.recurring.filter(x => x.id !== id);
  }
  save(); renderAll();
}

function toggleRecurring(id) {
  const r = state.recurring.find(x => x.id === id);
  if (r) { r.active = r.active === false ? true : false; save(); renderAll(); }
}

function freqLabel(f) {
  return {
    monthly: 'Mensuelle',
    bimonthly: 'Bimestrielle',
    quarterly: 'Trimestrielle',
    yearly: 'Annuelle'
  }[f] || f;
}

function renderRecurring() {
  const el = document.getElementById('recurringList');
  if (!state.recurring.length) {
    el.innerHTML = '<div class="empty">Aucun flux planifié.</div>';
  } else {
    const byBank = {};
    state.recurring.forEach(r => {
      const key = r.bankId || '_none';
      if (!byBank[key]) byBank[key] = [];
      byBank[key].push(r);
    });

    const sections = state.banks.map(b => {
      const fluxes = byBank[b.id] || [];
      if (!fluxes.length) return '';
      const incomes = fluxes.filter(r => r.type === 'income');
      const expenses = fluxes.filter(r => r.type === 'expense');
      const sorted = [...incomes, ...expenses];

      const rows = sorted.map(r => {
        const cat = state.categories.find(c => c.id === r.categoryId);
        const inactive = r.active === false;
        return `<div class="list-item" style="${inactive ? 'opacity:0.5;' : ''}">
          <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
              <span class="badge ${r.type}">${r.type === 'income' ? '💰 Recette' : '💸 Dépense'}</span>
${r.transferRecurringId ? '<span class="badge transfer">🔄 Virement</span>' : ''}
${cat ? `<span class="badge ${r.type === 'income' ? 'income' : 'expense'}">${cat.name}</span>` : ''}
<strong>${r.label}</strong>
            </div>
            <div style="font-size:0.8rem;color:#666;margin-top:4px;">
              ${freqLabel(r.freq)} · jour ${r.day} ·
              du ${new Date(r.start).toLocaleDateString('fr-FR')}${r.end ? ' au ' + new Date(r.end).toLocaleDateString('fr-FR') : ''}
            </div>
          </div>
          <div style="display:flex;gap:10px;align-items:center;">
            <span class="${r.type === 'income' ? 'amount-pos' : 'amount-neg'}">${fmt(r.amount)}</span>
            <button class="primary" onclick="openEditRecurring('${r.id}')" style="padding:6px 10px; font-size:0.8rem;">✏️</button>
            <button class="danger" onclick="toggleRecurring('${r.id}')">${inactive ? '▶' : '⏸'}</button>
            <button class="danger" onclick="deleteRecurring('${r.id}')">✕</button>
          </div>
        </div>`;
      }).join('');

      return `<div class="section-title" style="font-size:1rem;color:#16213e;margin-top:24px;">🏦 ${b.name} — ${b.account}</div>${rows}`;
    }).join('');

    el.innerHTML = sections || '<div class="empty">Aucun flux planifié</div>';
  }

  const sum = state.recurring.filter(r => r.active !== false).reduce((acc, r) => {
    const monthly = toMonthly(r.amount, r.freq);
    if (r.type === 'income') acc.income += monthly;
    else acc.expense += monthly;
    return acc;
  }, { income: 0, expense: 0 });

  document.getElementById('recurringSummary').innerHTML = `
    <div class="kpi green"><div class="kpi-label">Recettes / mois</div><div class="kpi-value">${fmt(sum.income)}</div></div>
    <div class="kpi red"><div class="kpi-label">Dépenses / mois</div><div class="kpi-value">${fmt(sum.expense)}</div></div>
    <div class="kpi ${sum.income - sum.expense >= 0 ? 'green' : 'red'}">
      <div class="kpi-label">Épargne / mois</div><div class="kpi-value">${fmt(sum.income - sum.expense)}</div>
    </div>
    <div class="kpi orange"><div class="kpi-label">Épargne / an</div><div class="kpi-value">${fmt((sum.income - sum.expense) * 12)}</div></div>
  `;
}

function toMonthly(amount, freq) {
  switch (freq) {
    case 'bimonthly': return amount / 2;
    case 'quarterly': return amount / 3;
    case 'yearly': return amount / 12;
    default: return amount;
  }
}

// ============ GÉNÉRATION TRANSACTIONS RÉCURRENTES ============
function occursOn(r, date) {
  if (r.active === false) return false;
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const start = new Date(r.start);
  const end = r.end ? new Date(r.end) : null;
  const startDay = new Date(start.getFullYear(), start.getMonth(), start.getDate());

  if (d < startDay) return false;
  if (end && d > new Date(end.getFullYear(), end.getMonth(), end.getDate())) return false;

  switch (r.freq) {
    case 'monthly': {
      const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
      const targetDay = Math.min(r.day, lastDay);
      if (d.getDate() !== targetDay) return false;
      if (d.getFullYear() < start.getFullYear()) return false;
      if (d.getFullYear() === start.getFullYear() && d.getMonth() < start.getMonth()) return false;
      return true;
    }
    
    case 'bimonthly': {
      const monthsDiff = (d.getFullYear() - start.getFullYear()) * 12 + (d.getMonth() - start.getMonth());
      if (monthsDiff < 0 || monthsDiff % 2 !== 0) return false;
      const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
      return d.getDate() === Math.min(r.day, lastDay);
    }
    case 'quarterly': {
      const monthsDiff = (d.getFullYear() - start.getFullYear()) * 12 + (d.getMonth() - start.getMonth());
      if (monthsDiff < 0 || monthsDiff % 3 !== 0) return false;
      const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
      return d.getDate() === Math.min(r.day, lastDay);
    }
    case 'yearly': {
      if (d.getMonth() !== start.getMonth()) return false;
      const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
      return d.getDate() === Math.min(r.day, lastDay);
    }
  }
  return false;
}

function generateForMonth(year, month) {
  let generated = 0;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  for (let day = 1; day <= daysInMonth; day++) {
    const dateObj = new Date(year, month, day);
    const dateStr = dateObj.getFullYear() + '-' +
      String(dateObj.getMonth() + 1).padStart(2, '0') + '-' +
      String(dateObj.getDate()).padStart(2, '0');
    state.recurring.forEach(r => {
      if (!occursOn(r, dateObj)) return;
      const exists = state.transactions.some(t =>
        t.date === dateStr && t.label === r.label && t.bankId === r.bankId &&
        ((r.type === 'income' && t.amount > 0) || (r.type === 'expense' && t.amount < 0))
      );
      if (exists) return;
      state.transactions.push({
        id: uid(), bankId: r.bankId, label: r.label,
        amount: r.type === 'income' ? r.amount : -r.amount,
        categoryId: r.categoryId, date: dateStr, checked: false
      });
      generated++;
    });
  }
  save(); renderAll();
  alert(`✅ ${generated} transaction(s) générée(s)`);
}

function generateMonthTransactions() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const todayDay = now.getDate();
  const mKey = year + '-' + String(month + 1).padStart(2, '0');
  let generated = 0;
  let alreadyThere = 0;

  for (let day = 1; day <= todayDay; day++) {
    const dateObj = new Date(year, month, day);
    const dateStr = year + '-' +
      String(month + 1).padStart(2, '0') + '-' +
      String(day).padStart(2, '0');

    state.recurring.forEach(r => {
      if (r.active === false) return;
      if (r.lastGenerated === mKey) return;
      if (!occursOn(r, dateObj)) return;

      const exists = state.transactions.some(t =>
        t.date === dateStr && t.label === r.label && t.bankId === r.bankId &&
        ((r.type === 'income' && t.amount > 0) || (r.type === 'expense' && t.amount < 0))
      );
      if (exists) { alreadyThere++; return; }

      state.transactions.push({
        id: uid(), bankId: r.bankId, label: r.label,
        amount: r.type === 'income' ? r.amount : -r.amount,
        categoryId: r.categoryId, date: dateStr, checked: false
      });
      generated++;
    });
  }

  state.recurring.forEach(r => {
    if (r.active === false) return;
    let tombeCeMois = false;
    for (let d = 1; d <= new Date(year, month + 1, 0).getDate(); d++) {
      if (occursOn(r, new Date(year, month, d))) { tombeCeMois = true; break; }
    }
    if (tombeCeMois) r.lastGenerated = mKey;
  });

  save(); renderAll();

  if (generated === 0 && alreadyThere === 0) {
    alert('ℹ️ Aucune opération planifiée pour les jours passés de ce mois.');
  } else {
    alert(`✅ ${generated} opération(s) créée(s)` + (alreadyThere ? `, ${alreadyThere} déjà présente(s)` : ''));
  }
}
// ============ COMPTES DE SUIVI ============

// Construit la liste des catégories en deux groupes (Flux planifiés / Autres),
// avec cases à cocher. Utilisée par la fenêtre de création ET la fenêtre de modification.
// - checkedIds : tableau d'ids de catégories à cocher au départ (vide en création, état actuel en modification)
// - containerId : id du div qui reçoit le HTML (par défaut 'accCatCheckboxes')
function renderAccountCatCheckboxes(checkedIds = [], containerId = 'accCatCheckboxes') {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!state.categories.length) {
    el.innerHTML = '<span style="color:#999;">Aucune catégorie</span>';
    return;
  }

  // Pour chaque catégorie, on regarde si elle a au moins un flux planifié
  // et si parmi ces flux, au moins un est actif (non en pause).
  const infoByCat = {};
  state.categories.forEach(c => {
    const fluxes = state.recurring.filter(r => r.categoryId === c.id);
    const hasFlux = fluxes.length > 0;
    const hasActiveFlux = fluxes.some(r => r.active !== false);
    infoByCat[c.id] = { hasFlux, hasActiveFlux };
  });

  const sorted = [...state.categories].sort((a, b) =>
    a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
  );

  const fluxCats = sorted.filter(c => infoByCat[c.id].hasFlux);
  const otherCats = sorted.filter(c => !infoByCat[c.id].hasFlux);

  const renderCheckbox = (c) => {
    const info = infoByCat[c.id];
    // data-paused="1" si la catégorie a des flux mais aucun actif (que des pauses)
    const pausedAttr = (info.hasFlux && !info.hasActiveFlux) ? 'data-paused="1"' : '';
    const checkedAttr = checkedIds.includes(c.id) ? 'checked' : '';
    return `<label><input type="checkbox" value="${c.id}" class="acc-cat-check" ${pausedAttr} ${checkedAttr} onchange="onAccCatCheckChange(this)"> ${c.name}</label>`;
  };

  let html = '';

  if (fluxCats.length) {
    html += `<div style="width:100%;font-size:0.8rem;font-weight:600;color:#16213e;margin:6px 0 4px;">🔁 Flux planifiés</div>`;
    html += fluxCats.map(renderCheckbox).join('');
  }

  if (otherCats.length) {
    html += `<div style="width:100%;font-size:0.8rem;font-weight:600;color:#16213e;margin:12px 0 4px;">📋 Autres catégories</div>`;
    html += otherCats.map(renderCheckbox).join('');
  }

  el.innerHTML = html;
}

// Quand on tente de cocher une catégorie qui n'a que des flux en pause :
// message d'information, et la case reste décochée.
function onAccCatCheckChange(checkbox) {
  if (!checkbox.checked) return; // décocher : rien à faire
  if (checkbox.dataset.paused !== '1') return; // pas en pause → OK
  // Flux en pause : on décoche et on prévient
  checkbox.checked = false;
  alert("Ce flux est en pause.");
}
// Vérifie si une catégorie peut être associée à un compte de type donné.
// Seule règle : un Locataire ne peut pas partager une catégorie avec un autre Locataire.
// Les Regroupements peuvent toujours partager, silencieusement.
// Retourne { ok, blockedBy }.
function checkCategoryAssignable(categoryId, targetType, excludeAccountId = null) {
  if (targetType !== 'tenant') return { ok: true };

  const otherTenant = state.accounts.find(a =>
    a.id !== excludeAccountId
    && a.type === 'tenant'
    && (a.categoryIds || []).includes(categoryId)
  );

  if (otherTenant) return { ok: false, blockedBy: otherTenant };
  return { ok: true };
}
function addAccount() {
  const name = document.getElementById('accName').value.trim();
  const type = document.getElementById('accType').value;
  if (!name) return alert('Donne un nom au compte');
  
  const checkboxes = document.querySelectorAll('.acc-cat-check:checked');
  const categoryIds = Array.from(checkboxes).map(c => c.value);
  if (!categoryIds.length) return alert('Sélectionne au moins une catégorie');

  // --- SEUL BLOCAGE : deux Locataires sur la même catégorie ---
  for (let cid of categoryIds) {
    const check = checkCategoryAssignable(cid, type, null);
    if (!check.ok) {
      const catName = state.categories.find(c => c.id === cid)?.name || 'Inconnue';
      alert(`⛔ Impossible : la catégorie "${catName}" est déjà utilisée par le compte Locataire "${check.blockedBy.name}".\n\nUn compte Locataire ne peut pas partager une catégorie avec un autre Locataire.`);
      const cb = document.querySelector(`.acc-cat-check[value="${cid}"]`);
      if (cb) cb.checked = false;
      return;
    }
  }
  // ------------------------------------------------------------

  state.accounts.push({ id: uid(), name, type, categoryIds });
  document.getElementById('accName').value = '';
  document.querySelectorAll('.acc-cat-check').forEach(c => c.checked = false);
  
  const createContent = document.getElementById('content-accCreate');
  if (createContent) {
    createContent.style.display = 'none';
    document.getElementById('icon-accCreate').textContent = '▼';
  }
  
  save(); renderAll();
}


// Ouvre la fenêtre de modification d'un compte de suivi
function openEditAccountModal(id) {
  const account = state.accounts.find(a => a.id === id);
  if (!account) return;

  // Remplir les champs
  document.getElementById('editAccName').value = account.name;
  document.getElementById('editAccType').value = account.type; // affiché mais grisé

  // Afficher les catégories avec l'état actuel du compte
  renderAccountCatCheckboxes(account.categoryIds || [], 'editAccCatCheckboxes');

  // Mémoriser l'id du compte en cours de modification
  document.getElementById('editAccountModal').dataset.accountId = id;

  // Ouvrir la modale
  document.getElementById('editAccountModal').classList.add('active');
}

// Valide la modification d'un compte de suivi
function saveEditAccount() {
  const modal = document.getElementById('editAccountModal');
  const id = modal.dataset.accountId;
  const account = state.accounts.find(a => a.id === id);
  if (!account) return;

  const name = document.getElementById('editAccName').value.trim();
  if (!name) return alert('Donne un nom au compte');

  const checkboxes = document.querySelectorAll('#editAccCatCheckboxes .acc-cat-check:checked');
  const categoryIds = Array.from(checkboxes).map(c => c.value);
  if (!categoryIds.length) return alert('Sélectionne au moins une catégorie');

  // --- SEUL BLOCAGE : deux Locataires sur la même catégorie ---
  for (let cid of categoryIds) {
    const check = checkCategoryAssignable(cid, account.type, account.id);
    if (!check.ok) {
      const catName = state.categories.find(c => c.id === cid)?.name || 'Inconnue';
      return alert(`⛔ Impossible : la catégorie "${catName}" est déjà utilisée par le compte Locataire "${check.blockedBy.name}".\n\nUn compte Locataire ne peut pas partager une catégorie avec un autre Locataire.`);
    }
  }
  // ------------------------------------------------------------

  // Mise à jour
  account.name = name;
  account.categoryIds = categoryIds;
  // Le type n'est pas modifiable (figé)

  modal.classList.remove('active');
  save();
  renderAll();
}

function deleteAccount(id) {
  const account = state.accounts.find(a => a.id === id);
  if (!account) return;
  const nbPosts = state.accountPosts.filter(p => p.accountId === id).length;
  const msg = `Supprimer le compte de suivi « ${account.name} » ?\n\n` +
    `Cela supprimera aussi ses ${nbPosts} poste(s) saisi(s).\n` +
    `Les transactions bancaires ne sont PAS supprimées.\n\n` +
    `Continuer ?`;
  if (!confirm(msg)) return;

  state.accounts = state.accounts.filter(a => a.id !== id);
  state.accountPosts = state.accountPosts.filter(p => p.accountId !== id);
  // Les logements qui utilisaient ce compte de suivi sont simplement détachés
  state.logements.forEach(l => { if (l.accountId === id) l.accountId = ''; });
  save(); renderAll();
}

// Calcul des montants d'un compte pour un mois donné
function computeAccountMonth(account, mKey) {
  const catIds = account.categoryIds || [];
  // Transactions pointées du mois avec ces catégories
  const txs = state.transactions.filter(t => {
    if (!t.checked) return false;
    if (!catIds.includes(t.categoryId)) return false;
    return t.date.slice(0, 7) === mKey;
  });

  // Mouvements : on prend le signe réel
  const encaisse = txs.filter(t => t.amount > 0).reduce((s, t) => s + t.amount, 0);
  const decaisse = Math.abs(txs.filter(t => t.amount < 0).reduce((s, t) => s + t.amount, 0));

  // Postes saisis manuellement (attendu)
  const posts = state.accountPosts.filter(p => p.accountId === account.id && p.month === mKey);
  const totalPostes = posts.reduce((s, p) => s + p.amount, 0);

  // Report = ce qui restait dû à la fin du mois précédent
  // = (total des postes des mois passés) - (total des transactions pointées des mois passés)
  // Positif : le locataire doit encore cet argent. Négatif : il a trop versé.
  let report = 0;
  state.accountPosts
    .filter(p => p.accountId === account.id && p.month < mKey)
    .forEach(p => { report += p.amount; });
  state.transactions
    .filter(t => t.checked && catIds.includes(t.categoryId) && t.date.slice(0, 7) < mKey)
    .forEach(t => { report -= t.amount; });

  const totalAttendu = report + totalPostes;     // ce qu'il faut recevoir ce mois (report compris)
  const totalEncaisse = encaisse - decaisse;
  // CORRECTION v3 : avant, le report était compté deux fois dans le cumul.
  const difference = totalEncaisse - totalPostes;  // le mois seul
  const cumulTotal = totalEncaisse - totalAttendu; // tout compris : >0 trop-perçu, <0 reste à percevoir

  return { posts, totalPostes, report, totalAttendu, encaisse, decaisse, totalEncaisse, difference, cumulTotal, txs };
}

function renderAccounts() {
  renderAccountCatCheckboxes();
  const el = document.getElementById('accountsList');
  if (!el) return;
  if (!state.accounts.length) {
    el.innerHTML = '<div class="empty">Aucun compte de suivi. Crée-en un ci-dessus.</div>';
    return;
  }
  const now = new Date();
  const defaultMonth = monthKey(now);

  // Initialiser le mois par défaut pour chaque compte
  state.accounts.forEach(a => {
    if (!accountMonthsView[a.id]) accountMonthsView[a.id] = defaultMonth;
  });

  el.innerHTML = state.accounts.map(a => {
    const mKey = accountMonthsView[a.id];
    const data = computeAccountMonth(a, mKey);
    const isTenant = a.type === 'tenant';
    const cls = isTenant ? 'tenant' : 'group';
    const cats = (a.categoryIds || []).map(cid => state.categories.find(c => c.id === cid)).filter(Boolean);
    const catsLabel = cats.map(c => c.name).join(' · ');

    const cumulClass = data.cumulTotal > 0.005 ? 'pos' : data.cumulTotal < -0.005 ? 'neg' : 'zero';
    const cumulLabel = data.cumulTotal > 0.005 ? 'Trop-perçu cumulé' : data.cumulTotal < -0.005 ? 'À percevoir cumulé' : 'À jour';

    return `<div class="account-card ${cls}" style="padding:0; overflow:hidden; margin-bottom:15px;">
      <div class="accordion-header" style="padding:18px; border-bottom:none; margin-bottom:0;" onclick="toggleAccount('${a.id}')">
        <div style="display:flex; flex-direction:column; gap:6px; flex:1;">
          <div class="account-card-title">${isTenant ? '👤' : '📊'} ${a.name}</div>
          <div class="account-card-cats" style="margin-bottom:0;">${catsLabel || 'Aucune catégorie'}</div>
        </div>
        <div style="display:flex; align-items:center; gap:15px;">
          <div class="account-cumul ${cumulClass}" style="margin-top:0; padding:6px 12px; font-size:0.85rem; border-radius:6px;">
            ${cumulLabel} : <strong>${fmt(data.cumulTotal)}</strong>
          </div>
          <span class="accordion-icon" id="icon-acc-${a.id}">${openAccounts.includes(a.id) ? '▲' : '▼'}</span>
        </div>
      </div>
      
      <div class="accordion-content" id="content-acc-${a.id}" style="display:${openAccounts.includes(a.id) ? 'block' : 'none'}; padding:18px; padding-top:0; background:#f9fafb; border-top:1px solid #eee;">
        ${renderAccountDetailHTML(a, mKey)}
      </div>
    </div>`;
  }).join('');
}

// Coche / décoche un poste de l'attendu (fige / défige la ligne)
function toggleAccountPostChecked(postId) {
  const p = state.accountPosts.find(x => x.id === postId);
  if (!p) return;
  p.checked = !p.checked;
  save();
  renderAll();
}
// Ouvre la fenêtre de modification d'un poste de l'attendu
function openEditAccountPostModal(postId) {
  const p = state.accountPosts.find(x => x.id === postId);
  if (!p) return;
  if (p.checked) return; // sécurité : on ne modifie pas un poste figé

  document.getElementById('editAccountPostModal').dataset.postId = postId;
  document.getElementById('editPostLabel').value = p.label;
  document.getElementById('editPostAmount').value = p.amount;
  document.getElementById('editAccountPostModal').classList.add('active');
}

function closeEditAccountPostModal() {
  document.getElementById('editAccountPostModal').classList.remove('active');
}

function saveEditAccountPost() {
  const modal = document.getElementById('editAccountPostModal');
  const postId = modal.dataset.postId;
  const p = state.accountPosts.find(x => x.id === postId);
  if (!p) return;
  if (p.checked) { closeEditAccountPostModal(); return; } // sécurité

  const label = document.getElementById('editPostLabel').value.trim();
  const amount = parseFloat(document.getElementById('editPostAmount').value);

  if (!label) return alert('Saisis un libellé');
  if (isNaN(amount)) return alert('Montant invalide');

  p.label = label;
  p.amount = amount;

  closeEditAccountPostModal();
  save();
  renderAll();
}

function renderAccountDetailHTML(account, mKey) {
  const data = computeAccountMonth(account, mKey);
  const isTenant = account.type === 'tenant';
  let html = '';

if (isTenant) {
  html += `
    <div class="account-block" style="background:white;">
      <h3>📋 Attendu (relevé du mois)</h3>
      <div class="account-nav" style="margin:10px 0;">
        <button onclick="navigateAccountMonth('${account.id}', -1)">◀</button>
        <div class="period">${monthKeyLabel(mKey)}</div>
        <button onclick="navigateAccountMonth('${account.id}', 1)">▶</button>
      </div>
      <div class="post-row report-line">
        <span class="post-label">Report du mois précédent (auto)</span>
        <span class="post-amount ${data.report > 0.005 ? 'amount-neg' : 'amount-pos'}">${fmt(data.report)}</span>
        <span class="post-actions"></span>
      </div>
      ${data.posts.map(p => `
        <div class="post-row">
          <span class="check ${p.checked ? 'done' : 'todo'}" onclick="toggleAccountPostChecked('${p.id}')">${p.checked ? '✅' : '⬜'}</span>
          <span class="post-label">${p.label}</span>
          <span class="post-amount ${p.amount >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(p.amount)}</span>
          <span class="post-actions">
            ${p.checked ? '' : `<button class="primary" onclick="openEditAccountPostModal('${p.id}')" style="padding:4px 8px; font-size:0.75rem;">✏️</button>
            <button class="danger" onclick="deleteAccountPost('${p.id}')">✕</button>`}
          </span>
        </div>
      `).join('')}
      <div style="margin-top:12px;">
        <button class="primary" onclick="openAccountPostModal('${account.id}', '${mKey}')">➕ Ajouter un poste</button>
      </div>
      <div class="account-total-row">
        <span>TOTAL ATTENDU (avec report)</span>
        <span class="${data.totalAttendu >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(data.totalAttendu)}</span>
      </div>
    </div>
  `;
} else {
  html += `
    <div class="account-nav" style="margin:10px 0;">
      <button onclick="navigateAccountMonth('${account.id}', -1)">◀</button>
      <div class="period">${monthKeyLabel(mKey)}</div>
      <button onclick="navigateAccountMonth('${account.id}', 1)">▶</button>
    </div>
  `;
}

  html += `
    <div class="account-block" style="background:white; margin-top:15px;">
      <h3>💳 ${isTenant ? 'Encaissé (pointé)' : 'Mouvements (pointés)'}</h3>
      ${data.txs.length ? data.txs.map(t => {
        const cat = state.categories.find(c => c.id === t.categoryId);
        return `<div class="encaisse-row">
          <span>✅ ${new Date(t.date).toLocaleDateString('fr-FR')}</span>
          <span>${t.label}</span>
          <span style="color:#666;font-size:0.8rem;">${cat ? cat.name : ''}</span>
          <strong class="${t.amount >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(t.amount)}</strong>
        </div>`;
      }).join('') : '<div class="empty" style="padding:15px;">Aucune transaction pointée ce mois</div>'}
      <div style="margin-top:12px;">
        <button class="success" onclick="checkAllAccountMonth('${account.id}', '${mKey}')">✅ Tout pointer ce mois</button>
      </div>
      <div class="account-total-row">
        <span>${isTenant ? 'TOTAL ENCAISSÉ (pointé)' : 'SOLDE DU MOIS'}</span>
        <span class="${(isTenant ? data.encaisse : data.totalEncaisse) >= 0 ? 'amount-pos' : 'amount-neg'}">${fmt(isTenant ? data.encaisse : data.totalEncaisse)}</span>
      </div>
    </div>

    <div class="account-diff-block ${data.difference > 0.005 ? 'pos' : data.difference < -0.005 ? 'neg' : 'zero'}" style="margin-top:15px;">
      <span>${isTenant ? 'Différence du mois' : 'Solde du mois'}</span>
      <span>${fmt(data.difference)}</span>
    </div>
    
      <div class="account-cumul-block ${data.cumulTotal > 0.005 ? 'pos' : data.cumulTotal < -0.005 ? 'neg' : 'zero'}" style="margin-top:10px;">
    <span>${data.cumulTotal > 0.005 ? '🟢 Trop-perçu cumulé' : data.cumulTotal < -0.005 ? '🔴 À percevoir cumulé' : '✅ À jour (cumul)'}</span>
    <span>${fmt(data.cumulTotal)}</span>
  </div>

  <div style="margin-top:20px; display:flex; justify-content:flex-end; gap:10px; padding-top:15px; border-top:1px solid #eee;">
    <button class="primary" style="padding:8px 14px;" onclick="openEditAccountModal('${account.id}')">✏️ Modifier</button>
    <button class="danger" style="padding:8px 14px;" onclick="deleteAccount('${account.id}')">🗑️ Supprimer</button>
  </div>
`;
return html;
}

function toggleAccount(id) {
  const content = document.getElementById('content-acc-' + id);
  const icon = document.getElementById('icon-acc-' + id);
  if (!content || !icon) return;

  const isOpen = content.style.display !== 'none';
  if (isOpen) {
    // On ferme
    content.style.display = 'none';
    icon.textContent = '▼';
    openAccounts = openAccounts.filter(x => x !== id);
  } else {
    // On ouvre
    content.style.display = 'block';
    icon.textContent = '▲';
    if (!openAccounts.includes(id)) openAccounts.push(id);
  }
}

let accountMonthsView = {}; 

function navigateAccountMonth(accountId, delta) {
  if (!accountMonthsView[accountId]) {
    accountMonthsView[accountId] = monthKey(new Date());
  }
  accountMonthsView[accountId] = addMonths(accountMonthsView[accountId], delta);
  save(); renderAll();
}

function checkAllAccountMonth(accountId, mKey) {
  const account = state.accounts.find(a => a.id === accountId);
  if (!account) return;

  // On force le mois affiché à celui transmis
  accountMonthsView[accountId] = mKey;

  const catIds = account.categoryIds || [];
  let countTx = 0;
  let countPosts = 0;

  // 1) Pointer les transactions bancaires non pointées de ce mois
  state.transactions.forEach(t => {
    if (t.checked) return;
    if (!catIds.includes(t.categoryId)) return;
    if (t.date.slice(0, 7) !== mKey) return;
    t.checked = true;
    countTx++;
  });

  // 2) Cocher tous les postes de l'attendu de ce mois
  state.accountPosts.forEach(p => {
    if (p.accountId !== accountId) return;
    if (p.month !== mKey) return;
    if (p.checked) return;
    p.checked = true;
    countPosts++;
  });

  save();
  renderAll();

  const messages = [];
  if (countTx > 0) messages.push(`${countTx} transaction(s) pointée(s)`);
  if (countPosts > 0) messages.push(`${countPosts} poste(s) figé(s)`);
  if (!messages.length) messages.push('Rien à pointer');
  alert(`✅ ${messages.join(' + ')} pour ${monthKeyLabel(mKey)}`);
}

function openAccountPostModal(accountId, mKey) {
  const account = state.accounts.find(a => a.id === accountId);
  if (!account) return;

  const sel = document.getElementById('postLine');
  const cats = (account.categoryIds || [])
    .map(cid => state.categories.find(c => c.id === cid))
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' }));

  const recs = state.recurring.filter(r =>
    r.active !== false && (account.categoryIds || []).includes(r.categoryId)
  );

  let opts = '<option value="">-- Choisir une ligne --</option>';
  if (recs.length) {
    opts += '<optgroup label="Flux planifiés">';
    recs.forEach(r => {
        const catDuFlux = state.categories.find(c => c.id === r.categoryId);
  const nomCat = catDuFlux ? catDuFlux.name : 'Sans catégorie';
  opts += `<option value="rec:${r.id}" data-amount="${r.type === 'income' ? r.amount : -r.amount}" data-label="${r.label}">${nomCat} — ${r.label} (${fmt(r.type === 'income' ? r.amount : -r.amount)})</option>`;
});
    opts += '</optgroup>';
  }
  if (cats.length) {
    opts += '<optgroup label="Catégories">';
    cats.forEach(c => {
      opts += `<option value="cat:${c.id}" data-label="${c.name}">${c.name} (montant à saisir)</option>`;
    });
    opts += '</optgroup>';
  }
  opts += '<optgroup label="Autre"><option value="libre">✏️ Libre (saisie manuelle)</option></optgroup>';
  sel.innerHTML = opts;

  document.getElementById('postModalPeriod').textContent = monthKeyLabel(mKey);
  document.getElementById('postAmount').value = '';
  document.getElementById('postLibreLabel').value = '';
  document.getElementById('postLibreLabelWrapper').style.display = 'none';
  
  // On stocke temporairement l'ID du compte et le mois
  document.getElementById('postAmount').dataset.accountId = accountId;
  document.getElementById('postAmount').dataset.month = mKey;
  
  document.getElementById('accountPostModal').classList.add('active');
}

function closeAccountPostModal() {
  document.getElementById('accountPostModal').classList.remove('active');
}

function updatePostLineForm() {
  const val = document.getElementById('postLine').value;
  const amountInput = document.getElementById('postAmount');
  const libreWrapper = document.getElementById('postLibreLabelWrapper');

  if (val.startsWith('rec:')) {
    const opt = document.getElementById('postLine').selectedOptions[0];
    amountInput.value = Math.abs(parseFloat(opt.dataset.amount) || 0);
    libreWrapper.style.display = 'none';
  } else if (val.startsWith('cat:')) {
    amountInput.value = '';
    libreWrapper.style.display = 'none';
    amountInput.focus();
  } else if (val === 'libre') {
    amountInput.value = '';
    libreWrapper.style.display = 'block';
  } else {
    amountInput.value = '';
    libreWrapper.style.display = 'none';
  }
}

function saveAccountPost() {
  const accountId = document.getElementById('postAmount').dataset.accountId;
  const mKey = document.getElementById('postAmount').dataset.month;
  const account = state.accounts.find(a => a.id === accountId);
  if (!account) return;
  
  const val = document.getElementById('postLine').value;
  const amount = parseFloat(document.getElementById('postAmount').value);

  if (!val) return alert('Choisis une ligne');
  if (isNaN(amount)) return alert('Montant invalide');

  let label = '';
  if (val.startsWith('rec:')) {
    const rec = state.recurring.find(r => r.id === val.slice(4));
if (!rec) return;
const catDuFlux = state.categories.find(c => c.id === rec.categoryId);
label = catDuFlux ? catDuFlux.name : rec.label;
  } else if (val.startsWith('cat:')) {
    const cat = state.categories.find(c => c.id === val.slice(4));
    if (!cat) return;
    label = cat.name;
  } else if (val === 'libre') {
    label = document.getElementById('postLibreLabel').value.trim();
    if (!label) return alert('Saisis un libellé');
  }

  state.accountPosts.push({
    id: uid(), accountId: account.id, month: mKey, label, amount
  });

  closeAccountPostModal();
  save(); renderAll();
}

function deleteAccountPost(postId) {
  const p = state.accountPosts.find(x => x.id === postId);
  if (!p) return;
  if (p.checked) return alert("⛔ Ce poste est figé. Décoche-le d'abord pour pouvoir le supprimer.");
  if (!confirm('Supprimer ce poste ?')) return;
  state.accountPosts = state.accountPosts.filter(x => x.id !== postId);
  save(); renderAll();
}
// ============ DASHBOARD ============
let catChart, monthChart, forecastChart;
let openAccounts = []; // ids des comptes de suivi actuellement ouverts (mémoire uniquement)
function renderDashboard() {
  const now = new Date();
  const monthTxs = state.transactions.filter(t => {
    const d = new Date(t.date);
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear() && !t.transferId;
  });
  const income = monthTxs.filter(t => t.amount > 0).reduce((s, t) => s + t.amount, 0);
  const expense = Math.abs(monthTxs.filter(t => t.amount < 0).reduce((s, t) => s + t.amount, 0));
  const totalBalance = state.banks.reduce((s, b) =>
    s + b.balance + state.transactions.filter(t => t.bankId === b.id).reduce((x, t) => x + t.amount, 0), 0);
  const uncheckedTxs = state.transactions.filter(t => !t.checked);
  const uncheckedTotal = uncheckedTxs.reduce((s, t) => s + t.amount, 0);
  document.getElementById('kpis').innerHTML = `
    <div class="kpi"><div class="kpi-label">Solde total</div><div class="kpi-value">${fmt(totalBalance)}</div></div>
    <div class="kpi green"><div class="kpi-label">Revenus du mois</div><div class="kpi-value">${fmt(income)}</div></div>
    <div class="kpi red"><div class="kpi-label">Dépenses du mois</div><div class="kpi-value">${fmt(expense)}</div></div>
    <div class="kpi orange"><div class="kpi-label">Épargne du mois</div><div class="kpi-value">${fmt(income - expense)}</div></div>
    <div class="kpi ${uncheckedTxs.length ? 'gray' : 'green'}">
      <div class="kpi-label">À pointer</div>
      <div class="kpi-value">${uncheckedTxs.length} tx</div>
      <div class="kpi-sub">${fmt(uncheckedTotal)} au total</div>
    </div>
  `;

  // Nouveau graphique : dépenses par catégorie et par mois
  renderCatMonthChart();

  // Ancien graphique mensuel (conservé)
  const months = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(); d.setMonth(d.getMonth() - i);
    months.push({ key: `${d.getFullYear()}-${d.getMonth()}`, label: d.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }) });
  }
  const incomeSeries = months.map(m => state.transactions.filter(t => {
    const d = new Date(t.date);
    return `${d.getFullYear()}-${d.getMonth()}` === m.key && t.amount > 0 && !t.transferId;
  }).reduce((s, t) => s + t.amount, 0));
  const expenseSeries = months.map(m => Math.abs(state.transactions.filter(t => {
    const d = new Date(t.date);
    return `${d.getFullYear()}-${d.getMonth()}` === m.key && t.amount < 0 && !t.transferId;
  }).reduce((s, t) => s + t.amount, 0)));
  if (monthChart) monthChart.destroy();
  monthChart = new Chart(document.getElementById('monthChart'), {
    type: 'bar',
    data: {
      labels: months.map(m => m.label),
      datasets: [
        { label: 'Revenus', data: incomeSeries, backgroundColor: '#10b981' },
        { label: 'Dépenses', data: expenseSeries, backgroundColor: '#ef4444' }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
  });
}

// ============ GRAPHIQUE DÉPENSES PAR CATÉGORIE ET PAR MOIS ============

let catMonthChart = null;
let catChartPeriodMode = '12m';          // '3m' | '6m' | '12m' | 'custom'
let catChartCustomFrom = null;           // 'YYYY-MM'
let catChartCustomTo = null;             // 'YYYY-MM'
let catChartSelectedCats = [];           // ids des catégories cochées

// Retourne { fromKey, toKey } selon le mode actif
function getCatChartPeriodRange() {
  const now = new Date();
  if (catChartPeriodMode === 'custom' && catChartCustomFrom && catChartCustomTo) {
    return { fromKey: catChartCustomFrom, toKey: catChartCustomTo };
  }
  const nbMonths = catChartPeriodMode === '3m' ? 3 : catChartPeriodMode === '6m' ? 6 : 12;
  const toKey = monthKey(now);
  const fromDate = new Date(now.getFullYear(), now.getMonth() - (nbMonths - 1), 1);
  return { fromKey: monthKey(fromDate), toKey };
}

// Liste tous les mois entre fromKey et toKey inclus (ordre croissant)
function listMonthsBetween(fromKey, toKey) {
  const result = [];
  let cur = fromKey;
  let safety = 240; // garde-fou
  while (cur <= toKey && safety-- > 0) {
    result.push(cur);
    cur = addMonths(cur, 1);
  }
  return result;
}

// Change le mode de période (boutons rapides)
function setCatChartPeriod(mode) {
  catChartPeriodMode = mode;
  const isCustom = mode === 'custom';
  const customEl = document.getElementById('catCustomPeriod');
  if (customEl) customEl.style.display = isCustom ? 'flex' : 'none';

  // Style visuel des boutons
  ['3m', '6m', '12m', 'custom'].forEach(m => {
    const btn = document.getElementById('catBtn' + (m === '3m' ? '3m' : m === '6m' ? '6m' : m === '12m' ? '12m' : 'Custom'));
    if (btn) btn.style.opacity = (m === mode) ? '1' : '0.6';
  });

  if (isCustom) {
    // Pré-remplir les menus si vides
    const selFrom = document.getElementById('catPeriodFrom');
    const selTo = document.getElementById('catPeriodTo');
    const now = new Date();
    if (selFrom && selFrom.options.length === 0) {
      const opts = [];
      for (let i = 23; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        opts.push(monthKey(d));
      }
      selFrom.innerHTML = opts.map(k => `<option value="${k}">${monthKeyLabel(k)}</option>`).join('');
      selTo.innerHTML = opts.map(k => `<option value="${k}">${monthKeyLabel(k)}</option>`).join('');
      selFrom.value = opts[Math.max(0, opts.length - 6)];
      selTo.value = opts[opts.length - 1];
    }
    if (!catChartCustomFrom) catChartCustomFrom = selFrom?.value || null;
    if (!catChartCustomTo) catChartCustomTo = selTo?.value || null;
  }

  renderCatMonthChart();
}

// Applique la période personnalisée choisie dans les deux menus
function applyCatChartCustomPeriod() {
  const from = document.getElementById('catPeriodFrom')?.value;
  const to = document.getElementById('catPeriodTo')?.value;
  if (!from || !to) return alert('Choisis une période');
  if (from > to) return alert('La date de début doit être avant la date de fin');
  catChartCustomFrom = from;
  catChartCustomTo = to;
  catChartPeriodMode = 'custom';
  renderCatMonthChart();
}

// Coche / décoche une catégorie
function toggleCatChartCategory(catId) {
  if (catChartSelectedCats.includes(catId)) {
    catChartSelectedCats = catChartSelectedCats.filter(id => id !== catId);
  } else {
    catChartSelectedCats.push(catId);
  }
  renderCatMonthChart();
}

// Tout cocher / tout décocher
function toggleAllCatChartCategories() {
  const allIds = getCatChartAvailableCategories();
  if (catChartSelectedCats.length >= allIds.length) {
    catChartSelectedCats = [];
  } else {
    catChartSelectedCats = [...allIds];
  }
  renderCatMonthChart();
}

// Retourne les ids des catégories ayant au moins une dépense réelle sur la période
function getCatChartAvailableCategories() {
  const { fromKey, toKey } = getCatChartPeriodRange();
  const result = [];
  const seen = new Set();
  state.transactions.forEach(t => {
    if (t.amount >= 0) return;
    if (t.transferId) return;
    if (!t.categoryId) return;
    const mk = t.date.slice(0, 7);
    if (mk < fromKey || mk > toKey) return;
    if (seen.has(t.categoryId)) return;
    seen.add(t.categoryId);
    result.push(t.categoryId);
  });
  // Tri alphabétique
  return result.sort((a, b) => {
    const ca = state.categories.find(c => c.id === a);
    const cb = state.categories.find(c => c.id === b);
    return (ca?.name || '').localeCompare(cb?.name || '', 'fr', { sensitivity: 'base' });
  });
}

// Génère le graphique et les cases à cocher
function renderCatMonthChart() {
  const wrapper = document.getElementById('catChartCategories');
  const emptyEl = document.getElementById('catChartEmpty');
  const canvas = document.getElementById('catMonthChart');
  if (!wrapper || !canvas) return;

  // 1) Catégories disponibles sur la période
  const available = getCatChartAvailableCategories();

  // Au premier rendu, tout cocher
  if (catChartSelectedCats.length === 0 && available.length > 0) {
    catChartSelectedCats = [...available];
  }
  // Retirer de la sélection les catégories qui ne sont plus disponibles
  catChartSelectedCats = catChartSelectedCats.filter(id => available.includes(id));

  // 2) Mettre à jour le bouton "Tout cocher / décocher"
  const toggleBtn = document.getElementById('catToggleAllBtn');
  if (toggleBtn) {
    toggleBtn.textContent = (catChartSelectedCats.length >= available.length && available.length > 0)
      ? 'Tout décocher'
      : 'Tout cocher';
  }

  // 3) Afficher les cases à cocher
  if (available.length === 0) {
    wrapper.innerHTML = '<span style="color:#999;">Aucune catégorie avec dépenses sur la période.</span>';
  } else {
    wrapper.innerHTML = available.map(id => {
      const cat = state.categories.find(c => c.id === id);
      const checked = catChartSelectedCats.includes(id) ? 'checked' : '';
      return `<label><input type="checkbox" value="${id}" ${checked} onchange="toggleCatChartCategory('${id}')"> ${cat?.name || '?'}</label>`;
    }).join('');
  }

  // 4) Construire le graphique
  const { fromKey, toKey } = getCatChartPeriodRange();
  const months = listMonthsBetween(fromKey, toKey);

  if (months.length === 0 || catChartSelectedCats.length === 0) {
    if (catMonthChart) { catMonthChart.destroy(); catMonthChart = null; }
    emptyEl.style.display = 'block';
    canvas.style.display = 'none';
    return;
  }

  emptyEl.style.display = 'none';
  canvas.style.display = 'block';

  // NOUVEAU SENS :
  // - Une barre = une CATÉGORIE (labels)
  // - Un segment = un MOIS (datasets)
  // - Barres VERTICALES empilées
  const datasets = months.map(mk => {
    const data = catChartSelectedCats.map(catId => {
      return state.transactions
        .filter(t => t.amount < 0 && !t.transferId && t.categoryId === catId && t.date.slice(0, 7) === mk)
        .reduce((s, t) => s + Math.abs(t.amount), 0);
    });
    // Couleur par mois : on alterne des teintes pour distinguer les segments
    const palette = ['#667eea','#11998e','#f7971e','#eb3349','#8b5cf6','#06b6d4','#ec4899','#84cc16','#f59e0b','#14b8a6','#a855f7','#ef4444'];
    const idx = months.indexOf(mk);
    return {
      label: monthKeyLabel(mk),
      data,
      backgroundColor: palette[idx % palette.length]
    };
  });

  if (catMonthChart) catMonthChart.destroy();

  // Plugin pour écrire les montants dans les segments
  const labelsInBarsPlugin = {
    id: 'labelsInBars',
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      ctx.save();
      ctx.font = 'bold 11px sans-serif';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      chart.data.datasets.forEach((dataset, di) => {
        const meta = chart.getDatasetMeta(di);
        meta.data.forEach((bar, i) => {
          const value = dataset.data[i];
          if (!value || value < 1) return;
          const props = bar.getProps(['x', 'y', 'base', 'width', 'height'], true);
          // Barre verticale : centre horizontal = x, centre vertical = (y + base) / 2
          const cx = props.x;
          const cy = (props.y + props.base) / 2;
          ctx.fillText(value.toFixed(0) + ' €', cx, cy);
        });
      });
      ctx.restore();
    }
  };

  catMonthChart = new Chart(canvas, {
    type: 'bar',
    data: {
      // En bas : les CATÉGORIES
      labels: catChartSelectedCats.map(id => state.categories.find(c => c.id === id)?.name || '?'),
      datasets
    },
    options: {
      // Barres VERTICALES (on ne met PAS indexAxis: 'y')
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
      },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label} : ${fmt(ctx.parsed.y)}`
          }
        }
      }
    },
    plugins: [labelsInBarsPlugin]
  });
}

// ============ PRÉVISIONNEL ============
function saveForecastParams() {
  state.forecastParams = {
    revGrowth: parseFloat(fcRevGrowth.value) || 0,
    inflation: parseFloat(fcInflation.value) || 0,
    yield: parseFloat(fcYield.value) || 0,
    variable: parseFloat(fcVariable.value) || 0
  };
  save();
}

function loadForecastParams() {
  fcRevGrowth.value = state.forecastParams.revGrowth;
  fcInflation.value = state.forecastParams.inflation;
  fcYield.value = state.forecastParams.yield;
  fcVariable.value = state.forecastParams.variable;
}
function renderForecast() {
  const baseBalance = state.banks.reduce((s, b) =>
    s + b.balance + state.transactions.filter(t => t.bankId === b.id).reduce((x, t) => x + t.amount, 0), 0);
  const p = state.forecastParams;
  let balance = baseBalance;
  const labels = [], balances = [], yearlyData = [];
  const startDate = new Date();

  const currentYear = startDate.getFullYear();
  let currentYearTracker = currentYear;
  let yearIncomeTemp = 0, yearExpenseTemp = 0;

  for (let m = 0; m < 36; m++) {
    const monthDate = new Date(startDate.getFullYear(), startDate.getMonth() + m, 1);
    const yearsElapsed = m / 12;
    let monthIncome = 0, monthExpense = 0;

    state.recurring.forEach(r => {
      if (r.active === false) return;
      const start = new Date(r.start);
      const startMonth = new Date(start.getFullYear(), start.getMonth(), 1);
      if (monthDate < startMonth) return;
      if (r.end) {
        const end = new Date(r.end);
        const endMonth = new Date(end.getFullYear(), end.getMonth(), 1);
        if (monthDate > endMonth) return;
      }
      const baseAmount = toMonthly(r.amount, r.freq);
      const adjusted = r.type === 'income'
        ? baseAmount * Math.pow(1 + p.revGrowth / 100, yearsElapsed)
        : baseAmount * Math.pow(1 + p.inflation / 100, yearsElapsed);
      if (r.type === 'income') monthIncome += adjusted;
      else monthExpense += adjusted;
    });

    monthExpense += p.variable;
    const savings = monthIncome - monthExpense;
    balance = balance * (1 + p.yield / 100 / 12) + savings;

    const d = new Date(startDate); d.setMonth(d.getMonth() + m);
    labels.push(d.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }));
    balances.push(balance);

    const currentYearOfMonth = d.getFullYear();
    if (currentYearOfMonth !== currentYearTracker) {
      yearlyData.push({
        year: currentYearTracker,
        income: yearIncomeTemp,
        expense: yearExpenseTemp,
        savings: yearIncomeTemp - yearExpenseTemp,
        endBalance: balances[balances.length - 2] || baseBalance
      });
      currentYearTracker = currentYearOfMonth;
      yearIncomeTemp = 0;
      yearExpenseTemp = 0;
    }
    yearIncomeTemp += monthIncome;
    yearExpenseTemp += monthExpense;
  }
  yearlyData.push({
    year: currentYearTracker,
    income: yearIncomeTemp,
    expense: yearExpenseTemp,
    savings: yearIncomeTemp - yearExpenseTemp,
    endBalance: balances[balances.length - 1]
  });

  const now = new Date();
  const currentMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  let currentIncome = 0, currentExpense = 0;
  state.recurring.forEach(r => {
    if (r.active === false) return;
    const start = new Date(r.start);
    const startMonth = new Date(start.getFullYear(), start.getMonth(), 1);
    if (currentMonth < startMonth) return;
    if (r.end) {
      const end = new Date(r.end);
      const endMonth = new Date(end.getFullYear(), end.getMonth(), 1);
      if (currentMonth > endMonth) return;
    }
    const baseAmount = toMonthly(r.amount, r.freq);
    if (r.type === 'income') currentIncome += baseAmount;
    else currentExpense += baseAmount;
  });
  currentExpense += p.variable;
  const monthlySavings = currentIncome - currentExpense;
  const endBalance36 = balances[35];

  document.getElementById('forecastKpis').innerHTML = `
    <div class="kpi ${monthlySavings >= 0 ? 'green' : 'red'}"><div class="kpi-label">Épargne mensuelle (mois en cours)</div><div class="kpi-value">${fmt(monthlySavings)}</div></div>
    <div class="kpi"><div class="kpi-label">Solde dans 3 ans</div><div class="kpi-value">${fmt(endBalance36)}</div></div>
    <div class="kpi orange"><div class="kpi-label">Recettes récurrentes / mois</div><div class="kpi-value">${fmt(currentIncome)}</div></div>
    <div class="kpi red"><div class="kpi-label">Dépenses récurrentes / mois</div><div class="kpi-value">${fmt(currentExpense)}</div></div>
  `;

  if (forecastChart) forecastChart.destroy();
  forecastChart = new Chart(document.getElementById('forecastChart'), {
    type: 'line',
    data: { labels, datasets: [{ label: 'Solde projeté', data: balances, borderColor: '#667eea', backgroundColor: 'rgba(102,126,234,0.1)', fill: true, tension: 0.3, pointRadius: 2 }] },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: false } },
      plugins: { tooltip: { callbacks: { label: ctx => 'Solde : ' + fmt(ctx.parsed.y) } } } }
  });

  if (!yearlyData.length) {
    document.getElementById('forecastTable').innerHTML = '<div class="empty">Ajoute des flux récurrents</div>';
  } else {
    document.getElementById('forecastTable').innerHTML = `<table><thead><tr>
      <th>Année</th><th>Revenus</th><th>Dépenses</th><th>Épargne</th><th>Solde fin</th>
    </tr></thead><tbody>${yearlyData.map(y => `<tr>
      <td><strong>${y.year}</strong></td>
      <td class="amount-pos">${fmt(y.income)}</td>
      <td class="amount-neg">${fmt(y.expense)}</td>
      <td>${fmt(y.savings)}</td>
      <td><strong>${fmt(y.endBalance)}</strong></td>
    </tr>`).join('')}</tbody></table>`;
  }
}

// ============ EXPORT / IMPORT / RESET ============
function exportData() {
  const dataStr = JSON.stringify(state, null, 2);
  const blob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const date = new Date().toISOString().slice(0, 10);
  a.href = url;
  a.download = `mon-budget-${date}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  alert('✅ Sauvegarde téléchargée !');
}

function importData() {
  const fileInput = document.getElementById('importFile');
  const file = fileInput.files[0];
  if (!file) return alert("Sélectionne d'abord un fichier .json");
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const imported = JSON.parse(e.target.result);
      if (!confirm('⚠️ Cela va REMPLACER toutes tes données actuelles.\n\nContinuer ?')) return;
      state = { ...state, ...imported };
      migrate();
      save();
      fileInput.value = '';
      renderAll();
      alert('✅ Données importées !');
    } catch (err) {
      alert('❌ Fichier invalide : ' + err.message);
    }
  };
  reader.readAsText(file);
}

function resetAll() {
  if (!confirm('⚠️ Effacer TOUTES les données ?')) return;
  if (!confirm('Vraiment sûr ? Action irréversible.')) return;
  localStorage.removeItem('budgetApp');
  location.reload();
}

// ============================================================
// ============ LOCATIF (logements, compteurs, charges) ========
// ============================================================
// Principe : on ne recopie RIEN de la banque.
//  - Les règlements des locataires = les transactions bancaires pointées
//    qui ont la catégorie du logement (via son compte de suivi).
//  - Ce module calcule seulement ce qui est DÛ (loyer, ordures ménagères,
//    charges d'après les relevés de compteurs) et l'envoie dans l'« attendu »
//    du compte de suivi. Le solde et le cumul restent calculés par le compte de suivi.

let locatifSection = 'apercu';            // onglet affiché dans la page Locatif
let locatifMonth = monthKey(new Date());  // mois choisi (YYYY-MM)
let avisLogementId = '';                  // logement affiché dans l'onglet « Avis »

// ---------- petits outils ----------
const esc = s => String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, ch =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
const round2 = n => Math.round((n + Number.EPSILON) * 100) / 100;
const num = v => { const x = parseFloat(String(v === undefined || v === null ? '' : v).replace(',', '.')); return isNaN(x) ? 0 : x; };
const nf = (n, d = 2) => new Intl.NumberFormat('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d }).format(n || 0);
const lastDayOfMonth = key => { const [y, m] = key.split('-').map(Number); return new Date(y, m, 0).getDate(); };
const frDate = iso => iso ? new Date(iso + (iso.length === 10 ? 'T00:00:00' : '')).toLocaleDateString('fr-FR') : '';

function logementsActifs() { return state.logements.filter(l => l.actif !== false); }
function getLogement(id) { return state.logements.find(l => l.id === id); }
function getCompte(id) { return state.accounts.find(a => a.id === id); }

// Valeur d'un historique [{from, montant}] à un mois donné (loyer, ordures ménagères)
function valeurAuMois(hist, month) {
  const list = [...(hist || [])].sort((a, b) => a.from.localeCompare(b.from));
  let cur = null;
  list.forEach(h => { if (h.from <= month) cur = h; });
  return cur ? num(cur.montant) : (list[0] ? num(list[0].montant) : 0);
}

// Tarifs en vigueur pour un mois (le plus récent dont la date de début est passée)
const TARIF_VIDE = { from: '2000-01', eau: 0, eauAbo: 0, hc: 0, hp: 0, moyen: 0, tcfe: 0, elecAbo: 0 };
function tarifPour(month) {
  const list = [...state.tarifs].sort((a, b) => a.from.localeCompare(b.from));
  let cur = null;
  list.forEach(t => { if (t.from <= month) cur = t; });
  return cur || list[0] || TARIF_VIDE;
}

// ---------- relevés de compteurs ----------
function releve(cid, month) {
  const v = (state.releves[cid] || {})[month];
  return (v === undefined || v === null || v === '') ? null : Number(v);
}
function setReleve(cid, month, val) {
  if (!state.releves[cid]) state.releves[cid] = {};
  if (val === '' || val === null || isNaN(val)) delete state.releves[cid][month];
  else state.releves[cid][month] = val;
}
// Consommation d'un compteur sur un mois = index fin de mois − index fin du mois d'avant
function consoCompteur(cid, month) {
  const a = releve(cid, addMonths(month, -1));
  const b = releve(cid, month);
  if (a === null || b === null) return null;
  return Math.round((b - a) * 1000) / 1000;
}
function compteursDe(logementId, nature) {
  return state.compteurs.filter(c => (c.logementId || '') === (logementId || '') && c.nature === nature);
}
function canalLabel(canal) { return canal === 'hp' ? 'jour (HP)' : canal === 'hc' ? 'nuit (HC)' : ''; }

// Charges réelles d'un logement pour le mois de consommation `cm`
function consoLogement(l, cm) {
  const t = tarifPour(cm);
  const manquants = [];
  const lignes = [];
  let kwhTotal = 0, total = 0, aElec = false;

  // --- Électricité ---
  const lignesElec = [];
  if (l.elec === 'deduite') {
    // Pas de compteur propre : consommation = compteur général − tous les autres logements
    aElec = true;
    let kwh = 0;
    const gen = compteursDe('', 'elec');
    if (!gen.length) manquants.push('compteur général d\'électricité (à créer)');
    gen.forEach(c => {
      const x = consoCompteur(c.id, cm);
      if (x === null) manquants.push(c.nom + ' (' + monthKeyLabel(cm) + ')'); else kwh += x;
    });
    state.compteurs.filter(c => c.nature === 'elec' && c.logementId && c.logementId !== l.id).forEach(c => {
      const x = consoCompteur(c.id, cm);
      if (x === null) manquants.push(c.nom + ' (' + monthKeyLabel(cm) + ')'); else kwh -= x;
    });
    lignesElec.push({ label: 'Éclairage (général − autres logements)', kwh, prix: num(t.moyen) });
  } else {
    compteursDe(l.id, 'elec').forEach(c => {
      aElec = true;
      const x = consoCompteur(c.id, cm);
      if (x === null) { manquants.push(c.nom + ' (' + monthKeyLabel(cm) + ')'); return; }
      const prix = c.canal === 'hp' ? num(t.hp) : c.canal === 'hc' ? num(t.hc) : num(t.moyen);
      lignesElec.push({ label: 'Éclairage ' + canalLabel(c.canal), kwh: x, prix });
    });
  }
  lignesElec.forEach(e => {
    const m = e.kwh * e.prix;
    kwhTotal += e.kwh; total += m;
    lignes.push({ label: e.label.trim(), detail: nf(e.kwh, 0) + ' kWh × ' + nf(e.prix, 4) + ' €', montant: m });
  });
  if (aElec) {
    const m = kwhTotal * num(t.tcfe);
    total += m;
    lignes.push({ label: 'TCFE, CSPE', detail: nf(kwhTotal, 0) + ' kWh × ' + nf(num(t.tcfe), 4) + ' €', montant: m });
    total += num(t.elecAbo);
    lignes.push({ label: 'Abonnement + CTA', detail: '', montant: num(t.elecAbo) });
  }

  // --- Eau ---
  const eau = compteursDe(l.id, 'eau');
  let m3 = 0;
  eau.forEach(c => {
    const x = consoCompteur(c.id, cm);
    if (x === null) manquants.push(c.nom + ' (' + monthKeyLabel(cm) + ')'); else m3 += x;
  });
  if (eau.length) {
    const m = m3 * num(t.eau);
    total += m;
    lignes.push({ label: 'Eau', detail: nf(m3, 2) + ' m³ × ' + nf(num(t.eau), 4) + ' €', montant: m });
    total += num(t.eauAbo);
    lignes.push({ label: 'Abonnement eau', detail: '', montant: num(t.eauAbo) });
  }

  return { cm, lignes, total: round2(total), kwhTotal, m3, manquants };
}

// Tout ce qu'il faut pour l'avis d'échéance d'un logement pour le mois M
function avisLogement(l, M) {
  const cm = addMonths(M, -1);                      // les charges de l'avis = consommation du mois d'avant
  const loyer = valeurAuMois(l.loyers, M);
  const om = valeurAuMois(l.om, M);
  const conso = consoLogement(l, cm);
  const avance = num(l.avance);
  const enAvance = l.modeCharges === 'avance';
  const charges = enAvance ? avance : conso.total;
  const acc = getCompte(l.accountId);
  const data = acc ? computeAccountMonth(acc, M) : null;
  const report = data ? data.report : 0;           // reste dû des mois précédents (négatif = trop-perçu)
  const appel = round2(loyer + om + charges + report);
  const encaisse = data ? data.totalEncaisse : 0;
  const reste = round2(appel - encaisse);
  return { l, M, cm, loyer, om, conso, avance, enAvance, charges, acc, data, report, appel, encaisse, reste };
}

// ---------- envoi de l'« attendu » vers le compte de suivi ----------
function poserPostAuto(acc, M, key, label, montant) {
  // Retourne 'cree' | 'maj' | 'fige' | 'rien'
  let p = state.accountPosts.find(x => x.accountId === acc.id && x.month === M && x.auto === key);
  if (!p) {
    if (!montant) return 'rien';
    state.accountPosts.push({ id: uid(), accountId: acc.id, month: M, label, amount: round2(montant), auto: key });
    return 'cree';
  }
  if (p.checked) return 'fige';
  if (!montant) { state.accountPosts = state.accountPosts.filter(x => x.id !== p.id); return 'maj'; }
  p.label = label; p.amount = round2(montant);
  return 'maj';
}

function majAttenduLogement(l, M) {
  const acc = getCompte(l.accountId);
  if (!acc) return { ok: false, msg: l.code + ' : pas de compte de suivi (clique sur « Créer le compte de suivi »).' };
  const A = avisLogement(l, M);
  const res = [];
  const r1 = poserPostAuto(acc, M, 'loyer', 'Loyer ' + l.code, A.loyer);
  const r2 = poserPostAuto(acc, M, 'om', 'Ordures ménagères ' + l.code, A.om);
  let r3 = 'rien';
  if (A.conso.manquants.length) {
    res.push('charges non ajoutées (relevés manquants : ' + A.conso.manquants.join(', ') + ')');
  } else {
    r3 = poserPostAuto(acc, M, 'charges', 'Charges ' + l.code + ' (consommation de ' + monthKeyLabel(A.cm) + ')', A.conso.total);
  }
  [r1, r2, r3].forEach(r => { if (r === 'fige') res.push('un poste figé (✅) n\'a pas été modifié'); });
  const nb = [r1, r2, r3].filter(r => r === 'cree' || r === 'maj').length;
  return { ok: true, msg: l.code + ' : ' + nb + ' poste(s) à jour' + (res.length ? ' — ' + res.join(' ; ') : '') };
}

function majAttenduMois(logementId) {
  const liste = logementId ? [getLogement(logementId)].filter(Boolean) : logementsActifs();
  if (!liste.length) return alert('Aucun logement.');
  const msgs = liste.map(l => majAttenduLogement(l, locatifMonth).msg);
  save(); renderAll();
  alert('Attendu de ' + monthKeyLabel(locatifMonth) + ' :\n\n' + msgs.join('\n'));
}

// ---------- création d'un compte de suivi pour un logement ----------
function creerSuiviLogement(id) {
  const l = getLogement(id);
  if (!l) return;
  if (getCompte(l.accountId)) return alert('Ce logement a déjà un compte de suivi.');
  const nomCat = 'Loyer ' + l.code;
  let cat = state.categories.find(c => c.name.trim().toLowerCase() === nomCat.toLowerCase());
  if (!cat) {
    const colors = ['#667eea', '#11998e', '#f7971e', '#eb3349', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];
    cat = { id: uid(), name: nomCat, budget: 0, color: colors[state.categories.length % colors.length] };
    state.categories.push(cat);
  }
  const check = checkCategoryAssignable(cat.id, 'tenant', null);
  if (!check.ok) return alert('La catégorie « ' + cat.name + ' » est déjà utilisée par le compte « ' + check.blockedBy.name + ' ».');
  const acc = { id: uid(), name: l.code + (l.locataire ? ' — ' + l.locataire : ''), type: 'tenant', categoryIds: [cat.id] };
  state.accounts.push(acc);
  l.accountId = acc.id;
  save(); renderAll();
  alert('✅ Compte de suivi créé.\n\nPour enregistrer un paiement du locataire : onglet Transactions → recette, catégorie « ' + cat.name + ' », puis pointe-la (⬜ → ✅).');
}

// ---------- logements : fenêtre de saisie ----------
function openLogementModal(id) {
  const l = id ? getLogement(id) : null;
  const m = document.getElementById('logementModal');
  m.dataset.id = id || '';
  document.getElementById('logementModalTitle').textContent = l ? '✏️ Modifier ' + l.code : '➕ Nouveau logement';
  const cur = monthKey(new Date());
  const v = (k, d = '') => document.getElementById(k).value = d;
  v('lgCode', l ? l.code : 'APP' + (state.logements.length + 1));
  v('lgLocataire', l ? l.locataire : '');
  v('lgAdresse', l ? l.adresse : '');
  v('lgSurface', l ? l.surface : '');
  v('lgLoyer', l ? valeurAuMois(l.loyers, cur) : '');
  v('lgOm', l ? valeurAuMois(l.om, cur) : '');
  v('lgDepuis', cur);
  v('lgMode', l ? l.modeCharges : 'reel');
  v('lgAvance', l ? l.avance : '');
  v('lgElec', l ? l.elec : 'releves');
  v('lgEntree', l ? l.entree : '');
  v('lgCaution', l ? l.caution : '');
  v('lgIrl', l ? l.irlRef : '');
  document.getElementById('lgActif').checked = l ? l.actif !== false : true;
  majLogementModalChamps();
  m.classList.add('active');
}
function majLogementModalChamps() {
  document.getElementById('lgAvanceWrap').style.display = document.getElementById('lgMode').value === 'avance' ? 'block' : 'none';
}
function closeLogementModal() { document.getElementById('logementModal').classList.remove('active'); }

function saveLogement() {
  const m = document.getElementById('logementModal');
  const id = m.dataset.id;
  const code = document.getElementById('lgCode').value.trim();
  if (!code) return alert('Donne un nom court au logement (ex. APP1)');
  const depuis = document.getElementById('lgDepuis').value || monthKey(new Date());
  const loyer = num(document.getElementById('lgLoyer').value);
  const om = num(document.getElementById('lgOm').value);
  let l = id ? getLogement(id) : null;
  if (!l) {
    l = { id: uid(), loyers: [], om: [], accountId: '' };
    state.logements.push(l);
  }
  l.code = code;
  l.locataire = document.getElementById('lgLocataire').value.trim();
  l.adresse = document.getElementById('lgAdresse').value.trim();
  l.surface = num(document.getElementById('lgSurface').value);
  l.modeCharges = document.getElementById('lgMode').value;
  l.avance = num(document.getElementById('lgAvance').value);
  l.elec = document.getElementById('lgElec').value;
  l.entree = document.getElementById('lgEntree').value;
  l.caution = num(document.getElementById('lgCaution').value);
  l.irlRef = num(document.getElementById('lgIrl').value);
  l.actif = document.getElementById('lgActif').checked;

  // Loyer et ordures ménagères : on ne crée une nouvelle ligne d'historique que si la valeur change
  const majHist = (hist, val) => {
    const cur = valeurAuMois(hist, depuis);
    if (!hist.length) { hist.push({ from: '2000-01', montant: val }); return; }
    if (Math.abs(cur - val) < 0.005) return;
    const same = hist.find(h => h.from === depuis);
    if (same) same.montant = val; else hist.push({ from: depuis, montant: val });
  };
  majHist(l.loyers, loyer);
  majHist(l.om, om);

  closeLogementModal();
  save(); renderAll();
}

function deleteLogement(id) {
  const l = getLogement(id);
  if (!l) return;
  if (!confirm('Supprimer le logement ' + l.code + ' ?\n\nSon compte de suivi, ses compteurs et ses relevés ne sont PAS supprimés.')) return;
  state.logements = state.logements.filter(x => x.id !== id);
  state.compteurs.forEach(c => { if (c.logementId === id) c.logementId = ''; });
  save(); renderAll();
}

// Révision du loyer avec l'indice IRL : nouveau loyer = ancien loyer × nouvel indice ÷ ancien indice
function reviserLoyer(id) {
  const l = getLogement(id);
  if (!l) return;
  if (!l.irlRef) return alert('Renseigne d\'abord l\'indice IRL de référence (bouton ✏️ du logement).');
  const nouvel = prompt('Nouvel indice IRL (ancien indice : ' + l.irlRef + ') :', '');
  if (nouvel === null) return;
  const irl = num(nouvel);
  if (irl <= 0) return alert('Indice invalide');
  const cur = valeurAuMois(l.loyers, monthKey(new Date()));
  const nouveau = round2(cur * irl / l.irlRef);
  const depuis = prompt('Nouveau loyer : ' + fmt(nouveau) + '\n(ancien : ' + fmt(cur) + ')\n\nÀ partir de quel mois ? (AAAA-MM)', addMonths(monthKey(new Date()), 1));
  if (depuis === null) return;
  if (!/^\d{4}-\d{2}$/.test(depuis.trim())) return alert('Format attendu : AAAA-MM (ex. 2027-03)');
  const from = depuis.trim();
  const same = l.loyers.find(h => h.from === from);
  if (same) same.montant = nouveau; else l.loyers.push({ from, montant: nouveau });
  l.irlRef = irl;
  save(); renderAll();
}

// ---------- compteurs ----------
function addCompteur() {
  const nom = document.getElementById('cpNom').value.trim();
  if (!nom) return alert('Donne un nom au compteur (ex. Eau APP1)');
  state.compteurs.push({
    id: uid(), nom,
    nature: document.getElementById('cpNature').value,
    canal: document.getElementById('cpCanal').value,
    logementId: document.getElementById('cpLogement').value
  });
  document.getElementById('cpNom').value = '';
  save(); renderLocatif();
}
function deleteCompteur(id) {
  const c = state.compteurs.find(x => x.id === id);
  if (!c) return;
  if (!confirm('Supprimer le compteur « ' + c.nom + ' » et tous ses relevés ?')) return;
  state.compteurs = state.compteurs.filter(x => x.id !== id);
  delete state.releves[id];
  save(); renderLocatif();
}
function saisirReleve(cid, valeur) {
  const v = String(valeur).trim() === '' ? '' : num(valeur);
  setReleve(cid, locatifMonth, v);
  save();
  majCalculsReleves();
}
// Met à jour les consommations affichées SANS reconstruire la page (pour ne pas perdre le champ en cours)
function majCalculsReleves() {
  state.compteurs.forEach(c => {
    const el = document.getElementById('conso-' + c.id);
    if (!el) return;
    const x = consoCompteur(c.id, locatifMonth);
    el.textContent = x === null ? '—' : nf(x, c.nature === 'eau' ? 2 : 0) + (c.nature === 'eau' ? ' m³' : ' kWh');
  });
  logementsActifs().filter(l => l.elec === 'deduite').forEach(l => {
    const el = document.getElementById('deduit-' + l.id);
    if (!el) return;
    const c = consoLogement(l, locatifMonth);
    el.textContent = c.manquants.length ? 'relevés manquants' : nf(c.kwhTotal, 0) + ' kWh';
  });
}

// ---------- tarifs ----------
function addTarif() {
  const base = tarifPour(locatifMonth);
  const from = locatifMonth;
  if (state.tarifs.some(t => t.from === from)) return alert('Il y a déjà une ligne de tarifs qui commence en ' + monthKeyLabel(from) + '.');
  state.tarifs.push({ ...base, from });
  save(); renderLocatif();
}
function deleteTarif(i) {
  if (!confirm('Supprimer cette ligne de tarifs ?')) return;
  state.tarifs.splice(i, 1);
  save(); renderLocatif();
}
function setTarif(i, key, val) {
  const t = state.tarifs[i];
  if (!t) return;
  if (key === 'from') {
    if (!/^\d{4}-\d{2}$/.test(val)) return alert('Mois attendu : AAAA-MM');
    t.from = val;
  } else t[key] = num(val);
  save();
}

// ---------- régularisations ----------
function setRegul(type, key, val) {
  state.regul[type][key] = (key === 'debut' || key === 'fin') ? val : num(val);
  save();
  majResultatsRegul();
}

function calcRegulOM() {
  const p = state.regul.om;
  const logs = state.logements.filter(l => l.surface > 0);
  const surfaceTotale = p.surfaceTotale > 0 ? p.surfaceTotale : logs.reduce((s, l) => s + l.surface, 0);
  if (!(p.cotisation > 0) || !(surfaceTotale > 0)) return null;
  const prixM2 = p.cotisation / surfaceTotale;
  // seuls les logements qui paient une TOM sont régularisés (les autres comptent seulement dans la surface totale)
  const lignes = logs.filter(l => valeurAuMois(l.om, p.annee + '-01') > 0).map(l => {
    const part = prixM2 * l.surface;
    const nouvelle = part / 12;
    const ancienne = valeurAuMois(l.om, p.annee + '-01');
    const regul = round2(nouvelle * p.mois) - round2(ancienne * p.mois);
    return { l, part, nouvelle: round2(nouvelle), ancienne, regul: round2(regul) };
  });
  return { prixM2, surfaceTotale, lignes };
}

function calcRegulEau() {
  const p = state.regul.eau;
  if (!p.debut || !p.fin || p.debut >= p.fin || !(p.totalM3 > 0) || !(p.totalFacture > 0)) return null;
  const prixReel = p.totalFacture / p.totalM3;
  const lignes = logementsActifs().map(l => {
    const cpts = compteursDe(l.id, 'eau');
    if (!cpts.length) return null;
    let m3 = 0, manque = false;
    cpts.forEach(c => {
      const a = releve(c.id, p.debut), b = releve(c.id, p.fin);
      if (a === null || b === null) manque = true; else m3 += b - a;
    });
    const regulConso = m3 * (prixReel - p.prixApplique);
    const regulAbo = p.aboReel - p.aboFacture;
    return { l, m3, manque, regulConso: round2(regulConso), regulAbo: round2(regulAbo), regul: round2(regulConso + regulAbo) };
  }).filter(Boolean);
  return { prixReel, lignes };
}

function majResultatsRegul() {
  const om = document.getElementById('regulOMResult');
  if (om) {
    const r = calcRegulOM();
    if (!r) om.innerHTML = '<div class="hint">Saisis la cotisation annuelle d\'ordures ménagères pour voir le calcul.</div>';
    else om.innerHTML = `
      <div class="hint">Prix au m² : ${nf(r.prixM2, 4)} € (cotisation ÷ ${nf(r.surfaceTotale, 0)} m²)</div>
      <div class="table-scroll"><table><thead><tr><th>Logement</th><th>m²</th><th>Part annuelle</th><th>Nouvelle mensualité</th><th>Mensualité payée</th><th>À régulariser</th><th></th></tr></thead><tbody>
      ${r.lignes.map(x => `<tr>
        <td><strong>${esc(x.l.code)}</strong></td><td>${nf(x.l.surface, 0)}</td><td>${fmt(x.part)}</td>
        <td>${fmt(x.nouvelle)}</td><td>${fmt(x.ancienne)}</td>
        <td class="${x.regul > 0 ? 'amount-neg' : 'amount-pos'}"><strong>${fmt(x.regul)}</strong></td>
        <td style="white-space:nowrap;">
          <button class="primary" style="padding:5px 8px;font-size:0.75rem;" onclick="appliquerMensualiteOM('${x.l.id}')" title="Nouvelle mensualité à partir du mois choisi en haut">📌 Mensualité</button>
          <button class="success" style="padding:5px 8px;font-size:0.75rem;" onclick="ajouterRegulAuSuivi('om','${x.l.id}')" title="Ajoute la régularisation à l'attendu du mois choisi en haut">➕ Suivi</button>
        </td></tr>`).join('')}
      </tbody></table></div>
      <div class="hint">Positif (rouge) = le locataire doit encore ce montant. Négatif = il a trop versé. « Mensualité » et « Suivi » agissent sur le mois choisi en haut de la page : <strong>${monthKeyLabel(locatifMonth)}</strong>.</div>`;
  }
  const eau = document.getElementById('regulEauResult');
  if (eau) {
    const r = calcRegulEau();
    if (!r) eau.innerHTML = '<div class="hint">Choisis la période (mois de début &lt; mois de fin) et saisis le total de la facture et les m³ facturés.</div>';
    else eau.innerHTML = `
      <div class="hint">Prix réel du m³ : ${nf(r.prixReel, 4)} € (facture ÷ m³)</div>
      <div class="table-scroll"><table><thead><tr><th>Logement</th><th>m³ consommés</th><th>Régul. consommation</th><th>Régul. abonnement</th><th>Total à régulariser</th><th></th></tr></thead><tbody>
      ${r.lignes.map(x => `<tr>
        <td><strong>${esc(x.l.code)}</strong></td>
        <td>${x.manque ? '<span class="amount-neg">relevé manquant</span>' : nf(x.m3, 2)}</td>
        <td>${fmt(x.regulConso)}</td><td>${fmt(x.regulAbo)}</td>
        <td class="${x.regul > 0 ? 'amount-neg' : 'amount-pos'}"><strong>${fmt(x.regul)}</strong></td>
        <td><button class="success" style="padding:5px 8px;font-size:0.75rem;" onclick="ajouterRegulAuSuivi('eau','${x.l.id}')">➕ Suivi</button></td></tr>`).join('')}
      </tbody></table></div>
      <div class="hint">« ➕ Suivi » ajoute la régularisation à l'attendu du mois choisi en haut : <strong>${monthKeyLabel(locatifMonth)}</strong>.</div>`;
  }
}

function ajouterRegulAuSuivi(type, logementId) {
  const l = getLogement(logementId);
  const acc = l && getCompte(l.accountId);
  if (!acc) return alert('Ce logement n\'a pas de compte de suivi.');
  let montant, label, key;
  if (type === 'om') {
    const r = calcRegulOM(); const x = r && r.lignes.find(y => y.l.id === logementId);
    if (!x) return;
    montant = x.regul; label = 'Régul ordures ménagères ' + state.regul.om.annee + ' ' + l.code; key = 'regul-om-' + state.regul.om.annee;
  } else {
    const r = calcRegulEau(); const x = r && r.lignes.find(y => y.l.id === logementId);
    if (!x) return;
    if (x.manque) return alert('Il manque un relevé d\'eau pour ce logement sur la période.');
    montant = x.regul; label = 'Régul eau ' + state.regul.eau.debut + ' → ' + state.regul.eau.fin + ' ' + l.code; key = 'regul-eau-' + state.regul.eau.debut + '-' + state.regul.eau.fin;
  }
  const res = poserPostAuto(acc, locatifMonth, key, label, montant);
  save(); renderAll();
  alert(res === 'fige' ? 'Ce poste est figé (✅), il n\'a pas été modifié.' :
    res === 'rien' ? 'Montant nul : rien à ajouter.' :
    '✅ ' + label + ' : ' + fmt(montant) + ' ajouté à l\'attendu de ' + monthKeyLabel(locatifMonth) + '.');
}

function appliquerMensualiteOM(logementId) {
  const r = calcRegulOM(); const x = r && r.lignes.find(y => y.l.id === logementId);
  if (!x) return;
  const l = x.l;
  if (!confirm('Mensualité d\'ordures ménagères de ' + l.code + ' : ' + fmt(x.nouvelle) + ' à partir de ' + monthKeyLabel(locatifMonth) + ' ?')) return;
  const same = l.om.find(h => h.from === locatifMonth);
  if (same) same.montant = x.nouvelle; else l.om.push({ from: locatifMonth, montant: x.nouvelle });
  save(); renderAll();
}

// ---------- avis d'échéance (aperçu et impression) ----------
function avisHTML(A) {
  const l = A.l;
  const p = state.proprietaire;
  const releveSeul = A.loyer === 0 && A.om === 0;
  const titre = releveSeul ? 'RELEVÉ DE CHARGES' : 'AVIS D\'ÉCHÉANCE';
  const debut = releveSeul ? A.cm : A.M;
  const periode = 'Du ' + frDate(debut + '-01') + ' au ' + frDate(debut + '-' + String(lastDayOfMonth(debut)).padStart(2, '0'));
  const ligne = (label, montant, detail) => `<tr><td>${label}${detail ? ' <span class="avis-detail">' + detail + '</span>' : ''}</td><td class="r">${fmt(montant)}</td></tr>`;
  let rows = '';
  if (A.loyer) rows += ligne('Loyer', A.loyer);
  if (A.om) rows += ligne('Taxe d\'ordures ménagères (TOM)', A.om);
  if (A.enAvance && !releveSeul) {
    rows += ligne('Avance sur charges', A.avance);
  } else if (A.conso.lignes.length) {
    rows += `<tr class="avis-sub"><td colspan="2">Charges — consommation de ${monthKeyLabel(A.cm)}</td></tr>`;
    A.conso.lignes.forEach(x => { rows += ligne(esc(x.label), x.montant, esc(x.detail)); });
    rows += `<tr class="avis-sub-total"><td>Total charges</td><td class="r">${fmt(A.conso.total)}</td></tr>`;
  }
  if (Math.abs(A.report) > 0.004) {
    rows += ligne(A.report > 0 ? 'Régularisation : reste dû des mois précédents' : 'Régularisation : trop-perçu des mois précédents', A.report);
  }
  const total = A.appel;
  const deja = A.encaisse > 0.004
    ? `<tr><td>Déjà réglé ce mois (pointé)</td><td class="r">− ${fmt(A.encaisse)}</td></tr>
       <tr class="avis-total"><td>RESTE À RÉGLER</td><td class="r">${fmt(A.reste)}</td></tr>` : '';
  return `<div class="avis">
    <div class="avis-top">
      <div>
        <strong>${esc(p.nom) || '<em>(propriétaire à renseigner)</em>'}</strong><br>
        ${esc(p.adresse)}<br>${esc(p.ville)}<br>${esc(p.email)}${p.tel ? '<br>Tél : ' + esc(p.tel) : ''}
      </div>
      <div class="avis-titre">${titre}<br><span>${periode}</span></div>
    </div>
    <div class="avis-locataire">
      <strong>${esc(l.locataire)}</strong><br>
      ${esc(l.adresse)}
    </div>
    <table class="avis-table"><tbody>
      ${rows}
      <tr class="avis-total"><td>MONTANT DÛ À CE JOUR</td><td class="r">${fmt(total)}</td></tr>
      ${deja}
    </tbody></table>
    ${A.conso.manquants.length && !A.enAvance ? `<div class="avis-warn">⚠️ Relevés manquants : ${esc(A.conso.manquants.join(', '))}. Le montant des charges est incomplet.</div>` : ''}
    <div class="avis-pied">
      Règlement à effectuer au premier jour ouvrable du mois.<br>
      ${p.iban ? 'IBAN : ' + esc(p.iban) + (p.bic ? ' — BIC : ' + esc(p.bic) : '') + '<br>' : ''}
      ${p.lieu ? 'À ' + esc(p.lieu) + ', le ' : 'Le '}${new Date().toLocaleDateString('fr-FR')} — <em>Ceci n'est pas une quittance.</em>
    </div>
  </div>`;
}

function majAvisPreview() {
  const el = document.getElementById('avisPreview');
  if (!el) return;
  const l = getLogement(avisLogementId);
  if (!l) { el.innerHTML = '<div class="empty">Choisis un logement</div>'; return; }
  const A = avisLogement(l, locatifMonth);
  const manque = A.conso.manquants.length;
  const infoAvance = A.enAvance ? `<div class="hint">Ce logement paie une <strong>avance sur charges</strong> (${fmt(A.avance)}). Les charges réelles de ${monthKeyLabel(A.cm)} (${fmt(A.conso.total)}) sont ajoutées à l'attendu du compte de suivi : l'écart (réel − avance) réapparaît tout seul en « régularisation » sur l'avis suivant.</div>` : '';
  el.innerHTML = `
    ${infoAvance}
    ${manque ? `<div class="hint warn">⚠️ Relevés manquants pour calculer les charges : ${esc(A.conso.manquants.join(', '))}.
      <button class="primary" style="padding:4px 8px;font-size:0.75rem;" onclick="allerReleves('${A.cm}')">Saisir les relevés de ${monthKeyLabel(A.cm)}</button></div>` : ''}
    ${avisHTML(A)}
    <div class="avis-actions">
      <button class="success" onclick="majAttenduMois('${l.id}')">📥 Mettre à jour l'attendu dans le compte de suivi</button>
      <button class="primary" onclick="imprimerAvis()">🖨️ Imprimer / PDF</button>
    </div>`;
}

function imprimerAvis() {
  const l = getLogement(avisLogementId);
  if (!l) return;
  document.getElementById('avisPrintZone').innerHTML = avisHTML(avisLogement(l, locatifMonth));
  document.body.classList.add('print-avis');
  window.print();
  setTimeout(() => document.body.classList.remove('print-avis'), 500);
}

function allerReleves(month) {
  locatifMonth = month;
  locatifSection = 'releves';
  renderLocatif();
}

// ---------- SUIVI CONSO : tableau mois par mois (comme l'onglet du tableur) ----------
const SUIVI_NB_MOIS = 12;

function moisFenetre(fin, nb = SUIVI_NB_MOIS) {
  const l = [];
  for (let i = nb - 1; i >= 0; i--) l.push(addMonths(fin, -i));
  return l;
}
const courtMois = k => { const [y, m] = k.split('-').map(Number); return new Date(y, m - 1, 1).toLocaleDateString('fr-FR', { month: 'short' }).replace('.', '') + ' ' + String(y).slice(2); };

// Contenu d'une cellule calculée, repérée par sa clé « type|a|b|mois »
function calcCellSuivi(k) {
  const [type, a, b, c] = k.split('|');
  const aff = (x, d = 0) => x === null || x === undefined || isNaN(x) ? '—' : nf(x, d);
  if (type === 'conso') {                         // consommation d'un compteur : conso|cid|nature|mois
    const x = consoCompteur(a, c);
    return aff(x, b === 'eau' ? 2 : 0);
  }
  if (type === 'tot') {                           // total d'un logement : tot|lgid|nature|mois
    const cp = compteursDe(a, b);
    let s = 0;
    for (const cc of cp) { const x = consoCompteur(cc.id, c); if (x === null) return '—'; s += x; }
    return cp.length ? aff(s, b === 'eau' ? 2 : 0) : '—';
  }
  if (type === 'ded') {                           // électricité déduite : ded|lgid||mois
    const l = getLogement(a);
    const r = l && consoLogement(l, c);
    return r && !r.manquants.length ? aff(r.kwhTotal, 0) : '—';
  }
  if (type === 'gen') {                           // total général : gen|nature||mois
    const cp = compteursDe('', a);
    let s = 0;
    for (const cc of cp) { const x = consoCompteur(cc.id, c); if (x === null) return '—'; s += x; }
    return cp.length ? aff(s, a === 'eau' ? 2 : 0) : '—';
  }
  if (type === 'ctl') {                           // contrôle eau : général − somme des logements
    const gen = compteursDe('', 'eau');
    if (!gen.length) return '—';
    let g = 0;
    for (const cc of gen) { const x = consoCompteur(cc.id, c); if (x === null) return '—'; g += x; }
    let s = 0;
    for (const cc of state.compteurs.filter(z => z.nature === 'eau' && z.logementId)) { const x = consoCompteur(cc.id, c); if (x === null) return '—'; s += x; }
    return aff(g - s, 2);
  }
  if (type === 'chg') {                           // charges calculées en € : chg|lgid||mois
    const l = getLogement(a);
    const r = l && consoLogement(l, c);
    return r && !r.manquants.length ? fmt(r.total) : '—';
  }
  return '';
}
function majSuiviCalculs() {
  document.querySelectorAll('#suiviTable [data-k]').forEach(td => { td.textContent = calcCellSuivi(td.dataset.k); });
}
function saisirReleveMois(cid, mois, valeur) {
  setReleve(cid, mois, String(valeur).trim() === '' ? '' : num(valeur));
  save();
  majSuiviCalculs();
}

function locatifSuiviHTML() {
  const mois = moisFenetre(locatifMonth);
  const nomLg = id => { const l = getLogement(id); return l ? l.code : 'Général'; };
  const th = mois.map(m => `<th class="num">${courtMois(m)}</th>`).join('');
  const cols = mois.length + 1;
  const rowIndex = c => `<tr><td class="sticky">${esc(c.nom)} <span class="hint">index</span></td>${mois.map(m =>
    `<td><input type="number" step="any" inputmode="decimal" class="cell-input mini" value="${releve(c.id, m) === null ? '' : esc(releve(c.id, m))}" onchange="saisirReleveMois('${c.id}', '${m}', this.value)"></td>`).join('')}</tr>`;
  const rowCalc = (label, keyFn, cls = 'calc') => `<tr class="${cls}"><td class="sticky">${label}</td>${mois.map(m => `<td class="num" data-k="${keyFn(m)}"></td>`).join('')}</tr>`;
  const grp = t => `<tr class="grp"><td colspan="${cols}">${t}</td></tr>`;
  const tri = (a, b) => nomLg(a.logementId).localeCompare(nomLg(b.logementId)) || a.nom.localeCompare(b.nom);

  let h = '';
  // ----- électricité -----
  h += grp('⚡ ÉLECTRICITÉ (index en kWh)');
  logementsActifs().forEach(l => {
    const cp = compteursDe(l.id, 'elec').sort(tri);
    cp.forEach(c => { h += rowIndex(c) + rowCalc('&nbsp;&nbsp;↳ conso kWh', m => `conso|${c.id}|elec|${m}`); });
    if (cp.length > 1) h += rowCalc(`<strong>${esc(l.code)} — total kWh</strong>`, m => `tot|${l.id}|elec|${m}`, 'calc total');
    if (l.elec === 'deduite') h += rowCalc(`<strong>${esc(l.code)} — kWh déduits (général − autres)</strong>`, m => `ded|${l.id}||${m}`, 'calc total');
  });
  const gE = compteursDe('', 'elec').sort(tri);
  gE.forEach(c => { h += rowIndex(c) + rowCalc('&nbsp;&nbsp;↳ conso kWh', m => `conso|${c.id}|elec|${m}`); });
  if (gE.length) h += rowCalc('<strong>Général — total kWh</strong>', m => `gen|elec||${m}`, 'calc total');

  // ----- eau -----
  h += grp('💧 EAU (index en m³)');
  logementsActifs().forEach(l => {
    compteursDe(l.id, 'eau').sort(tri).forEach(c => { h += rowIndex(c) + rowCalc('&nbsp;&nbsp;↳ conso m³', m => `conso|${c.id}|eau|${m}`); });
  });
  const gW = compteursDe('', 'eau');
  gW.forEach(c => { h += rowIndex(c) + rowCalc('&nbsp;&nbsp;↳ conso m³', m => `conso|${c.id}|eau|${m}`); });
  if (gW.length) h += rowCalc('<strong>Contrôle : général − somme des logements (m³)</strong>', m => `ctl|||${m}`, 'calc total');

  // ----- charges calculées -----
  h += grp('💶 CHARGES CALCULÉES (électricité + eau + abonnements, tarif du mois)');
  logementsActifs().forEach(l => { h += rowCalc(esc(l.code), m => `chg|${l.id}||${m}`); });

  return `<div class="card">
      <div class="section-title">Suivi de la consommation</div>
      <div class="hint">Saisis (ou corrige) directement l'<strong>index de fin de mois</strong> dans le tableau : les consommations, les totaux, le contrôle de l'eau et les charges en € se calculent tout seuls.
      Les 12 mois affichés se terminent en <strong>${monthKeyLabel(locatifMonth)}</strong> (◀ ▶ en haut pour décaler).</div>
      <div class="table-scroll"><table id="suiviTable" class="suivi">
        <thead><tr><th class="sticky">Compteur</th>${th}</tr></thead>
        <tbody>${h || `<tr><td colspan="${cols}" class="hint">Aucun compteur</td></tr>`}</tbody>
      </table></div>
    </div>`;
}

// ---------- FACTURE EDF : nouveaux tarifs, écarts, régularisation au prorata ----------
const r4 = n => Math.round(n * 10000) / 10000;
const r3 = n => Math.round(n * 1000) / 1000;

function nbLogementsElec() {
  return Math.max(1, logementsActifs().filter(l => l.elec === 'deduite' || compteursDe(l.id, 'elec').length).length);
}
// Première ouverture : on part des tarifs actuels (ce qui ne change pas n'est pas à ressaisir)
function initFacture() {
  const f = state.factureEdf;
  if (f.init) return;
  const t = tarifPour(locatifMonth);
  const n = nbLogementsElec();
  f.hcHT = String(Math.round(t.hc / 1.2 * 100000) / 100000);
  f.hpHT = String(Math.round(t.hp / 1.2 * 100000) / 100000);
  f.acciseHT = String(Math.round(t.tcfe / 1.2 * 100000) / 100000);
  f.tcfeHT = '0';
  f.aboHT = String(Math.round(t.elecAbo * n / 1.2 * 100) / 100);
  f.ctaHT = '0';
  f.tva = 20; f.nbLogements = n;
  f.init = true;
  save();
}

function periodeFacture(f) {
  if (!f.debut || !f.fin || f.debut > f.fin) return [];
  const a = f.debut.slice(0, 7), b = f.fin.slice(0, 7);
  const l = [];
  for (let k = a; k <= b && l.length < 12; k = addMonths(k, 1)) l.push(k);
  return l;
}
// Part du mois comprise dans la période de la facture (prorata au nombre de jours), modifiable à la main
function partMois(f, m) {
  if (f.parts && f.parts[m] !== undefined && f.parts[m] !== '') return num(f.parts[m]) / 100;
  const dim = lastDayOfMonth(m);
  let d1 = 1, d2 = dim;
  if (m === f.debut.slice(0, 7)) d1 = Number(f.debut.slice(8, 10));
  if (m === f.fin.slice(0, 7)) d2 = Number(f.fin.slice(8, 10));
  return Math.max(0, (d2 - d1 + 1) / dim);
}
function tarifsFacture(f) {
  const k = 1 + num(f.tva) / 100;
  const n = Math.max(1, num(f.nbLogements) || 1);
  return {
    hc: num(f.hcHT) * k, hp: num(f.hpHT) * k,
    tcfe: (num(f.acciseHT) + num(f.tcfeHT)) * k,
    elecAbo: (num(f.aboHT) + num(f.ctaHT)) * k / n
  };
}

function calcFacture() {
  const f = state.factureEdf;
  const mois = periodeFacture(f);
  const nw = tarifsFacture(f);
  const base = mois.length ? mois[0] : locatifMonth;
  const old = tarifPour(base);
  // tarif moyen (logements sans jour/nuit) : facture − ce que paient les logements jour/nuit
  let kwhHC = 0, kwhHP = 0, manqueMoyen = false;
  state.compteurs.filter(c => c.nature === 'elec' && c.logementId && (c.canal === 'hc' || c.canal === 'hp')).forEach(c => {
    mois.forEach(m => {
      const x = consoCompteur(c.id, m);
      if (x === null) { manqueMoyen = true; return; }
      if (c.canal === 'hc') kwhHC += x * partMois(f, m); else kwhHP += x * partMois(f, m);
    });
  });
  const ttc = num(f.montantHT) * (1 + num(f.tva) / 100);
  const coutJN = kwhHC * nw.hc + kwhHP * nw.hp;
  const kwhReste = num(f.kwhFacture) - (kwhHC + kwhHP);
  const moyenNew = kwhReste > 0 && ttc > 0 ? (ttc - coutJN) / kwhReste : 0;
  const moyenOld = num(old.moyen);
  const moyenUtile = moyenNew > 0 ? moyenNew : moyenOld;

  // régularisation : mois de la période, sauf le dernier (déjà facturé au nouveau tarif sur l'avis suivant)
  const moisReg = f.excludeLast === false ? mois : mois.slice(0, -1);
  const nbAbo = (f.moisAbo === '' || f.moisAbo === undefined) ? moisReg.length : num(f.moisAbo);
  const lignes = logementsActifs().map(l => {
    const lg = []; let manque = false, kwhTot = 0, aElec = false;
    const ajoute = (label, kwh, ancien, nouveau) => {
      kwhTot += kwh;
      lg.push({ label, detail: nf(kwh, 1) + ' kWh × (' + nf(nouveau, 5) + ' − ' + nf(ancien, 5) + ')', montant: kwh * (nouveau - ancien) });
    };
    if (l.elec === 'deduite') {
      aElec = true; let kwh = 0;
      moisReg.forEach(m => { const r = consoLogement(l, m); if (r.manquants.length) manque = true; else kwh += r.kwhTotal * partMois(f, m); });
      ajoute('Éclairage (déduit)', kwh, moyenOld, moyenUtile);
    } else {
      compteursDe(l.id, 'elec').forEach(c => {
        aElec = true; let kwh = 0;
        moisReg.forEach(m => { const x = consoCompteur(c.id, m); if (x === null) manque = true; else kwh += x * partMois(f, m); });
        if (c.canal === 'hc') ajoute('Éclairage nuit (HC)', kwh, num(old.hc), nw.hc);
        else if (c.canal === 'hp') ajoute('Éclairage jour (HP)', kwh, num(old.hp), nw.hp);
        else ajoute('Éclairage', kwh, moyenOld, moyenUtile);
      });
    }
    if (aElec) {
      const kt = kwhTot;
      lg.push({ label: 'TCFE, CSPE', detail: nf(kt, 1) + ' kWh × (' + nf(nw.tcfe, 5) + ' − ' + nf(num(old.tcfe), 5) + ')', montant: kt * (nw.tcfe - num(old.tcfe)) });
      lg.push({ label: 'Abonnement + CTA', detail: nbAbo + ' mois × (' + nf(nw.elecAbo, 3) + ' − ' + nf(num(old.elecAbo), 3) + ')', montant: nbAbo * (nw.elecAbo - num(old.elecAbo)) });
    }
    const total = round2(lg.reduce((s, x) => s + x.montant, 0));
    return { l, lignes: lg, total, manque };
  });
  return { f, mois, moisReg, nw, old, kwhHC, kwhHP, ttc, coutJN, kwhReste, moyenNew, moyenOld, moyenUtile, manqueMoyen, lignes, nbAbo };
}

function setFacture(key, val) {
  const f = state.factureEdf;
  if (key === 'excludeLast') f[key] = !!val;
  else f[key] = val;
  save();
  if (key === 'debut' || key === 'fin') renderLocatif(); else majResultatFacture();
}
function setPartFacture(m, val) {
  const f = state.factureEdf;
  if (!f.parts) f.parts = {};
  f.parts[m] = val;
  save(); majResultatFacture();
}

function majResultatFacture() {
  const el = document.getElementById('factureResult');
  if (!el) return;
  const R = calcFacture();
  const f = R.f;
  const ligneT = (label, ancien, nouveau, d = 5) => {
    const ecart = nouveau - ancien;
    const change = Math.abs(ecart) > 0.000005;
    return `<tr class="${change ? 'changed' : ''}"><td>${label}</td><td class="num">${nf(ancien, d)}</td><td class="num"><strong>${nf(nouveau, d)}</strong></td>
      <td class="num ${change ? (ecart > 0 ? 'amount-neg' : 'amount-pos') : ''}">${change ? (ecart > 0 ? '+' : '') + nf(ecart, d) : '= inchangé'}</td></tr>`;
  };
  const moyenInfo = R.moyenNew > 0
    ? ligneT('kWh moyen (APP1, APP4…)', R.moyenOld, R.moyenNew)
    : `<tr><td>kWh moyen (APP1, APP4…)</td><td class="num">${nf(R.moyenOld, 5)}</td><td colspan="2" class="hint">saisis les kWh et le montant HT de la facture pour le calculer</td></tr>`;

  let html = `<div class="section-title" style="margin-top:14px;">Comparaison des tarifs (TTC)</div>
    <div class="hint">Ancien = tarif en vigueur en ${R.mois.length ? monthKeyLabel(R.mois[0]) : monthKeyLabel(locatifMonth)}. Les lignes colorées ont changé.</div>
    <div class="table-scroll"><table><thead><tr><th>Tarif</th><th class="num">Ancien</th><th class="num">Nouveau</th><th class="num">Écart</th></tr></thead><tbody>
      ${ligneT('kWh nuit (HC)', num(R.old.hc), R.nw.hc)}
      ${ligneT('kWh jour (HP)', num(R.old.hp), R.nw.hp)}
      ${ligneT('TCFE + accise (€/kWh)', num(R.old.tcfe), R.nw.tcfe)}
      ${ligneT('Abonnement + CTA (€/mois/logement)', num(R.old.elecAbo), R.nw.elecAbo, 3)}
      ${moyenInfo}
    </tbody></table></div>`;

  if (R.moyenNew > 0) {
    html += `<div class="calc-line"><span>Facture TTC : ${fmt(R.ttc)} − consommation des logements jour/nuit (${nf(R.kwhHC, 0)} kWh nuit + ${nf(R.kwhHP, 0)} kWh jour = ${fmt(R.coutJN)})</span><span></span></div>
      <div class="calc-line"><span>kWh restants répartis entre les logements sans jour/nuit</span><strong>${nf(R.kwhReste, 0)} kWh</strong></div>`;
    if (R.manqueMoyen) html += '<div class="hint warn">⚠️ Il manque des relevés sur la période : le tarif moyen est incomplet.</div>';
  }

  if (!R.mois.length) {
    html += '<div class="hint warn">Renseigne les dates de début et de fin de la facture pour calculer la régularisation.</div>';
  } else {
    html += `<div class="section-title" style="margin-top:16px;">Régularisation de la période (${frDate(f.debut)} → ${frDate(f.fin)})</div>
      <div class="hint">Mois régularisés : ${R.moisReg.map(m => monthKeyLabel(m) + ' (' + Math.round(partMois(f, m) * 100) + ' %)').join(', ') || 'aucun'}.
      Positif = le locataire doit en plus. Négatif = on lui rend.</div>`;
    html += R.lignes.map(x => `<div class="regul-bloc">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap;">
          <strong>${esc(x.l.code)}</strong> <span class="hint">${esc(x.l.locataire)}</span>
          <span class="${x.total > 0 ? 'amount-neg' : 'amount-pos'}" style="font-size:1.05rem;"><strong>${fmt(x.total)}</strong></span>
        </div>
        ${x.manque ? '<div class="hint warn">⚠️ Relevés manquants sur la période : montant incomplet.</div>' : ''}
        <div class="table-scroll"><table><tbody>${x.lignes.map(z => `<tr><td>${esc(z.label)}</td><td class="hint">${z.detail}</td><td class="num">${nf(z.montant, 4)} €</td></tr>`).join('')}</tbody></table></div>
        <button class="success" style="padding:5px 10px;font-size:.8rem;" onclick="ajouterRegulEdfAuSuivi('${x.l.id}')">➕ Ajouter ${fmt(x.total)} au suivi de ${monthKeyLabel(locatifMonth)}</button>
      </div>`).join('');
  }

  html += `<div class="card inner" style="margin-top:16px;">
      <div class="section-title">Appliquer les nouveaux tarifs</div>
      <div class="hint">Les avis utilisent le tarif <strong>du mois de consommation</strong>. Par défaut : à partir du dernier mois de la facture (les mois d'avant sont régularisés ci-dessus).</div>
      <div class="form-row">
        <label>À partir du mois<input type="month" id="factureAppliquerDes" value="${R.mois.length ? R.mois[R.mois.length - 1] : locatifMonth}"></label>
        <button class="success" onclick="appliquerFacture()">✅ Appliquer ces tarifs</button>
      </div>
    </div>`;
  el.innerHTML = html;
}

function appliquerFacture() {
  const R = calcFacture();
  const from = document.getElementById('factureAppliquerDes').value;
  if (!/^\d{4}-\d{2}$/.test(from)) return alert('Choisis le mois de départ (AAAA-MM)');
  const prev = tarifPour(from);
  const nouveau = {
    ...prev, from,
    hc: r4(R.nw.hc), hp: r4(R.nw.hp), tcfe: r4(R.nw.tcfe), elecAbo: r3(R.nw.elecAbo),
    moyen: r4(R.moyenUtile)
  };
  const i = state.tarifs.findIndex(t => t.from === from);
  if (i >= 0) state.tarifs[i] = nouveau; else state.tarifs.push(nouveau);
  save(); renderLocatif();
  alert('✅ Nouveaux tarifs appliqués à partir de ' + monthKeyLabel(from) + '.\n\nTu peux les revoir et les corriger dans l\'onglet Tarifs.');
}

function ajouterRegulEdfAuSuivi(logementId) {
  const R = calcFacture();
  const x = R.lignes.find(y => y.l.id === logementId);
  const l = x && x.l;
  const acc = l && getCompte(l.accountId);
  if (!acc) return alert('Ce logement n\'a pas de compte de suivi (onglet Logements).');
  if (x.manque && !confirm('Des relevés manquent : le montant est incomplet. Ajouter quand même ?')) return;
  const f = R.f;
  const res = poserPostAuto(acc, locatifMonth, 'regul-edf-' + f.fin, 'Régul lumière ' + frDate(f.debut) + ' → ' + frDate(f.fin) + ' ' + l.code, x.total);
  save(); renderAll();
  alert(res === 'fige' ? 'Ce poste est figé (✅), il n\'a pas été modifié.' :
    res === 'rien' ? 'Montant nul : rien à ajouter.' : '✅ Régularisation de ' + fmt(x.total) + ' ajoutée à l\'attendu de ' + monthKeyLabel(locatifMonth) + '.');
}

function locatifFactureHTML() {
  initFacture();
  const f = state.factureEdf;
  const mois = periodeFacture(f);
  const inp = (key, label, step = 'any') => `<label>${label}<input type="number" step="${step}" inputmode="decimal" value="${esc(f[key])}" onchange="setFacture('${key}', this.value)"></label>`;
  return `<div class="card">
      <div class="section-title">⚡ Facture EDF de l'immeuble</div>
      <div class="hint">Saisis les chiffres de ta nouvelle facture. Ceux qui n'ont pas changé sont déjà remplis avec les tarifs actuels : tu ne modifies que ce qui change. Les prix sont <strong>hors taxes (HT)</strong>, comme sur la facture.</div>
      <div class="form-row">
        <label>N° de facture<input value="${esc(f.numero)}" onchange="setFacture('numero', this.value)"></label>
        <label>Début de période<input type="date" value="${esc(f.debut)}" onchange="setFacture('debut', this.value)"></label>
        <label>Fin de période<input type="date" value="${esc(f.fin)}" onchange="setFacture('fin', this.value)"></label>
      </div>
      <div class="form-row">
        ${inp('hcHT', 'kWh nuit HC (€ HT)')}${inp('hpHT', 'kWh jour HP (€ HT)')}
        ${inp('acciseHT', 'Accise / « Ac s/Elect » (€ HT/kWh)')}${inp('tcfeHT', 'TCFE (€ HT/kWh)')}
      </div>
      <div class="form-row">
        ${inp('aboHT', 'Abonnement immeuble (€ HT/mois)')}${inp('ctaHT', 'CTA immeuble (€ HT/mois)')}
        ${inp('tva', 'TVA (%)')}${inp('nbLogements', 'Nombre de logements qui se partagent l\'abonnement', '1')}
      </div>
      <div class="form-row">
        ${inp('kwhFacture', 'Total kWh facturés (immeuble)')}${inp('montantHT', 'Prix HT total de la facture (€)')}
      </div>
      <div class="hint">Les deux derniers chiffres servent à calculer le <strong>tarif moyen</strong> des logements sans heures pleines/creuses (APP1, APP4).</div>
      <div class="section-title" style="margin-top:12px;">Régularisation au prorata</div>
      <div class="form-row" style="align-items:center;">
        <label class="inline" style="margin:0;"><input type="checkbox" ${f.excludeLast === false ? '' : 'checked'} onchange="setFacture('excludeLast', this.checked)"> Ne pas régulariser le dernier mois (déjà facturé au nouveau tarif)</label>
        ${inp('moisAbo', 'Mois d\'abonnement à régulariser (vide = automatique)', '1')}
      </div>
      ${mois.length ? `<div class="hint">Part de consommation retenue pour chaque mois de la période (calculée d'après les jours, modifiable) :</div>
        <div class="form-row">${mois.map(m => `<label>${monthKeyLabel(m)} (%)<input type="number" step="1" inputmode="decimal" value="${Math.round(partMois(f, m) * 1000) / 10}" onchange="setPartFacture('${m}', this.value)"></label>`).join('')}</div>` : ''}
    </div>
    <div class="card"><div id="factureResult"></div></div>`;
}

// ---------- HISTORIQUE : mois par mois, par logement ----------
let histLogementId = '';
let histPeriode = '12';   // '12' = 12 derniers mois, ou une année (ex. '2026')

function setHist(key, val) { if (key === 'lg') histLogementId = val; else histPeriode = val; renderLocatif(); }

function locatifHistoriqueHTML() {
  const actifs = state.logements;
  if (!actifs.length) return '<div class="card"><div class="empty">Aucun logement</div></div>';
  if (!histLogementId || !getLogement(histLogementId)) histLogementId = actifs[0].id;
  const l = getLogement(histLogementId);
  const acc = getCompte(l.accountId);
  const an = Number(locatifMonth.slice(0, 4));
  let mois;
  if (histPeriode === '12') mois = moisFenetre(locatifMonth, 12);
  else mois = Array.from({ length: 12 }, (_, i) => histPeriode + '-' + String(i + 1).padStart(2, '0'));

  const tot = { loyer: 0, om: 0, charges: 0, du: 0, enc: 0, kwh: 0, m3: 0 };
  const lignes = mois.map(M => {
    const cm = addMonths(M, -1);
    const loyer = valeurAuMois(l.loyers, M), om = valeurAuMois(l.om, M);
    const conso = consoLogement(l, cm);
    const complet = !conso.manquants.length;
    const premier = acc ? state.accountPosts.filter(p => p.accountId === acc.id).map(p => p.month).sort()[0] : null;
    const data = acc && premier && M >= premier ? computeAccountMonth(acc, M) : null;   // avant le départ du suivi : pas de chiffres
    const du = data ? data.totalPostes : loyer + om + (complet ? conso.total : 0);
    const enc = data ? data.totalEncaisse : null;
    tot.loyer += loyer; tot.om += om; tot.du += du;
    if (complet) { tot.charges += conso.total; tot.kwh += conso.kwhTotal; tot.m3 += conso.m3; }
    if (enc !== null) tot.enc += enc;
    const vide = !complet && !data && !loyer && !om;
    return `<tr class="${vide ? 'calc' : ''}">
      <td><strong>${monthKeyLabel(M)}</strong></td>
      <td class="num">${fmt(loyer)}</td><td class="num">${fmt(om)}</td>
      <td class="num">${complet ? fmt(conso.total) : '<span class="hint">incomplet</span>'}</td>
      <td class="num hint">${complet ? nf(conso.kwhTotal, 0) + ' kWh · ' + nf(conso.m3, 1) + ' m³' : '—'}</td>
      <td class="num">${acc && !data ? '—' : fmt(du)}</td>
      <td class="num">${enc === null ? '—' : fmt(enc)}</td>
      <td class="num ${data ? (data.cumulTotal < -0.005 ? 'amount-neg' : data.cumulTotal > 0.005 ? 'amount-pos' : '') : ''}"><strong>${data ? fmt(data.cumulTotal) : '—'}</strong></td>
    </tr>`;
  }).join('');

  const annees = [];
  for (let y = an; y >= an - 4; y--) annees.push(y);
  return `<div class="card">
      <div class="section-title">📜 Historique</div>
      <div class="form-row">
        <label>Logement<select onchange="setHist('lg', this.value)">${actifs.map(x => `<option value="${x.id}" ${x.id === histLogementId ? 'selected' : ''}>${esc(x.code)} — ${esc(x.locataire)}</option>`).join('')}</select></label>
        <label>Période<select onchange="setHist('per', this.value)">
          <option value="12" ${histPeriode === '12' ? 'selected' : ''}>12 mois jusqu'à ${monthKeyLabel(locatifMonth)}</option>
          ${annees.map(y => `<option value="${y}" ${histPeriode === String(y) ? 'selected' : ''}>Année ${y}</option>`).join('')}
        </select></label>
      </div>
      <div class="hint">Charges = consommation du mois d'avant. « Dû » et « Encaissé » viennent du compte de suivi (règlements pointés)${acc ? '' : ' — ce logement n\'en a pas, le dû est donc recalculé'}. « Solde cumulé » : négatif = reste à percevoir, positif = trop-perçu.</div>
      <div class="table-scroll"><table>
        <thead><tr><th>Mois</th><th class="num">Loyer</th><th class="num">TOM</th><th class="num">Charges</th><th class="num">Consommation</th><th class="num">Dû</th><th class="num">Encaissé</th><th class="num">Solde cumulé</th></tr></thead>
        <tbody>${lignes}
          <tr class="calc total"><td>Total</td><td class="num">${fmt(tot.loyer)}</td><td class="num">${fmt(tot.om)}</td><td class="num">${fmt(tot.charges)}</td>
          <td class="num">${nf(tot.kwh, 0)} kWh · ${nf(tot.m3, 1)} m³</td><td class="num">${fmt(tot.du)}</td><td class="num">${acc ? fmt(tot.enc) : '—'}</td><td></td></tr>
        </tbody>
      </table></div>
    </div>`;
}

// ---------- propriétaire ----------
function setProprio(key, val) { state.proprietaire[key] = val; save(); }

// ---------- navigation de la page Locatif ----------
function setLocatifSection(s) { locatifSection = s; renderLocatif(); }
function navigateLocatifMonth(delta) { locatifMonth = addMonths(locatifMonth, delta); renderLocatif(); }
function setLocatifMonth(v) { if (/^\d{4}-\d{2}$/.test(v)) { locatifMonth = v; renderLocatif(); } }
function setAvisLogement(id) { avisLogementId = id; majAvisPreview(); }

// ---------- rendu ----------
function renderLocatif() {
  const body = document.getElementById('locatifBody');
  if (!body) return;

  // barre du haut : mois + onglets
  document.getElementById('locatifMonthLabel').textContent = monthKeyLabel(locatifMonth);
  const sections = [
    ['apercu', '📊 Vue d\'ensemble'], ['logements', '🏠 Logements'], ['suivi', '📈 Suivi conso'], ['historique', '📜 Historique'], ['releves', '🔢 Saisie du mois'],
    ['avis', '🧾 Avis'], ['facture', '⚡ Facture EDF'], ['tarifs', '💶 Tarifs'], ['regul', '⚖️ Ordures / eau'], ['proprio', '👤 Propriétaire']
  ];
  document.getElementById('locatifPills').innerHTML = sections.map(([k, label]) =>
    `<button class="pill ${locatifSection === k ? 'active' : ''}" onclick="setLocatifSection('${k}')">${label}</button>`).join('');

  const actifs = logementsActifs();
  if (!avisLogementId || !getLogement(avisLogementId)) avisLogementId = actifs.length ? actifs[0].id : '';

  switch (locatifSection) {
    case 'logements': body.innerHTML = locatifLogementsHTML(); break;
    case 'historique': body.innerHTML = locatifHistoriqueHTML(); break;
    case 'suivi':     body.innerHTML = locatifSuiviHTML(); majSuiviCalculs(); break;
    case 'releves':   body.innerHTML = locatifRelevesHTML(); majCalculsReleves(); break;
    case 'facture':   body.innerHTML = locatifFactureHTML(); majResultatFacture(); break;
    case 'avis':      body.innerHTML = locatifAvisHTML(); majAvisPreview(); break;
    case 'tarifs':    body.innerHTML = locatifTarifsHTML(); break;
    case 'regul':     body.innerHTML = locatifRegulHTML(); majResultatsRegul(); break;
    case 'proprio':   body.innerHTML = locatifProprioHTML(); break;
    default:          body.innerHTML = locatifApercuHTML();
  }
}

// ----- Vue d'ensemble -----
function locatifApercuHTML() {
  const M = locatifMonth;
  const actifs = logementsActifs();
  if (!actifs.length) {
    return `<div class="card"><div class="empty">Aucun logement pour l'instant.<br>
      Va dans <strong>🏠 Logements</strong> pour les créer, ou importe ton tableur dans l'onglet <strong>Données</strong>.</div></div>`;
  }
  const lignes = actifs.map(l => ({ l, A: avisLogement(l, M) }));
  const totAppel = lignes.reduce((s, x) => s + x.A.appel, 0);
  const totEnc = lignes.reduce((s, x) => s + (x.A.acc ? x.A.encaisse : 0), 0);
  const totReste = lignes.reduce((s, x) => s + (x.A.acc ? Math.max(0, x.A.reste) : 0), 0);
  const sansSuivi = lignes.filter(x => !x.A.acc);
  const incomplets = lignes.filter(x => x.A.conso.manquants.length && !x.A.enAvance);

  return `
    <div class="kpis" style="margin-bottom:15px;">
      <div class="kpi"><div class="kpi-label">À appeler (${monthKeyLabel(M)})</div><div class="kpi-value">${fmt(totAppel)}</div></div>
      <div class="kpi green"><div class="kpi-label">Encaissé (pointé)</div><div class="kpi-value">${fmt(totEnc)}</div></div>
      <div class="kpi ${totReste > 0.005 ? 'red' : 'green'}"><div class="kpi-label">Reste à percevoir</div><div class="kpi-value">${fmt(totReste)}</div></div>
    </div>
    ${incomplets.length ? `<div class="hint warn">⚠️ Relevés manquants pour : ${incomplets.map(x => esc(x.l.code)).join(', ')} — les charges de ${monthKeyLabel(addMonths(M, -1))} sont incomplètes.
       <button class="primary" style="padding:4px 8px;font-size:0.75rem;" onclick="allerReleves('${addMonths(M, -1)}')">Saisir les relevés</button></div>` : ''}
    ${sansSuivi.length ? `<div class="hint warn">ℹ️ Sans compte de suivi (donc rien n'est pointé) : ${sansSuivi.map(x => esc(x.l.code)).join(', ')}. Voir l'onglet 🏠 Logements.</div>` : ''}
    <div class="card">
      <div class="table-scroll"><table>
        <thead><tr><th>Logement</th><th>Loyer + TOM</th><th>Charges</th><th>Report</th><th>À appeler</th><th>Encaissé</th><th>Reste</th></tr></thead>
        <tbody>${lignes.map(({ l, A }) => `<tr>
          <td><strong>${esc(l.code)}</strong><br><span class="hint">${esc(l.locataire)}</span></td>
          <td>${fmt(A.loyer + A.om)}</td>
          <td>${fmt(A.charges)}<br><span class="hint">${A.enAvance ? 'avance' : (A.conso.manquants.length ? 'incomplet' : 'réel')}</span></td>
          <td class="${A.report > 0.005 ? 'amount-neg' : A.report < -0.005 ? 'amount-pos' : ''}">${fmt(A.report)}</td>
          <td><strong>${fmt(A.appel)}</strong></td>
          <td>${A.acc ? fmt(A.encaisse) : '—'}</td>
          <td class="${A.acc ? (A.reste > 0.005 ? 'amount-neg' : 'amount-pos') : ''}"><strong>${A.acc ? fmt(A.reste) : '—'}</strong></td>
        </tr>`).join('')}</tbody>
      </table></div>
      <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;">
        <button class="success" onclick="majAttenduMois('')">📥 Mettre à jour l'attendu de ${monthKeyLabel(M)} (tous les logements)</button>
      </div>
      <div class="hint" style="margin-top:8px;">Les charges du mois ${monthKeyLabel(M)} sont calculées d'après la consommation de ${monthKeyLabel(addMonths(M, -1))}.
      « Reste » = à appeler − règlements pointés en ${monthKeyLabel(M)}.</div>
    </div>`;
}

// ----- Logements -----
function locatifLogementsHTML() {
  const M = locatifMonth;
  const cartes = state.logements.map(l => {
    const acc = getCompte(l.accountId);
    const hist = (h) => [...h].sort((a, b) => b.from.localeCompare(a.from)).slice(0, 4)
      .map(x => `${x.from === '2000-01' ? 'depuis toujours' : 'dès ' + monthKeyLabel(x.from)} : ${fmt(x.montant)}`).join(' · ');
    return `<div class="list-item" style="flex-direction:column;align-items:stretch;${l.actif === false ? 'opacity:.55;' : ''}">
      <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;">
        <div>
          <strong style="font-size:1.05rem;">${esc(l.code)}</strong> <span class="badge">${nf(l.surface, 0)} m²</span>
          ${l.actif === false ? '<span class="badge">inactif</span>' : ''}<br>
          <span>${esc(l.locataire) || '<em>(locataire à renseigner)</em>'}</span><br>
          <span class="hint">${esc(l.adresse)}</span>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="primary" style="padding:6px 10px;font-size:0.8rem;" onclick="openLogementModal('${l.id}')">✏️</button>
          <button class="danger" onclick="deleteLogement('${l.id}')">✕</button>
        </div>
      </div>
      <div class="loc-facts">
        <div><span>Loyer</span><strong>${fmt(valeurAuMois(l.loyers, M))}</strong></div>
        <div><span>Ordures ménagères</span><strong>${fmt(valeurAuMois(l.om, M))}</strong></div>
        <div><span>Charges</span><strong>${l.modeCharges === 'avance' ? 'Avance ' + fmt(l.avance) : 'Réelles (relevés)'}</strong></div>
        <div><span>Électricité</span><strong>${l.elec === 'deduite' ? 'Déduite du général' : 'Compteur(s)'}</strong></div>
        <div><span>Entrée</span><strong>${l.entree ? frDate(l.entree) : '—'}</strong></div>
        <div><span>Caution</span><strong>${l.caution ? fmt(l.caution) : '—'}</strong></div>
      </div>
      <div class="hint">Historique loyer : ${hist(l.loyers) || '—'}<br>Historique TOM : ${hist(l.om) || '—'}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        ${acc ? `<span class="badge income">🔗 Compte de suivi : ${esc(acc.name)}</span>`
              : `<button class="success" onclick="creerSuiviLogement('${l.id}')">🔗 Créer le compte de suivi</button>`}
        <button class="primary" onclick="reviserLoyer('${l.id}')">📈 Réviser le loyer (IRL)</button>
      </div>
    </div>`;
  }).join('');

  return `<div class="card">
      <div class="section-title">Mes logements</div>
      ${cartes || '<div class="empty">Aucun logement</div>'}
      <div style="margin-top:12px;"><button class="primary" onclick="openLogementModal('')">➕ Ajouter un logement</button></div>
      <div class="hint" style="margin-top:8px;">Le <strong>compte de suivi</strong> relie le logement à la banque : les virements du locataire (catégorie « Loyer … », pointés ✅) sont comptés tout seuls, sans les ressaisir.</div>
    </div>`;
}

// ----- Relevés -----
function locatifRelevesHTML() {
  const M = locatifMonth;
  const prev = addMonths(M, -1);
  const optLogements = '<option value="">Compteur général</option>' + state.logements.map(l => `<option value="${l.id}">${esc(l.code)}</option>`).join('');
  const nomLogement = id => { const l = getLogement(id); return id ? (l ? l.code : '?') : 'Général'; };
  const ligne = c => `<tr>
      <td>${esc(c.nom)}</td><td>${esc(nomLogement(c.logementId))}</td>
      <td>${releve(c.id, prev) === null ? '—' : esc(releve(c.id, prev))}</td>
      <td><input type="number" step="any" inputmode="decimal" class="cell-input" value="${releve(c.id, M) === null ? '' : esc(releve(c.id, M))}"
           onchange="saisirReleve('${c.id}', this.value)" placeholder="index"></td>
      <td id="conso-${c.id}">—</td>
      <td><button class="danger" style="padding:4px 8px;" onclick="deleteCompteur('${c.id}')">✕</button></td>
    </tr>`;
  const tri = (a, b) => (a.logementId === '' ? 'zzz' : nomLogement(a.logementId)).localeCompare(b.logementId === '' ? 'zzz' : nomLogement(b.logementId)) || a.nom.localeCompare(b.nom);
  const elec = state.compteurs.filter(c => c.nature === 'elec').sort(tri);
  const eau = state.compteurs.filter(c => c.nature === 'eau').sort(tri);
  const deduits = logementsActifs().filter(l => l.elec === 'deduite');

  return `<div class="card">
      <div class="section-title">Relevés de fin ${monthKeyLabel(M)}</div>
      <div class="hint">Saisis l'<strong>index lu sur le compteur</strong> à la fin du mois. Consommation = index de ce mois − index du mois précédent.
      Pour l'avis de ${monthKeyLabel(addMonths(M, 1))}, il faut les relevés de fin ${monthKeyLabel(M)} <em>et</em> de fin ${monthKeyLabel(prev)}.</div>
      <div class="table-scroll"><table>
        <thead><tr><th>Compteur</th><th>Logement</th><th>Index ${monthKeyLabel(prev)}</th><th>Index ${monthKeyLabel(M)}</th><th>Consommation</th><th></th></tr></thead>
        <tbody>
          <tr class="grp"><td colspan="6">⚡ Électricité</td></tr>${elec.map(ligne).join('') || '<tr><td colspan="6" class="hint">Aucun compteur</td></tr>'}
          ${deduits.map(l => `<tr class="deduit"><td>Éclairage ${esc(l.code)} <span class="hint">(déduit : général − autres)</span></td><td>${esc(l.code)}</td><td>—</td><td>—</td><td id="deduit-${l.id}">—</td><td></td></tr>`).join('')}
          <tr class="grp"><td colspan="6">💧 Eau</td></tr>${eau.map(ligne).join('') || '<tr><td colspan="6" class="hint">Aucun compteur</td></tr>'}
        </tbody>
      </table></div>
    </div>
    <div class="accordion-header" onclick="toggleAccordion('cptGestion')" style="margin-top:15px;">
      <span>⚙️ Gérer les compteurs (ajouter / supprimer)</span><span class="accordion-icon" id="icon-cptGestion">▼</span>
    </div>
    <div class="accordion-content" id="content-cptGestion" style="display:none;">
      <div class="form-row">
        <input id="cpNom" placeholder="Nom (ex. Eau APP1)">
        <select id="cpNature"><option value="elec">Électricité</option><option value="eau">Eau</option></select>
        <select id="cpCanal">
          <option value="unique">Un seul index</option>
          <option value="hp">Jour (heures pleines)</option>
          <option value="hc">Nuit (heures creuses)</option>
        </select>
        <select id="cpLogement">${optLogements}</select>
        <button class="primary" onclick="addCompteur()">➕ Ajouter</button>
      </div>
      <div class="hint">« Un seul index » = compteur simple (facturé au tarif moyen pour l'électricité). Compteur général = celui de tout l'immeuble (sert à déduire un logement sans compteur).</div>
    </div>`;
}

// ----- Avis -----
function locatifAvisHTML() {
  const opts = logementsActifs().map(l => `<option value="${l.id}" ${l.id === avisLogementId ? 'selected' : ''}>${esc(l.code)} — ${esc(l.locataire)}</option>`).join('');
  if (!opts) return '<div class="card"><div class="empty">Aucun logement</div></div>';
  return `<div class="card">
      <div class="form-row" style="margin-bottom:12px;">
        <label style="flex:1;min-width:220px;">Logement
          <select onchange="setAvisLogement(this.value)">${opts}</select></label>
      </div>
      <div class="hint">Avis du mois de <strong>${monthKeyLabel(locatifMonth)}</strong> (change le mois avec ◀ ▶ en haut).</div>
      <div id="avisPreview"></div>
    </div>`;
}

// ----- Tarifs -----
function locatifTarifsHTML() {
  const rows = state.tarifs.map((t, i) => {
    const champ = (k, step = '0.0001') => `<td><input type="number" step="${step}" inputmode="decimal" class="cell-input" value="${esc(t[k])}" onchange="setTarif(${i}, '${k}', this.value)"></td>`;
    return `<tr>
      <td><input type="month" class="cell-input" placeholder="AAAA-MM" value="${esc(t.from)}" onchange="setTarif(${i}, 'from', this.value)"></td>
      ${champ('eau')}${champ('eauAbo', '0.01')}${champ('hc')}${champ('hp')}${champ('moyen')}${champ('tcfe')}${champ('elecAbo', '0.01')}
      <td><button class="danger" style="padding:4px 8px;" onclick="deleteTarif(${i})">✕</button></td></tr>`;
  }).join('');
  const mois = m => `<option value="${m}">${monthKeyLabel(m)}</option>`;
  return `<div class="card">
      <div class="section-title">Tarifs (€ TTC)</div>
      <div class="hint">Un tarif est valable <strong>à partir du mois indiqué</strong> et jusqu'au suivant. Pour un avis, on utilise le tarif du mois de consommation.</div>
      <div class="table-scroll"><table>
        <thead><tr><th>Dès le mois</th><th>Eau €/m³</th><th>Abo. eau €/mois</th><th>kWh nuit (HC)</th><th>kWh jour (HP)</th><th>kWh moyen</th><th>TCFE €/kWh</th><th>Abo. + CTA €/mois</th><th></th></tr></thead>
        <tbody>${rows || '<tr><td colspan="9" class="hint">Aucun tarif</td></tr>'}</tbody>
      </table></div>
      <div style="margin-top:10px;"><button class="primary" onclick="addTarif()">➕ Nouvelle ligne à partir de ${monthKeyLabel(locatifMonth)}</button></div>
      <div class="hint" style="margin-top:8px;">Pour une nouvelle facture EDF, utilise plutôt l'onglet <strong>⚡ Facture EDF</strong> : il calcule les nouveaux tarifs et la régularisation.</div>
    </div>`;
}

// ----- Régularisations -----
function locatifRegulHTML() {
  const o = state.regul.om, e = state.regul.eau;
  const inp = (type, key, val, step = 'any') => `<input type="number" step="${step}" inputmode="decimal" value="${esc(val)}" onchange="setRegul('${type}', '${key}', this.value)">`;
  return `<div class="card">
      <div class="section-title">🗑️ Ordures ménagères — régularisation annuelle</div>
      <div class="hint">La cotisation de l'immeuble est répartie au m². On compare avec les mensualités déjà payées.</div>
      <div class="form-row">
        <label>Année${inp('om', 'annee', o.annee, '1')}</label>
        <label>Cotisation annuelle (€)${inp('om', 'cotisation', o.cotisation)}</label>
        <label>Surface totale (m²) <span class="hint">0 = somme des logements</span>${inp('om', 'surfaceTotale', o.surfaceTotale)}</label>
        <label>Nombre de mois à régulariser${inp('om', 'mois', o.mois, '1')}</label>
      </div>
      <div id="regulOMResult"></div>
    </div>
    <div class="card" style="margin-top:15px;">
      <div class="section-title">💧 Eau — régularisation d'après la facture annuelle</div>
      <div class="hint">Prix réel du m³ = facture ÷ m³ facturés. Pour chaque logement : m³ lus entre les deux relevés × (prix réel − prix appliqué), plus l'écart d'abonnement.</div>
      <div class="form-row">
        <label>Relevé de départ<input type="month" value="${esc(e.debut)}" onchange="setRegul('eau', 'debut', this.value)"></label>
        <label>Relevé de fin<input type="month" value="${esc(e.fin)}" onchange="setRegul('eau', 'fin', this.value)"></label>
        <label>Total de la facture (€)${inp('eau', 'totalFacture', e.totalFacture)}</label>
        <label>m³ facturés (immeuble)${inp('eau', 'totalM3', e.totalM3)}</label>
        <label>Prix du m³ déjà appliqué${inp('eau', 'prixApplique', e.prixApplique)}</label>
        <label>Abonnements réels / logement (€)${inp('eau', 'aboReel', e.aboReel)}</label>
        <label>Abonnements déjà facturés / logement (€)${inp('eau', 'aboFacture', e.aboFacture)}</label>
      </div>
      <div id="regulEauResult"></div>
    </div>`;
}

// ----- Propriétaire -----
function locatifProprioHTML() {
  const p = state.proprietaire;
  const f = (key, label, type = 'text') => `<label>${label}<input type="${type}" value="${esc(p[key])}" onchange="setProprio('${key}', this.value)"></label>`;
  return `<div class="card">
      <div class="section-title">Mes coordonnées (pour les avis d'échéance)</div>
      <div class="form-row">
        ${f('nom', 'Nom')}${f('adresse', 'Adresse')}${f('ville', 'Code postal et ville')}
        ${f('email', 'E-mail', 'email')}${f('tel', 'Téléphone', 'tel')}${f('lieu', 'Fait à (ville)')}
        ${f('iban', 'IBAN')}${f('bic', 'BIC')}
      </div>
      <div class="hint">Ces informations restent sur ton appareil (stockage du navigateur) et dans ta sauvegarde .json.</div>
    </div>`;
}

// ---------- import du tableur (fusion, sans rien effacer) ----------
function importLocatif() {
  const fileInput = document.getElementById('importLocatifFile');
  const file = fileInput.files[0];
  if (!file) return alert('Sélectionne d\'abord le fichier .json du tableur');
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const d = JSON.parse(e.target.result);
      if (!confirm('Ajouter les logements, compteurs, relevés, tarifs et comptes de suivi du tableur ?\n\n' +
        'Tes comptes bancaires, transactions et autres données ne sont PAS touchés.\n' +
        '(Si des logements existent déjà, ils sont remplacés par ceux du fichier.)')) return;
      const ajouteSiAbsent = (cible, source, cle) => (source || []).forEach(x => { if (!cible.some(y => y[cle] === x[cle])) cible.push(x); });
      // catégories : par identifiant OU par nom (pas de doublon)
      (d.categories || []).forEach(c => {
        if (!state.categories.some(y => y.id === c.id || y.name.trim().toLowerCase() === c.name.trim().toLowerCase())) state.categories.push(c);
      });
      // les comptes de suivi pointent vers des catégories : si une catégorie existait déjà sous un autre id, on corrige
      const idParNom = {};
      state.categories.forEach(c => { idParNom[c.name.trim().toLowerCase()] = c.id; });
      const idCat = {};
      (d.categories || []).forEach(c => { idCat[c.id] = idParNom[c.name.trim().toLowerCase()] || c.id; });
      (d.accounts || []).forEach(a => { a.categoryIds = (a.categoryIds || []).map(id => idCat[id] || id); });
      ajouteSiAbsent(state.accounts, d.accounts, 'id');
      ajouteSiAbsent(state.accountPosts, d.accountPosts, 'id');
      if (d.logements) state.logements = d.logements;
      if (d.compteurs) state.compteurs = d.compteurs;
      if (d.tarifs) state.tarifs = d.tarifs;
      if (d.proprietaire) state.proprietaire = { ...state.proprietaire, ...d.proprietaire };
      if (d.regul) state.regul = { om: { ...state.regul.om, ...(d.regul.om || {}) }, eau: { ...state.regul.eau, ...(d.regul.eau || {}) } };
      if (d.factureEdf) state.factureEdf = { ...state.factureEdf, ...d.factureEdf };
      Object.keys(d.releves || {}).forEach(cid => {
        state.releves[cid] = { ...(state.releves[cid] || {}), ...d.releves[cid] };
      });
      migrate();
      save();
      fileInput.value = '';
      renderAll();
      alert('✅ Tableur importé : ' + state.logements.length + ' logement(s), ' + state.compteurs.length + ' compteur(s).');
    } catch (err) {
      alert('❌ Fichier invalide : ' + err.message);
    }
  };
  reader.readAsText(file);
}

// ============ RENDU GLOBAL ============
function renderAll() {
  renderBanks();
  renderTxBanksSummary();
  renderCategories();
  populateSelects();
  renderTransactions();
  renderRecurring();
  renderAlertBanner();
  renderDashboard();
  renderForecast();
  renderAccounts();
  renderLocatif();
}

// ============ INITIALISATION ============
load();
loadForecastParams();
renderAll();