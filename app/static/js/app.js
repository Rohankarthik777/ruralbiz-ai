// RuralBiz AI - Main Application Controller
let currentLanguage = localStorage.getItem('ruralbiz_lang') || 'en';
let currentUser = null;
let cashflowChart = null;
let lastGeneratedIdeas = null;
let cachedChecklist = [];
let cachedSchemes = [];
let lastFinancialResults = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    checkAuthSession();
    setupEventListeners();
    loadDashboardSummary();
});

// --------------------------------------------------------------------------
// 1. Language & Localization
// --------------------------------------------------------------------------
function initLanguage() {
    setLanguage(currentLanguage);
}

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('ruralbiz_lang', lang);
    document.body.className = lang === 'ta' ? 'lang-ta' : '';
    
    // Update language toggle button text
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
        langBtn.innerHTML = lang === 'ta' ? '<i class="fa-solid fa-language text-rural-700 mr-1.5"></i> English' : '<i class="fa-solid fa-language text-rural-700 mr-1.5"></i> தமிழ்';
    }

    // Apply i18n dictionary to all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (translations[lang] && translations[lang][key]) {
            el.setAttribute('placeholder', translations[lang][key]);
        }
    });

    // Update chat input placeholder
    const chatInput = document.getElementById('chat-input');
    if (chatInput && translations[lang]['chat_placeholder']) {
        chatInput.placeholder = translations[lang]['chat_placeholder'];
    }

    // Update Daybook Category Select Dropdown
    populateCategoryDropdown();

    // Update Location select options
    const locSelect = document.getElementById('idea-location-select');
    if (locSelect) {
        Array.from(locSelect.options).forEach(opt => {
            const key = opt.getAttribute('data-i18n');
            if (key && translations[lang][key]) {
                opt.textContent = translations[lang][key];
            }
        });
    }

    // Update Filter select options
    const filterSelect = document.getElementById('cashbook-filter-type');
    if (filterSelect) {
        Array.from(filterSelect.options).forEach(opt => {
            const key = opt.getAttribute('data-i18n');
            if (key && translations[lang][key]) {
                opt.textContent = translations[lang][key];
            }
        });
    }

    // Re-render Generated Ideas if available
    if (lastGeneratedIdeas && lastGeneratedIdeas.length) {
        renderGeneratedIdeas(lastGeneratedIdeas);
    }

    // Update Chatbot Quick Prompts
    updateQuickPrompts(lang);

    // Re-render Financial Results if available
    if (lastFinancialResults) {
        renderFinancialResults(lastFinancialResults);
    }

    // Re-render Loan items if available
    if (cachedChecklist.length) {
        renderLoanChecklist(cachedChecklist);
    }
    if (cachedSchemes.length) {
        renderLoanSchemes(cachedSchemes);
    }
}

function toggleLanguage() {
    const nextLang = currentLanguage === 'en' ? 'ta' : 'en';
    setLanguage(nextLang);
    if (currentUser) {
        currentUser.preferred_language = nextLang;
    }
}

// --------------------------------------------------------------------------
// 2. Authentication & Session Management
// --------------------------------------------------------------------------
function getToken() {
    return localStorage.getItem('ruralbiz_token') || '';
}

function setToken(token) {
    localStorage.setItem('ruralbiz_token', token);
}

function clearToken() {
    localStorage.removeItem('ruralbiz_token');
    currentUser = null;
}

function authHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

async function checkAuthSession() {
    const token = getToken();
    if (!token) {
        updateAuthUI(null);
        return;
    }

    try {
        const res = await fetch('/api/auth/me', { headers: authHeaders() });
        if (res.ok) {
            const data = await res.json();
            currentUser = data.user;
            if (currentUser.preferred_language && !localStorage.getItem('ruralbiz_lang')) {
                setLanguage(currentUser.preferred_language);
            }
            updateAuthUI(currentUser);
        } else {
            clearToken();
            updateAuthUI(null);
        }
    } catch (e) {
        console.error("Session check error:", e);
    }
}

function updateAuthUI(user) {
    const authActions = document.getElementById('auth-actions');
    const userBadge = document.getElementById('user-badge');
    const userNameSpan = document.getElementById('user-name-display');

    if (user) {
        if (authActions) authActions.classList.add('hidden');
        if (userBadge) {
            userBadge.classList.remove('hidden');
            userNameSpan.innerText = user.full_name || user.username;
        }
    } else {
        if (authActions) authActions.classList.remove('hidden');
        if (userBadge) userBadge.classList.add('hidden');
    }
}

async function quickDemoLogin() {
    try {
        const res = await fetch('/api/auth/demo-login', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            setToken(data.token);
            currentUser = data.user;
            updateAuthUI(currentUser);
            showNotification(currentLanguage === 'ta' ? "டெமோ கணக்கில் வெற்றிகரமாக உள்நுழைந்துள்ளீர்கள்!" : "Logged into Demo Account successfully!", "success");
            loadCashbookData();
            loadDashboardSummary();
        }
    } catch (e) {
        alert("Demo login error: " + e.message);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Login failed");

        setToken(data.token);
        currentUser = data.user;
        updateAuthUI(currentUser);
        closeModal('auth-modal');
        showNotification(currentLanguage === 'ta' ? "மீண்டும் நல்வரவு, " + currentUser.full_name : "Welcome back, " + currentUser.full_name, "success");
        loadCashbookData();
        loadDashboardSummary();
    } catch (err) {
        document.getElementById('auth-error').innerText = err.message;
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const full_name = document.getElementById('reg-fullname').value;
    const phone = document.getElementById('reg-phone').value;
    const village_town = document.getElementById('reg-village').value;
    const district = document.getElementById('reg-district').value;
    const business_type = document.getElementById('reg-biztype').value;

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username, password, full_name, phone, village_town, district,
                preferred_language: currentLanguage, business_type
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Registration failed");

        setToken(data.token);
        currentUser = data.user;
        updateAuthUI(currentUser);
        closeModal('auth-modal');
        showNotification(currentLanguage === 'ta' ? "கணக்கு வெற்றிகரமாக உருவாக்கப்பட்டது!" : "Account created successfully!", "success");
    } catch (err) {
        document.getElementById('auth-error').innerText = err.message;
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST', headers: authHeaders() });
    } catch (e) {}
    clearToken();
    updateAuthUI(null);
    showNotification(currentLanguage === 'ta' ? "வெற்றிகரமாக வெளியேறினீர்கள்." : "Logged out successfully.", "info");
    switchTab('dashboard');
}

