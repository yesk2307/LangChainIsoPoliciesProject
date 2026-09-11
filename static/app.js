// ==========================================================================
// ISO Policies Assistant — Frontend Controller
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  const queryForm = document.getElementById('queryForm');
  const queryInput = document.getElementById('queryInput');
  const submitBtn = document.getElementById('submitBtn');
  const messagesArea = document.getElementById('messagesArea');
  const welcomeCard = document.getElementById('welcomeCard');
  const suggestionChips = document.querySelectorAll('.suggestion-chip');
  
  // Policy Catalog Modal elements
  const catalogModal = document.getElementById('catalogModal');
  const openCatalogBtn = document.getElementById('openCatalogBtn');
  const closeCatalogBtn = document.getElementById('closeCatalogBtn');
  const policyList = document.getElementById('policyList');
  const policySearchInput = document.getElementById('policySearchInput');
  const statusCount = document.getElementById('statusCount');

  let policiesCache = [];

  // 1. Auto-resize textarea
  queryInput.addEventListener('input', () => {
    queryInput.style.height = 'auto';
    queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + 'px';
  });

  // Handle Enter to submit (Shift+Enter for newline)
  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (queryInput.value.trim() && !submitBtn.disabled) {
        queryForm.dispatchEvent(new Event('submit'));
      }
    }
  });

  // 2. Click on suggested chips
  suggestionChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const queryText = chip.getAttribute('data-query');
      if (queryText) {
        queryInput.value = queryText;
        queryForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  // 3. Form Submit / Query Execution
  queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = queryInput.value.trim();
    if (!question) return;

    // Hide welcome hero on first query
    if (welcomeCard) {
      welcomeCard.style.display = 'none';
    }

    // Append user message
    appendUserMessage(question);
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // Disable input while processing
    setInputLoading(true);

    // Append loading placeholder
    const loadingId = appendLoadingMessage();

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Network error' }));
        throw new Error(errData.detail || 'Failed to process request');
      }

      const data = await response.json();
      removeLoadingMessage(loadingId);
      appendAssistantMessage(data.answer, data.sources);
    } catch (err) {
      removeLoadingMessage(loadingId);
      appendAssistantMessage(
        `⚠️ **Error:** ${err.message}\n\nPlease verify that the server is running and your \`GOOGLE_API_KEY\` is active in \`.env\`.`,
        []
      );
    } finally {
      setInputLoading(false);
      queryInput.focus();
    }
  });

  function setInputLoading(loading) {
    submitBtn.disabled = loading;
    queryInput.disabled = loading;
  }

  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row user';
    row.innerHTML = `
      <div class="message-avatar">You</div>
      <div class="message-bubble">${escapeHtml(text)}</div>
    `;
    messagesArea.appendChild(row);
    scrollToBottom();
  }

  function appendLoadingMessage() {
    const id = 'loading-' + Date.now();
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = id;
    row.innerHTML = `
      <div class="message-avatar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
      </div>
      <div class="message-bubble loading-bubble">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
      </div>
    `;
    messagesArea.appendChild(row);
    scrollToBottom();
    return id;
  }

  function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendAssistantMessage(markdownText, sources = []) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    // Parse Markdown safely
    let htmlContent = '';
    if (typeof marked !== 'undefined' && marked.parse) {
      htmlContent = marked.parse(markdownText);
    } else {
      htmlContent = `<p>${escapeHtml(markdownText)}</p>`;
    }

    // Format source badges
    let sourcesHtml = '';
    if (sources && sources.length > 0) {
      // Deduplicate sources by policy and page
      const uniqueSources = [];
      const seen = new Set();
      sources.forEach(s => {
        const key = `${s.policy}-${s.page}`;
        if (!seen.has(key)) {
          seen.add(key);
          uniqueSources.push(s);
        }
      });

      const badges = uniqueSources.map(s => `
        <span class="source-badge" title="${escapeHtml(s.snippet || '')}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          ${escapeHtml(s.policy)} (p. ${s.page})
        </span>
      `).join('');

      sourcesHtml = `
        <div class="sources-card">
          <div class="sources-header">Verified Policy Citations</div>
          <div class="sources-chips">${badges}</div>
        </div>
      `;
    }

    row.innerHTML = `
      <div class="message-avatar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="M9 12l2 2 4-4"/>
        </svg>
      </div>
      <div class="message-bubble">
        <div class="markdown-body">${htmlContent}</div>
        ${sourcesHtml}
      </div>
    `;

    messagesArea.appendChild(row);
    scrollToBottom();
  }

  function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // 4. Policy Catalog Modal Logic
  async function loadPoliciesCatalog() {
    try {
      const res = await fetch('/api/policies');
      if (!res.ok) throw new Error('Failed to load policies');
      policiesCache = await res.json();
      renderPolicies(policiesCache);
      if (statusCount) {
        statusCount.textContent = `${policiesCache.length} Policies Indexed`;
      }
    } catch (err) {
      policyList.innerHTML = `<li class="policy-item">Failed to load policies: ${err.message}</li>`;
    }
  }

  function renderPolicies(items) {
    if (items.length === 0) {
      policyList.innerHTML = `<li class="policy-item">No matching policies found.</li>`;
      return;
    }

    policyList.innerHTML = items.map(p => `
      <li class="policy-item">
        <div class="policy-item-name">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          ${escapeHtml(p.filename)}
        </div>
        <span class="policy-size">${p.size_kb} KB</span>
      </li>
    `).join('');
  }

  policySearchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase().trim();
    const filtered = policiesCache.filter(p => p.filename.toLowerCase().includes(term));
    renderPolicies(filtered);
  });

  openCatalogBtn.addEventListener('click', () => {
    catalogModal.classList.add('open');
    if (policiesCache.length === 0) {
      loadPoliciesCatalog();
    }
  });

  closeCatalogBtn.addEventListener('click', () => {
    catalogModal.classList.remove('open');
  });

  catalogModal.addEventListener('click', (e) => {
    if (e.target === catalogModal) {
      catalogModal.classList.remove('open');
    }
  });

  // Preload policy count
  loadPoliciesCatalog();
});