// --------------------------------------------------------------------------
// 3. Navigation & Tab Switching
// --------------------------------------------------------------------------
function switchTab(tabId) {
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.add('hidden');
    });

    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    const targetPanel = document.getElementById(`panel-${tabId}`);
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
    }

    const targetNav = document.getElementById(`tab-${tabId}`);
    if (targetNav) {
        targetNav.classList.add('active');
    }

    if (tabId === 'cashbook') {
        loadCashbookData();
    } else if (tabId === 'loan') {
        loadLoanSchemesAndChecklist();
    } else if (tabId === 'dashboard') {
        loadDashboardSummary();
    }
}

// --------------------------------------------------------------------------
// 4. Feature 2: AI Business Idea Generator
// --------------------------------------------------------------------------
function updateBudgetValue(val) {
    document.getElementById('budget-display').innerText = '₹ ' + parseInt(val).toLocaleString('en-IN');
}

async function runIdeaGenerator() {
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const budget = parseFloat(document.getElementById('idea-budget-slider').value);
    const location = document.getElementById('idea-location-select').value;
    
    const skillCheckboxes = document.querySelectorAll('.skill-checkbox:checked');
    const skills = Array.from(skillCheckboxes).map(cb => cb.value);

    const btn = document.getElementById('generate-ideas-btn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> ${currentLanguage === 'ta' ? 'தொழில் வாய்ப்புகளை பகுப்பாய்வு செய்கிறது...' : 'Analyzing local feasibility...'}`;

    try {
        const res = await fetch('/api/ideas/generate', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                budget,
                skills,
                location,
                language: currentLanguage
            })
        });
        const data = await res.json();
        lastGeneratedIdeas = data.ideas || [];
        renderGeneratedIdeas(lastGeneratedIdeas);
    } catch (e) {
        alert("Error generating ideas: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles text-harvest-500 mr-2"></i> ${translations[currentLanguage]['btn_generate_ideas']}`;
    }
}

function renderGeneratedIdeas(ideas) {
    const container = document.getElementById('ideas-result-container');
    container.innerHTML = '';

    if (!ideas || !ideas.length) {
        container.innerHTML = `<div class="p-8 text-center text-slate-500">${currentLanguage === 'ta' ? 'பொருத்தமான தொழில்கள் கண்டறியப்படவில்லை. பட்ஜெட்டை உயர்த்தி மீண்டும் முயற்சிக்கவும்.' : 'No matching business ideas found for this criteria. Try increasing budget or selecting general skills.'}</div>`;
        return;
    }

    const isTa = currentLanguage === 'ta';

    ideas.forEach((idea, index) => {
        const title = isTa ? (idea.ta_title || idea.title) : idea.title;
        const category = isTa ? (idea.ta_category || idea.category) : idea.category;
        const desc = isTa ? (idea.ta_description || idea.description) : idea.description;
        const steps = isTa ? (idea.ta_steps || idea.steps) : idea.steps;

        let materialsHtml = '';
        if (idea.materials) {
            materialsHtml = idea.materials.map(m => {
                const matName = isTa ? (m.ta_item || m.item) : m.item;
                return `
                    <li class="flex justify-between py-1 text-sm border-b border-slate-100">
                        <span class="text-slate-700 font-medium">• ${matName}</span>
                        <span class="font-bold text-slate-900">₹${m.cost.toLocaleString('en-IN')}</span>
                    </li>
                `;
            }).join('');
        }

        let stepsHtml = '';
        if (steps) {
            stepsHtml = steps.map((s, sIdx) => {
                const stepText = isTa ? (idea.ta_steps && idea.ta_steps[sIdx] ? idea.ta_steps[sIdx] : s) : s;
                return `<li class="mb-1 text-sm text-slate-700 leading-relaxed">${stepText}</li>`;
            }).join('');
        }

        const profitLabel = isTa
            ? `+₹${idea.estimated_monthly_profit.toLocaleString('en-IN')} / மாதம் (நிகர லாபம்)`
            : `+₹${idea.estimated_monthly_profit.toLocaleString('en-IN')}/mo net`;

        const card = document.createElement('div');
        card.className = "bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all";
        card.innerHTML = `
            <div class="flex flex-wrap items-start justify-between gap-4 mb-3">
                <div>
                    <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 mb-2">
                        ${category}
                    </span>
                    <h3 class="text-xl font-bold text-slate-900">${title}</h3>
                </div>
                <div class="text-right">
                    <div class="text-xs text-slate-500">${translations[currentLanguage]['card_est_cost']}</div>
                    <div class="text-xl font-extrabold text-emerald-700">₹${idea.estimated_investment.toLocaleString('en-IN')}</div>
                    <div class="text-xs text-emerald-600 font-bold">${profitLabel}</div>
                </div>
            </div>

            <p class="text-sm text-slate-600 mb-4 leading-relaxed">${desc}</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-lg mb-4">
                <div>
                    <h4 class="font-semibold text-xs uppercase tracking-wider text-slate-600 mb-2 flex items-center">
                        <i class="fa-solid fa-boxes-stacked mr-1.5 text-emerald-700"></i> ${translations[currentLanguage]['materials_needed']}
                    </h4>
                    <ul class="space-y-1">
                        ${materialsHtml}
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold text-xs uppercase tracking-wider text-slate-600 mb-2 flex items-center">
                        <i class="fa-solid fa-list-check mr-1.5 text-emerald-700"></i> ${translations[currentLanguage]['startup_steps']}
                    </h4>
                    <ol class="space-y-1.5 list-none">
                        ${stepsHtml}
                    </ol>
                </div>
            </div>

            <div class="flex flex-wrap gap-2 justify-end pt-2 border-t border-slate-100">
                <button onclick='loadIdeaIntoPlan(${JSON.stringify(idea).replace(/'/g, "&#39;")})' class="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors">
                    <i class="fa-solid fa-file-invoice mr-1"></i> ${translations[currentLanguage]['draft_plan_btn']}
                </button>
                <button onclick='saveBusinessIdea(${JSON.stringify(idea).replace(/'/g, "&#39;")})' class="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-700 text-white hover:bg-emerald-800 transition-colors">
                    <i class="fa-regular fa-bookmark mr-1"></i> ${translations[currentLanguage]['save_idea_btn']}
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function saveBusinessIdea(idea) {
    try {
        const title = currentLanguage === 'ta' ? (idea.ta_title || idea.title) : idea.title;
        const res = await fetch('/api/ideas/save', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                idea_title: title,
                idea_data: idea
            })
        });
        const data = await res.json();
        if (data.success) {
            showNotification(currentLanguage === 'ta' ? "தொழில் யோசனை சேமிக்கப்பட்டது!" : "Business idea saved to profile!", "success");
        }
    } catch (e) {
        alert("Error saving idea: " + e.message);
    }
}

function loadIdeaIntoPlan(idea) {
    switchTab('plan');
    const isTa = currentLanguage === 'ta';
    document.getElementById('plan-input-title').value = isTa ? (idea.ta_title || idea.title) : idea.title;
    document.getElementById('plan-input-category').value = isTa ? (idea.ta_category || idea.category) : idea.category;
    document.getElementById('plan-input-investment').value = idea.estimated_investment;
    document.getElementById('plan-input-sales').value = Math.round(idea.estimated_monthly_profit * 2.5);
    showNotification(currentLanguage === 'ta' ? "தொழில் விவரங்கள் திட்ட அறிக்கையில் நிரப்பப்பட்டது." : "Details loaded into Business Plan generator.", "info");
}

// --------------------------------------------------------------------------
// 5. Feature 3: Financial Planning Calculator
// --------------------------------------------------------------------------
async function runFinancialCalculator(e) {
    if (e) e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const daily_sales_units = parseFloat(document.getElementById('calc-daily-units').value) || 0;
    const selling_price_per_unit = parseFloat(document.getElementById('calc-selling-price').value) || 0;
    const cost_per_unit = parseFloat(document.getElementById('calc-cost-unit').value) || 0;
    const daily_operating_cost = parseFloat(document.getElementById('calc-daily-operating').value) || 0;
    const fixed_startup_cost = parseFloat(document.getElementById('calc-startup-cost').value) || 0;
    const working_capital_days = parseInt(document.getElementById('calc-working-days').value) || 30;

    try {
        const res = await fetch('/api/finance/calculate', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                daily_sales_units,
                selling_price_per_unit,
                cost_per_unit,
                daily_operating_cost,
                fixed_startup_cost,
                working_capital_days
            })
        });
        const data = await res.json();
        lastFinancialResults = data.results;
        renderFinancialResults(lastFinancialResults);
    } catch (err) {
        alert("Calculation error: " + err.message);
    }
}

function renderFinancialResults(res) {
    document.getElementById('calc-results-box').classList.remove('hidden');

    document.getElementById('res-daily-revenue').innerText = `₹${res.daily.revenue.toLocaleString('en-IN')}`;
    document.getElementById('res-daily-profit').innerText = `₹${res.daily.net_profit.toLocaleString('en-IN')}`;
    document.getElementById('res-monthly-revenue').innerText = `₹${res.monthly.revenue.toLocaleString('en-IN')}`;
    document.getElementById('res-monthly-profit').innerText = `₹${res.monthly.net_profit.toLocaleString('en-IN')}`;
    document.getElementById('res-profit-margin').innerText = `${res.monthly.profit_margin_pct}%`;

    const unitItem = translations[currentLanguage]['unit_item_mo'];
    const unitDay = translations[currentLanguage]['unit_day'];
    const unitMonth = translations[currentLanguage]['unit_month'];

    document.getElementById('res-breakeven-units').innerText = `${res.break_even.units_needed_monthly} ${unitItem}`;
    document.getElementById('res-breakeven-days').innerText = `${res.break_even.days_to_break_even_each_month} ${unitDay}`;
    
    document.getElementById('res-working-capital').innerText = `₹${res.capital_structure.working_capital_required.toLocaleString('en-IN')}`;
    document.getElementById('res-total-capital').innerText = `₹${res.capital_structure.total_startup_capital_required.toLocaleString('en-IN')}`;
    document.getElementById('res-payback').innerText = `${res.capital_structure.payback_period_months} ${unitMonth}`;

    const beDays = Math.min(26, res.break_even.days_to_break_even_each_month);
    const bePct = Math.min(100, Math.round((beDays / 26) * 100));
    const beBar = document.getElementById('breakeven-progress-bar');
    if (beBar) {
        beBar.style.width = `${bePct}%`;
        beBar.className = `h-2.5 rounded-full ${beDays <= 12 ? 'bg-emerald-600' : (beDays <= 20 ? 'bg-amber-500' : 'bg-red-500')}`;
    }
}

// --------------------------------------------------------------------------
// 6. Feature 4: Daily Cash Book
// --------------------------------------------------------------------------
function populateCategoryDropdown() {
    const typeSelect = document.getElementById('txn-type');
    const catSelect = document.getElementById('txn-category');
    if (!typeSelect || !catSelect) return;

    const currentType = typeSelect.value || 'income';
    const lang = currentLanguage || 'en';
    const categories = (daybookCategories[lang] && daybookCategories[lang][currentType])
        ? daybookCategories[lang][currentType]
        : daybookCategories['en'][currentType];

    const prevVal = catSelect.value;
    const promptText = translations[lang]['select_category_prompt'] || '-- Select Category --';
    catSelect.innerHTML = `<option value="">${promptText}</option>`;
    
    categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat;
        catSelect.appendChild(opt);
    });

    if (prevVal && categories.includes(prevVal)) {
        catSelect.value = prevVal;
    }
}

async function loadCashbookData() {
    if (!currentUser) return;

    try {
        const sumRes = await fetch('/api/cashbook/summary', { headers: authHeaders() });
        if (sumRes.ok) {
            const sumData = await sumRes.json();
            renderCashbookSummary(sumData);
        }

        const filterType = document.getElementById('cashbook-filter-type')?.value || '';
        let url = '/api/cashbook/transactions?limit=50';
        if (filterType) url += `&type=${filterType}`;

        const txnRes = await fetch(url, { headers: authHeaders() });
        if (txnRes.ok) {
            const txnData = await txnRes.json();
            renderCashbookTable(txnData.transactions || []);
        }
    } catch (e) {
        console.error("Cashbook load error:", e);
    }
}

function renderCashbookSummary(data) {
    document.getElementById('cb-total-inflow').innerText = `₹${data.all_time.total_income.toLocaleString('en-IN')}`;
    document.getElementById('cb-total-outflow').innerText = `₹${data.all_time.total_expense.toLocaleString('en-IN')}`;
    document.getElementById('cb-net-surplus').innerText = `₹${data.all_time.net_balance.toLocaleString('en-IN')}`;
    document.getElementById('cb-weekly-inflow').innerText = `₹${data.weekly.income.toLocaleString('en-IN')}`;
    document.getElementById('cb-weekly-outflow').innerText = `₹${data.weekly.expense.toLocaleString('en-IN')}`;

    renderCashflowChart(data.daily_trends || []);
}

function renderCashflowChart(trends) {
    const ctx = document.getElementById('cashflow-canvas');
    if (!ctx) return;

    const labels = trends.map(t => t.date.slice(5));
    const incomeData = trends.map(t => t.day_income);
    const expenseData = trends.map(t => t.day_expense);

    if (cashflowChart) {
        cashflowChart.destroy();
    }

    const incomeLabel = currentLanguage === 'ta' ? 'வரவு (Income)' : 'Income';
    const expenseLabel = currentLanguage === 'ta' ? 'செலவு (Expense)' : 'Expense';

    cashflowChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: incomeLabel,
                    data: incomeData,
                    backgroundColor: '#10b981',
                    borderRadius: 4
                },
                {
                    label: expenseLabel,
                    data: expenseData,
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: val => '₹' + val
                    }
                }
            }
        }
    });
}

function renderCashbookTable(transactions) {
    const tbody = document.getElementById('cashbook-tbody');
    tbody.innerHTML = '';

    if (!transactions.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-400">${translations[currentLanguage]['empty_txns']}</td></tr>`;
        return;
    }

    transactions.forEach(t => {
        const isIncome = t.type === 'income';
        const typeBadge = isIncome
            ? `<span class="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800"><i class="fa-solid fa-arrow-down mr-1"></i> ${translations[currentLanguage]['income_label']}</span>`
            : `<span class="inline-flex items-center px-2 py-0.5 rounded-full bg-rose-100 text-rose-800"><i class="fa-solid fa-arrow-up mr-1"></i> ${translations[currentLanguage]['expense_label']}</span>`;

        const tr = document.createElement('tr');
        tr.className = "border-b border-slate-100 hover:bg-slate-50 transition-colors";
        tr.innerHTML = `
            <td class="py-3 px-4 text-sm font-medium text-slate-700">${t.date}</td>
            <td class="py-3 px-4 text-xs font-semibold">${typeBadge}</td>
            <td class="py-3 px-4 text-sm text-slate-800 font-medium">${t.category}</td>
            <td class="py-3 px-4 text-sm font-bold ${isIncome ? 'text-emerald-700' : 'text-rose-600'}">
                ${isIncome ? '+' : '-'}₹${t.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
            </td>
            <td class="py-3 px-4 text-xs text-slate-600">
                <span class="px-2 py-0.5 rounded bg-slate-100 font-medium">${t.payment_mode || 'Cash'}</span>
            </td>
            <td class="py-3 px-4 text-xs text-slate-500 max-w-xs truncate">${t.notes || '-'}</td>
            <td class="py-3 px-4 text-right">
                <button onclick="deleteCashTransaction(${t.id})" class="text-slate-400 hover:text-rose-600 p-1 transition-colors" title="Delete">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleAddTransaction(e) {
    e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const date = document.getElementById('txn-date').value;
    const type = document.getElementById('txn-type').value;
    const category = document.getElementById('txn-category').value;
    const amount = parseFloat(document.getElementById('txn-amount').value);
    const payment_mode = document.getElementById('txn-payment-mode').value;
    const notes = document.getElementById('txn-notes').value;

    if (!category) {
        alert(currentLanguage === 'ta' ? "தயவுசெய்து ஒரு பிரிவைத் தேர்ந்தெடுக்கவும்." : "Please select a category.");
        return;
    }

    try {
        const res = await fetch('/api/cashbook/transactions', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({ date, type, category, amount, payment_mode, notes })
        });
        const data = await res.json();
        if (data.success) {
            closeModal('txn-modal');
            showNotification(currentLanguage === 'ta' ? "பரிவர்த்தனை வெற்றிகரமாக பதிவு செய்யப்பட்டது!" : "Transaction recorded successfully!", "success");
            loadCashbookData();
        } else {
            alert(data.detail || "Error recording transaction");
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
}

async function deleteCashTransaction(id) {
    if (!confirm(currentLanguage === 'ta' ? "இப்பதிவை நீக்க உறுதி செய்கிறீர்களா?" : "Are you sure you want to delete this transaction?")) return;
    try {
        await fetch(`/api/cashbook/transactions/${id}`, { method: 'DELETE', headers: authHeaders() });
        loadCashbookData();
    } catch (e) {
        alert("Error deleting: " + e.message);
    }
}

function exportCashbookCSV() {
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }
    const token = getToken();
    window.location.href = `/api/cashbook/export-csv?auth_token=${token}`;
}

// --------------------------------------------------------------------------
// 7. Feature 5: Hyper-Local Market Analysis
// --------------------------------------------------------------------------
async function runMarketAnalysis(e) {
    if (e) e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const business_type = document.getElementById('market-biz-type').value;
    const village_town = document.getElementById('market-village').value;
    const district = document.getElementById('market-district').value;

    const btn = document.getElementById('market-analyze-btn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> ${currentLanguage === 'ta' ? 'சந்தையை பகுப்பாய்வு செய்கிறது...' : 'Analyzing local market dynamics...'}`;

    try {
        const res = await fetch('/api/market/analyze', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                business_type,
                village_town,
                district,
                language: currentLanguage
            })
        });
        const data = await res.json();
        renderMarketAnalysis(data.analysis);
    } catch (e) {
        alert("Market analysis error: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = translations[currentLanguage]['btn_analyze_market'];
    }
}

function renderMarketAnalysis(analysis) {
    document.getElementById('market-results-box').classList.remove('hidden');

    const segContainer = document.getElementById('market-segments-container');
    segContainer.innerHTML = '';
    analysis.customer_segments.forEach(seg => {
        const div = document.createElement('div');
        div.className = "bg-white p-4 rounded-xl border border-slate-200 shadow-sm";
        div.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <h4 class="font-bold text-slate-800">${seg.segment}</h4>
                <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">${seg.share}</span>
            </div>
            <p class="text-xs text-slate-600 leading-relaxed">${seg.buying_behavior}</p>
        `;
        segContainer.appendChild(div);
    });

    const seasonContainer = document.getElementById('market-seasonal-container');
    seasonContainer.innerHTML = '';
    analysis.seasonal_demand.forEach(s => {
        const div = document.createElement('div');
        div.className = "bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between";
        div.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-1">
                    <h4 class="font-bold text-slate-800 text-sm">${s.season}</h4>
                    <span class="text-xs font-extrabold text-amber-600">${s.demand_level}</span>
                </div>
                <div class="text-xs font-semibold text-emerald-700 mb-2">${s.impact}</div>
                <p class="text-xs text-slate-600 leading-relaxed">${s.recommendation}</p>
            </div>
        `;
        seasonContainer.appendChild(div);
    });

    const surveyContainer = document.getElementById('market-survey-container');
    surveyContainer.innerHTML = '';
    const isTa = currentLanguage === 'ta';

    analysis.survey_questions.forEach(q => {
        const questionText = isTa ? q.ta : q.en;
        const div = document.createElement('div');
        div.className = "p-3 bg-slate-50 rounded-lg border border-slate-200 text-sm";
        div.innerHTML = `
            <div class="font-semibold text-slate-800 mb-1.5">Q${q.q_no}: ${questionText}</div>
            <div class="grid grid-cols-2 gap-2 text-xs text-slate-600">
                ${q.options.map(opt => `<div class="flex items-center"><span class="w-3 h-3 rounded-full border border-slate-400 mr-1.5 inline-block"></span> ${opt}</div>`).join('')}
            </div>
        `;
        surveyContainer.appendChild(div);
    });
}

function printSurveyQuestionnaire() {
    window.print();
}

// --------------------------------------------------------------------------
// 8. Feature 6: Smart Pricing Assistant
// --------------------------------------------------------------------------
async function runSmartPricing(e) {
    if (e) e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const product_name = document.getElementById('price-product-name').value;
    const raw_material_cost = parseFloat(document.getElementById('price-cost-raw').value) || 0;
    const direct_labor_cost = parseFloat(document.getElementById('price-cost-labor').value) || 0;
    const packaging_cost = parseFloat(document.getElementById('price-cost-pkg').value) || 0;
    const utilities_and_fuel = parseFloat(document.getElementById('price-cost-util').value) || 0;
    const other_overhead = parseFloat(document.getElementById('price-cost-ovh').value) || 0;
    const target_margin_pct = parseFloat(document.getElementById('price-target-margin').value) || 25;
    const competitor_market_price = parseFloat(document.getElementById('price-competitor').value) || null;

    try {
        const res = await fetch('/api/finance/pricing', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                product_name,
                raw_material_cost,
                direct_labor_cost,
                packaging_cost,
                utilities_and_fuel,
                other_overhead,
                target_margin_pct,
                competitor_market_price
            })
        });
        const data = await res.json();
        renderPricingResults(data.product_name, data.pricing);
    } catch (err) {
        alert("Pricing calculation error: " + err.message);
    }
}

function renderPricingResults(productName, p) {
    document.getElementById('pricing-results-box').classList.remove('hidden');

    document.getElementById('res-total-unit-cost').innerText = `₹${p.cost_breakdown.total_unit_cost.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('res-suggested-price').innerText = `₹${p.pricing_summary.suggested_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('res-profit-unit').innerText = `₹${p.pricing_summary.profit_per_unit.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('res-markup-pct').innerText = `${p.pricing_summary.markup_pct}%`;
    document.getElementById('res-actual-margin').innerText = `${p.pricing_summary.profit_margin_pct}%`;

    document.getElementById('tier-penetration').innerText = `₹${p.price_tiers.penetration_price.toFixed(2)}`;
    document.getElementById('tier-standard').innerText = `₹${p.price_tiers.recommended_price.toFixed(2)}`;
    document.getElementById('tier-premium').innerText = `₹${p.price_tiers.premium_price.toFixed(2)}`;

    const compBox = document.getElementById('pricing-competitor-box');
    if (p.competitor_comparison) {
        compBox.classList.remove('hidden');
        document.getElementById('comp-difference').innerText = `₹${p.competitor_comparison.difference_amount > 0 ? '+' : ''}${p.competitor_comparison.difference_amount.toFixed(2)} (${p.competitor_comparison.difference_pct}%)`;
        document.getElementById('comp-verdict').innerText = `${p.competitor_comparison.competitiveness} — ${p.competitor_comparison.advice}`;
    } else {
        compBox.classList.add('hidden');
    }
}

// --------------------------------------------------------------------------
// 9. Feature 7: AI Advisory Chatbot
// --------------------------------------------------------------------------
function updateQuickPrompts(lang) {
    const isTa = lang === 'ta';
    const container = document.getElementById('quick-prompts-container');
    if (!container) return;

    const prompts = isTa ? [
        { label: "முத்ரா கடன் வழிகாட்டி", query: "முத்ரா கடன் எப்படி வாங்குவது? என்ன ஆவணங்கள் தேவை?" },
        { label: "நாட்டுக்கோழி பண்ணை", query: "₹25,000 முதலீட்டில் நாட்டுக்கோழி பண்ணை ஆரம்பிக்க வழிகாட்டி" },
        { label: "விலை நிர்ணய சூத்திரம்", query: "25% லாப வரம்பில் விற்பனை விலையை எப்படி கணக்கிடுவது?" },
        { label: "நடைமுறை மூலதனம்", query: "நடைமுறை மூலதனம் (Working Capital) என்றால் என்ன?" }
    ] : [
        { label: "MUDRA Loan Guide", query: "What is MUDRA loan and how to apply?" },
        { label: "Country Poultry Farm", query: "How to start country chicken farm with ₹25,000?" },
        { label: "Pricing Formula", query: "How to calculate product price with 25% margin?" },
        { label: "Working Capital", query: "What is working capital in simple terms?" }
    ];

    container.innerHTML = `
        <span class="text-slate-400 font-semibold flex-shrink-0" data-i18n="quick_prompts">${translations[lang]['quick_prompts']}</span>
        ${prompts.map(p => `
            <button onclick="sendQuickPrompt('${p.query}')" class="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 whitespace-nowrap transition-colors text-xs font-medium">
                ${p.label}
            </button>
        `).join('')}
    `;
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    appendChatMessage(msg, 'user');
    input.value = '';

    const apiKey = localStorage.getItem('user_gemini_key') || null;
    const typingId = appendChatTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                language: currentLanguage,
                api_key: apiKey
            })
        });
        const data = await res.json();
        removeChatTyping(typingId);
        appendChatMessage(data.reply, 'assistant');
    } catch (e) {
        removeChatTyping(typingId);
        appendChatMessage("Sorry, an error occurred: " + e.message, 'assistant');
    }
}

function appendChatMessage(text, role) {
    const container = document.getElementById('chat-messages-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex gap-3 mb-4 ${role === 'user' ? 'justify-end' : 'justify-start'}`;

    const formattedText = marked ? marked.parse(text) : text.replace(/\n/g, '<br/>');

    if (role === 'user') {
        msgDiv.innerHTML = `
            <div class="max-w-[80%] bg-emerald-700 text-white rounded-2xl rounded-tr-none px-4 py-3 shadow-sm text-sm">
                ${text}
            </div>
            <div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold text-xs flex-shrink-0">
                You
            </div>
        `;
    } else {
        msgDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="max-w-[80%] bg-white border border-slate-200 text-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm text-sm leading-relaxed prose prose-sm">
                ${formattedText}
            </div>
        `;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function appendChatTyping() {
    const container = document.getElementById('chat-messages-container');
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = "flex gap-3 mb-4 justify-start";
    div.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bg-white border border-slate-200 text-slate-400 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm text-sm flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.2s"></span>
            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.4s"></span>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeChatTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function sendQuickPrompt(promptText) {
    document.getElementById('chat-input').value = promptText;
    sendChatMessage();
}

// --------------------------------------------------------------------------
// 10. Feature 8: Business Plan Generator
// --------------------------------------------------------------------------
let currentBusinessPlan = null;

async function runBusinessPlanGenerator(e) {
    if (e) e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const title = document.getElementById('plan-input-title').value;
    const category = document.getElementById('plan-input-category').value;
    const location = document.getElementById('plan-input-location').value || (currentUser.village_town + ', ' + currentUser.district);
    const startup_budget = parseFloat(document.getElementById('plan-input-investment').value) || 35000;
    const monthly_sales_target = parseFloat(document.getElementById('plan-input-sales').value) || 45000;

    const btn = document.getElementById('plan-generate-btn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> ${currentLanguage === 'ta' ? 'திட்ட அறிக்கை தயாரிக்கப்படுகிறது...' : 'Drafting comprehensive business plan...'}`;

    try {
        const res = await fetch('/api/plans/generate', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                title, category, location,
                startup_budget, monthly_sales_target,
                language: currentLanguage
            })
        });
        const data = await res.json();
        currentBusinessPlan = data.plan;
        renderBusinessPlan(currentBusinessPlan);
    } catch (e) {
        alert("Error generating plan: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = translations[currentLanguage]['btn_generate_plan'];
    }
}

function renderBusinessPlan(plan) {
    document.getElementById('plan-results-box').classList.remove('hidden');
    document.getElementById('plan-display-title').innerText = plan.metadata.title;
    
    const isTa = currentLanguage === 'ta';
    const prepLabel = translations[currentLanguage]['meta_prepared_for'];
    const locLabel = translations[currentLanguage]['meta_location'];
    const invLabel = translations[currentLanguage]['meta_investment'];

    document.getElementById('plan-display-meta').innerText = `${prepLabel} ${plan.metadata.owner} | ${locLabel} ${plan.metadata.location} | ${invLabel} ₹${plan.metadata.startup_capital.toLocaleString('en-IN')}`;

    const container = document.getElementById('plan-sections-container');
    container.innerHTML = '';

    plan.sections.forEach((sec, idx) => {
        const div = document.createElement('div');
        div.className = "bg-white p-5 rounded-xl border border-slate-200 shadow-sm";
        div.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <h4 class="font-bold text-slate-800 text-base">${sec.title}</h4>
                <span class="text-xs text-slate-400 font-mono">${isTa ? 'பகுதி ' + (idx + 1) : 'Section ' + (idx + 1)}</span>
            </div>
            <textarea id="plan-section-text-${idx}" class="w-full text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg p-3 font-sans leading-relaxed focus:bg-white focus:outline-emerald-600 focus:ring-1 focus:ring-emerald-600 transition-colors" rows="4">${sec.content}</textarea>
        `;
        container.appendChild(div);
    });
}

async function saveCurrentBusinessPlan() {
    if (!currentBusinessPlan || !currentUser) return;

    currentBusinessPlan.sections.forEach((sec, idx) => {
        const ta = document.getElementById(`plan-section-text-${idx}`);
        if (ta) sec.content = ta.value;
    });

    try {
        const res = await fetch('/api/plans/save', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                title: currentBusinessPlan.metadata.title,
                business_category: currentBusinessPlan.metadata.category,
                location: currentBusinessPlan.metadata.location,
                startup_cost: currentBusinessPlan.metadata.startup_capital,
                plan_data: currentBusinessPlan
            })
        });
        const data = await res.json();
        if (data.success) {
            showNotification(currentLanguage === 'ta' ? "திட்ட அறிக்கை சேமிக்கப்பட்டது!" : "Business plan saved successfully!", "success");
        }
    } catch (e) {
        alert("Error saving plan: " + e.message);
    }
}

function printBusinessPlan() {
    window.print();
}

// --------------------------------------------------------------------------
// 11. Feature 9: Microloan Readiness Assistant
// --------------------------------------------------------------------------
const docCatTranslations = {
    "Identity & Address": { en: "Identity & Address", ta: "அடையாளம் & முகவரி" },
    "Financial Identity": { en: "Financial Identity", ta: "நிதி அடையாளம் (PAN)" },
    "Financial Record": { en: "Financial Record", ta: "வங்கி கணக்கு புத்தகம்" },
    "Identity": { en: "Identity", ta: "புகைப்படம்" },
    "Business Proof": { en: "Business Proof", ta: "வணிக பதிவு சான்று (Udyam)" },
    "Project Cost": { en: "Project Cost", ta: "இயந்திர விலைப்புள்ளி (Quotation)" },
    "Project Feasibility": { en: "Project Feasibility", ta: "திட்ட அறிக்கை (Project Report)" },
    "Business Location": { en: "Business Location", ta: "இட வாடகை / வரி ரசீது" }
};

async function loadLoanSchemesAndChecklist() {
    try {
        const [cRes, sRes] = await Promise.all([
            fetch('/api/loan/checklist'),
            fetch('/api/loan/schemes')
        ]);
        if (cRes.ok && sRes.ok) {
            const cData = await cRes.json();
            const sData = await sRes.json();
            cachedChecklist = cData.checklist;
            cachedSchemes = sData.schemes;
            renderLoanChecklist(cachedChecklist);
            renderLoanSchemes(cachedSchemes);
        }
    } catch (e) {
        console.error("Loan data load error:", e);
    }
}

function renderLoanChecklist(docs) {
    const container = document.getElementById('loan-checklist-container');
    container.innerHTML = '';
    const isTa = currentLanguage === 'ta';

    docs.forEach(d => {
        const catName = (docCatTranslations[d.category] && docCatTranslations[d.category][currentLanguage])
            ? docCatTranslations[d.category][currentLanguage]
            : d.category;

        const div = document.createElement('label');
        div.className = "flex items-start p-3 bg-white border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors";
        div.innerHTML = `
            <input type="checkbox" value="${d.id}" class="loan-doc-checkbox mt-1 h-4 w-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500" ${d.mandatory ? 'checked' : ''} onchange="updateCheckedDocsCount()" />
            <div class="ml-3 text-sm">
                <span class="font-medium text-slate-800">${d.title}</span>
                <span class="ml-2 text-xs font-semibold ${d.mandatory ? 'text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded' : 'text-slate-500'}">
                    ${d.mandatory ? (isTa ? 'அவசியம்' : 'Mandatory') : (isTa ? 'கூடுதல் பலன்' : 'Optional')}
                </span>
                <div class="text-xs text-slate-500">${catName}</div>
            </div>
        `;
        container.appendChild(div);
    });
    updateCheckedDocsCount();
}

function updateCheckedDocsCount() {
    const checked = document.querySelectorAll('.loan-doc-checkbox:checked').length;
    const total = cachedChecklist.length || 8;
    const badge = document.getElementById('docs-count-badge');
    if (badge) {
        badge.innerText = currentLanguage === 'ta' ? `${checked} / ${total} தயார்` : `${checked} / ${total} Ready`;
    }
}

function renderLoanSchemes(schemes) {
    const container = document.getElementById('loan-schemes-container');
    container.innerHTML = '';
    const isTa = currentLanguage === 'ta';

    schemes.forEach(s => {
        const div = document.createElement('div');
        div.className = "bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between";
        
        const maxAmtText = isTa ? `₹${(s.max_amount / 100000).toFixed(1)} லட்சம் வரை` : `Up to ₹${(s.max_amount / 100000).toFixed(1)} Lakhs`;
        const feeText = isTa ? (s.processing_fee === 'NIL' ? 'கட்டணம் இல்லை (இலவசம்)' : s.processing_fee) : s.processing_fee;
        const tenureText = isTa ? s.tenure.replace('years', 'ஆண்டுகள்').replace('year', 'ஆண்டு') : s.tenure;

        div.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-bold text-slate-900 text-sm">${s.name}</h4>
                    <span class="px-2 py-0.5 rounded text-xs font-extrabold bg-emerald-100 text-emerald-800">${maxAmtText}</span>
                </div>
                <p class="text-xs text-slate-600 mb-2 leading-relaxed">${isTa ? (s.ta_best_for || s.best_for) : s.best_for}</p>
                <div class="text-xs text-slate-500"><i class="fa-solid fa-gift text-emerald-600 mr-1"></i> ${s.subsidy}</div>
            </div>
            <div class="pt-3 border-t border-slate-100 mt-2 flex justify-between text-xs text-slate-500 font-medium">
                <span>${isTa ? 'கட்டணம்: ' : 'Fee: '}${feeText}</span>
                <span>${isTa ? 'கால அளவு: ' : 'Tenure: '}${tenureText}</span>
            </div>
        `;
        container.appendChild(div);
    });
}

async function runLoanAssessment(e) {
    if (e) e.preventDefault();
    if (!currentUser) {
        openModal('auth-modal');
        return;
    }

    const requested_amount = parseFloat(document.getElementById('loan-input-amount').value) || 50000;
    const monthly_net_profit = parseFloat(document.getElementById('loan-input-profit').value) || 18000;
    const existing_emi = parseFloat(document.getElementById('loan-input-emi').value) || 0;
    const has_existing_loan = existing_emi > 0;

    const checked_documents = Array.from(document.querySelectorAll('.loan-doc-checkbox:checked')).map(cb => cb.value);

    try {
        const res = await fetch('/api/loan/assess', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                requested_amount,
                monthly_net_profit,
                checked_documents,
                has_existing_loan,
                existing_emi
            })
        });
        const data = await res.json();
        renderLoanAssessmentResults(data.assessment);
    } catch (err) {
        alert("Loan assessment error: " + err.message);
    }
}

function renderLoanAssessmentResults(a) {
    document.getElementById('loan-results-box').classList.remove('hidden');

    const isTa = currentLanguage === 'ta';
    document.getElementById('res-loan-score').innerText = `${a.score} / 100`;
    
    document.getElementById('res-loan-grade').innerText = isTa
        ? (a.score >= 80 ? 'அதிக ஒப்புதல் வாய்ப்பு (High Likelihood)' : (a.score >= 60 ? 'நடுத்தர வாய்ப்பு (Good Likelihood)' : 'தயாரிப்பு தேவை (Needs Preparation)'))
        : a.grade;

    document.getElementById('res-banker-verdict').innerText = isTa
        ? (a.score >= 80 ? 'உங்கள் திட்ட அறிக்கை மற்றும் ஆவணங்கள் வங்கி கடன் பெற மிகவும் தகுதியாக உள்ளன! மாதாந்திர தவணையை எளிதில் செலுத்தும் நிதி உபரி உள்ளது.'
          : (a.score >= 60 ? 'உங்கள் விண்ணப்பம் பரிசீலிக்கப்படலாம். அசல் இயந்திர விலைப்புள்ளி (Quotation) மற்றும் உத்யம் பதிவை இணைப்பது கடனை விரைவாக பெற உதவும்.'
          : 'வங்கி மேலாளரை திருப்திப்படுத்த விடுபட்ட கட்டாய ஆவணங்களை தயார் செய்து விற்பனை கணிப்புகளை மேம்படுத்துங்கள்.'))
        : a.banker_verdict;

    document.getElementById('res-loan-emi').innerText = `₹${a.estimated_monthly_emi.toLocaleString('en-IN')}`;
    
    const dscrStatus = isTa
        ? (a.dscr_ratio >= 2.0 ? 'மிக ஆரோக்கியமானது' : (a.dscr_ratio >= 1.2 ? 'ஏற்றுக்கொள்ளத்தக்கது' : 'அபாயகரமானது'))
        : a.dscr_health;
    document.getElementById('res-dscr-ratio').innerText = `${a.dscr_ratio}x (${dscrStatus})`;

    const scoreBar = document.getElementById('loan-score-bar');
    if (scoreBar) {
        scoreBar.style.width = `${a.score}%`;
        scoreBar.className = `h-3 rounded-full ${a.score >= 80 ? 'bg-emerald-600' : (a.score >= 60 ? 'bg-blue-600' : 'bg-amber-500')}`;
    }
}

// --------------------------------------------------------------------------
// 12. Dashboard Overview Summary
// --------------------------------------------------------------------------
async function loadDashboardSummary() {
    if (!currentUser) return;
    try {
        const sumRes = await fetch('/api/cashbook/summary', { headers: authHeaders() });
        if (sumRes.ok) {
            const data = await sumRes.json();
            const dashBalance = document.getElementById('dash-net-balance');
            const dashIncome = document.getElementById('dash-month-income');
            if (dashBalance) dashBalance.innerText = `₹${data.all_time.net_balance.toLocaleString('en-IN')}`;
            if (dashIncome) dashIncome.innerText = `₹${data.monthly.income.toLocaleString('en-IN')}`;
        }
    } catch (e) {}
}

// --------------------------------------------------------------------------
// 13. UI Helpers, Modals & Toast Notifications
// --------------------------------------------------------------------------
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('hidden');
    if (id === 'txn-modal') {
        populateCategoryDropdown();
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden');
}

function toggleAuthTab(type) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('reg-form');
    const tabLogin = document.getElementById('auth-tab-login');
    const tabReg = document.getElementById('auth-tab-reg');

    if (type === 'login') {
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
        tabLogin.classList.add('text-emerald-700', 'border-b-2', 'border-emerald-700', 'font-bold');
        tabReg.classList.remove('text-emerald-700', 'border-b-2', 'border-emerald-700', 'font-bold');
    } else {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        tabReg.classList.add('text-emerald-700', 'border-b-2', 'border-emerald-700', 'font-bold');
        tabLogin.classList.remove('text-emerald-700', 'border-b-2', 'border-emerald-700', 'font-bold');
    }
}

function showNotification(msg, type = "info") {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium flex items-center space-x-2 transition-all transform duration-300 ${
        type === 'success' ? 'bg-emerald-800 text-white' : (type === 'error' ? 'bg-rose-700 text-white' : 'bg-slate-800 text-white')
    }`;
    toast.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check text-emerald-400' : 'fa-circle-info'} mr-2"></i> ${msg}`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function openSettingsModal() {
    const key = localStorage.getItem('user_gemini_key') || '';
    const input = document.getElementById('settings-gemini-key');
    if (input) input.value = key;
    openModal('settings-modal');
}

function saveGeminiSettings(e) {
    e.preventDefault();
    const val = document.getElementById('settings-gemini-key').value.trim();
    if (val) {
        localStorage.setItem('user_gemini_key', val);
        showNotification(currentLanguage === 'ta' ? "Gemini API சாவி சேமிக்கப்பட்டது!" : "Gemini API key saved!", "success");
    } else {
        localStorage.removeItem('user_gemini_key');
        showNotification(currentLanguage === 'ta' ? "Gemini API சாவி நீக்கப்பட்டது (உள்ளமைக்கப்பட்ட வழிகாட்டி பயன்படுத்தப்படும்)" : "Gemini API key cleared (using built-in rural intelligence)", "info");
    }
    closeModal('settings-modal');
}

function setupEventListeners() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const regForm = document.getElementById('reg-form');
    if (regForm) regForm.addEventListener('submit', handleRegister);

    const txnForm = document.getElementById('txn-form');
    if (txnForm) txnForm.addEventListener('submit', handleAddTransaction);

    const calcForm = document.getElementById('calc-form');
    if (calcForm) calcForm.addEventListener('submit', runFinancialCalculator);

    const priceForm = document.getElementById('pricing-form');
    if (priceForm) priceForm.addEventListener('submit', runSmartPricing);

    const planForm = document.getElementById('plan-form');
    if (planForm) planForm.addEventListener('submit', runBusinessPlanGenerator);

    const loanForm = document.getElementById('loan-form');
    if (loanForm) loanForm.addEventListener('submit', runLoanAssessment);

    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendChatMessage();
        });
    }

    const dateInput = document.getElementById('txn-date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Populate category dropdown initially
    populateCategoryDropdown();
    updateQuickPrompts(currentLanguage);
}
