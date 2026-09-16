// DOSSIÊ JURÍDICO: CASTELLANO x CARUSO — INTERACTIVE ENGINE

// --- AUTHENTICATION GATE (STJ REsp 1.903.366/PR Protection) ---
const AUTH_KEY = 'dossier_auth_status';
const VALID_PASSWORD = 'senha123';

function checkAuth() {
  const isAuth = sessionStorage.getItem(AUTH_KEY) === 'authenticated';
  const gate = document.getElementById('auth-gate');
  if (isAuth && gate) {
    gate.classList.add('hidden');
  } else if (gate) {
    gate.classList.remove('hidden');
    const pwdInput = document.getElementById('auth-password');
    if (pwdInput) setTimeout(() => pwdInput.focus(), 150);
  }
}

window.handleAuthSubmit = function(e) {
  if (e) e.preventDefault();
  const pwdInput = document.getElementById('auth-password');
  const errorEl = document.getElementById('auth-error');
  if (!pwdInput) return;

  if (pwdInput.value === VALID_PASSWORD) {
    sessionStorage.setItem(AUTH_KEY, 'authenticated');
    const gate = document.getElementById('auth-gate');
    if (gate) {
      gate.style.opacity = '0';
      gate.style.transition = 'opacity 0.3s ease';
      setTimeout(() => gate.classList.add('hidden'), 300);
    }
    if (errorEl) errorEl.textContent = '';
  } else {
    if (errorEl) {
      errorEl.textContent = '❌ Senha incorreta. Acesso não autorizado.';
      pwdInput.classList.add('shake');
      setTimeout(() => pwdInput.classList.remove('shake'), 400);
    }
  }
};

window.lockDossier = function() {
  sessionStorage.removeItem(AUTH_KEY);
  const pwdInput = document.getElementById('auth-password');
  if (pwdInput) pwdInput.value = '';
  checkAuth();
};

document.addEventListener('DOMContentLoaded', () => {
  checkAuth();

  const data = window.DOSSIER_DATA;
  if (!data) {
    console.error('DOSSIER_DATA not found.');
    return;
  }

  // --- 1. RENDER TIMELINE BLOCKS ---
  const timelineContainer = document.getElementById('timeline-blocks-container');
  let currentFilter = 'TODOS';
  let searchQuery = '';

  function renderTimeline() {
    timelineContainer.innerHTML = '';

    let totalRenderedEvents = 0;

    data.blocks.forEach(block => {
      // Filter events in block
      const filteredEvents = block.events.filter(ev => {
        // Tag filter
        if (currentFilter !== 'TODOS') {
          const tList = ev.tags || [];
          let matches = false;
          if (currentFilter === 'FINANCEIRO') {
            matches = tList.some(t => t.includes('FINANCEIRO') || t === 'COMPROVANTE_OFICIAL' || t === 'PROPOSTA_SOO_TECH');
          } else if (currentFilter === 'CONTRATO') {
            matches = tList.some(t => t.includes('CONTRATO') || t === 'PROPOSTA_SOO_TECH' || t === 'PARCERIA_COMERCIAL');
          } else if (currentFilter === 'AMEACA_DISPUTA') {
            matches = tList.some(t => t.includes('AMEACA') || t.includes('DISPUTA') || t.includes('PROTETIVA') || t === 'CRIME');
          } else if (currentFilter === 'CARRO_DIVIDA') {
            matches = tList.some(t => t.includes('CARRO'));
          } else if (currentFilter === 'HOSPITAL_SAUDE') {
            matches = tList.some(t => t.includes('HOSPITAL') || t.includes('SAUDE')) || (ev.attachment && ev.attachment.toLowerCase().includes('internac'));
          } else {
            matches = tList.includes(currentFilter);
          }
          if (!matches) return false;
        }
        // Search query
        if (searchQuery.trim() !== '') {
          const q = searchQuery.toLowerCase();
          const matchesContent = ev.content.toLowerCase().includes(q);
          const matchesTranscription = ev.audio_transcription && ev.audio_transcription.toLowerCase().includes(q);
          const matchesAuthor = ev.author.toLowerCase().includes(q);
          const matchesAtt = ev.attachment && ev.attachment.toLowerCase().includes(q);
          return matchesContent || matchesTranscription || matchesAuthor || matchesAtt;
        }
        return true;
      });

      if (filteredEvents.length === 0 && (currentFilter !== 'TODOS' || searchQuery.trim() !== '')) {
        return; // Skip empty block during filter
      }

      totalRenderedEvents += filteredEvents.length;

      const blockEl = document.createElement('div');
      blockEl.className = 'timeline-block';
      blockEl.id = block.id;

      let eventsHtml = '';
      filteredEvents.forEach(ev => {
        const isGustavo = ev.author.toLowerCase().includes('gustavo');
        const authorClass = isGustavo ? 'gustavo' : 'camila';
        const isCritical = ev.tags.includes('AMEACA_DISPUTA') || ev.tags.includes('FINANCEIRO');
        const critClass = isCritical ? 'crit' : '';

        // Attachment badge/media
        let attHtml = '';
        if (ev.attachment) {
          if (ev.attachment.endsWith('.opus') && ev.audio_transcription) {
            attHtml = `
              <div class="event-audio-box">
                <div style="font-size:11px;color:var(--text-dim);margin-bottom:4px;">
                  🎙️ <strong>Áudio Oficial do WhatsApp</strong> (${ev.attachment})
                </div>
                <audio controls preload="none" src="${ev.attachment}"></audio>
                <div class="event-transcription">
                  <strong>Transcrição Oficial (Whisper):</strong> "${escapeHtml(ev.audio_transcription)}"
                </div>
              </div>
            `;
          } else if (ev.attachment.toLowerCase().match(/\.(jpg|jpeg|png|webp)$/)) {
            attHtml = `
              <div class="event-attachment">
                <span>📎 Imagem anexada: <strong>${ev.attachment}</strong></span>
                <button class="filter-btn" onclick="openLightboxImage('${ev.attachment}')">Visualizar</button>
              </div>
            `;
          } else {
            attHtml = `
              <div class="event-attachment">
                <span>📄 Documento anexado: <strong>${escapeHtml(ev.attachment)}</strong></span>
                <button class="filter-btn" onclick="openLightboxImage('${escapeHtml(ev.attachment)}')">📄 Visualizar Documento</button>
              </div>
            `;
          }
        }

        // Tags & Custom Badges
        let tagsHtml = '';
        if (ev.custom_badge) {
          tagsHtml += `<span class="badge blue" style="background:rgba(59,130,246,0.2);border:1px solid #3b82f6;color:#93c5fd;font-weight:700;">💼 ${escapeHtml(ev.custom_badge)}</span> `;
        }
        const seenLabels = new Set();
        tagsHtml += ev.tags
          .filter(t => !ev.custom_badge || t !== 'PROPOSTA_SOO_TECH')
          .map(t => {
            let label = t;
            let badgeColor = 'blue';
            if (t === 'PROPOSTA_SOO_TECH') { label = '💼 Proposta Soo Tech (João, Victor e Gustavo)'; badgeColor = 'blue'; }
            else if (t === 'COMPROVANTE_OFICIAL') { label = '📑 Comprovante Oficial'; badgeColor = 'green'; }
            else if (t === 'FINANCEIRO' || t === 'FINANCEIRO_APORTE') { label = '💳 Aporte Financeiro'; badgeColor = 'green'; }
            else if (t === 'CARRO_DIVIDA' || t === 'CARRO_DIVIDA_RE') { label = '🚗 Dívida do Carro (Ré)'; badgeColor = 'amber'; }
            else if (t === 'CONTRATO' || t === 'CONTRATO_DIVIDA') { label = '📝 Contrato / Confissão de Dívida'; badgeColor = 'blue'; }
            else if (t === 'HOSPITAL_SAUDE') { label = '🏥 Internação / Saúde'; badgeColor = 'amber'; }
            else if (t === 'FALSA_MEDIDA_PROTETIVA') { label = '🚨 AMEAÇA: FALSA MEDIDA PROTETIVA'; badgeColor = 'red'; }
            else if (t === 'CRIME') { label = '⚖️ Notícia-Crime / Art. 171'; badgeColor = 'red'; }
            else if (t === 'PARCERIA_COMERCIAL') { label = '🤝 Parceria Comercial'; badgeColor = 'blue'; }
            else if (t === 'AMEACA_DISPUTA' || t === 'JURIDICO_DISPUTA') { label = '⚖️ Cobrança / Notificação'; badgeColor = 'amber'; }
            
            if (seenLabels.has(label)) return '';
            seenLabels.add(label);
            return `<span class="badge ${badgeColor}">${label}</span>`;
          }).join(' ');

        let noteHtml = '';
        if (ev.custom_note) {
          noteHtml = `
            <div class="custom-forensic-note" style="margin-top:10px;padding:10px 14px;background:rgba(30,41,59,0.7);border-left:3px solid #60a5fa;border-radius:4px;font-size:12.5px;color:#cbd5e1;line-height:1.5;">
              <strong style="color:#60a5fa;">Nota Contextual:</strong> ${escapeHtml(ev.custom_note)}
            </div>
          `;
        }

        eventsHtml += `
          <div class="event-item ${critClass}">
            <div class="event-meta">
              <span class="event-author ${authorClass}">${escapeHtml(ev.author)}</span>
              <span class="event-time">${ev.date} às ${ev.time}</span>
              ${tagsHtml}
            </div>
            ${ev.content ? `<div class="event-content">${escapeHtml(ev.content)}</div>` : ''}
            ${attHtml}
            ${noteHtml}
          </div>
        `;
      });

      blockEl.innerHTML = `
        <div class="block-header">
          <div>
            <div class="block-title">${escapeHtml(block.title)}</div>
            <div style="font-size:12.5px;color:var(--text-dim);margin-top:2px;">Período: ${block.dates}</div>
          </div>
          <span class="badge ${block.badgeClass}">${block.badge}</span>
        </div>
        <div class="block-summary">
          <strong>Síntese dos Fatos Relevantes:</strong> ${escapeHtml(block.summary)}
        </div>
        <div class="timeline-events">
          ${eventsHtml || '<p style="color:var(--text-dim);font-size:13px;">Nenhum evento correspondente ao filtro selecionado neste bloco.</p>'}
        </div>
      `;

      timelineContainer.appendChild(blockEl);
    });

    const counterEl = document.getElementById('rendered-events-counter');
    if (counterEl) {
      counterEl.innerText = `${totalRenderedEvents} eventos filtrados`;
    }
  }

  // --- 2. SEARCH & FILTER CONTROLS ---
  const searchInput = document.getElementById('timeline-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      renderTimeline();
    });
  }

  const filterButtons = document.querySelectorAll('.filter-btn[data-tag]');
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-tag');
      renderTimeline();
    });
  });

  // --- 3. MULTI-AGENT TABS ---
  const tabButtons = document.querySelectorAll('.tab-btn[data-agent]');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const agentKey = btn.getAttribute('data-agent');
      renderAgentTab(agentKey);
    });
  });

  function renderAgentTab(agentKey) {
    const container = document.getElementById('agent-content-display');
    const agent = data.multiAgentData[agentKey];
    if (!agent || !container) return;

    const articlesBadges = agent.articles.map(a => `<span class="badge blue" style="margin-right:6px;">${a}</span>`).join('');

    container.innerHTML = `
      <div class="card" style="animation: fadeIn 0.25s ease;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
          <h3 style="color:#fff;font-size:18px;font-family:var(--font-heading);">${escapeHtml(agent.title)}</h3>
          <div>${articlesBadges}</div>
        </div>
        <div style="font-size:14px;color:var(--primary-light);font-weight:600;margin-bottom:16px;">
          ${escapeHtml(agent.lead)}
        </div>
        <div style="font-size:14px;color:#cbd5e1;white-space:pre-wrap;line-height:1.7;">${escapeHtml(agent.content.trim())}</div>
      </div>
    `;
  }

  // Initial render of agent tab
  renderAgentTab('agent_penal');

  // --- 4. RENDER EVIDENCE GALLERY ---
  const evidenceContainer = document.getElementById('evidence-gallery-container');
  if (evidenceContainer) {
    data.evidenceGallery.forEach(ev => {
      const isImg = ev.filename.toLowerCase().match(/\.(jpg|jpeg|png|webp)$/);
      const thumbHtml = isImg ? 
        `<img src="${ev.filename}" alt="${escapeHtml(ev.title)}" loading="lazy">` :
        `<div class="evidence-doc-placeholder"><span class="evidence-doc-icon">📄</span><span style="font-size:11px;">Documento Oficial</span></div>`;

      const card = document.createElement('div');
      card.className = 'evidence-card';
      card.onclick = () => openEvidenceModal(ev);

      card.innerHTML = `
        <div class="evidence-thumb">${thumbHtml}</div>
        <div class="evidence-body">
          <div style="margin-bottom:6px;"><span class="badge blue">${ev.category}</span></div>
          <div class="evidence-title">${escapeHtml(ev.title)}</div>
          <div class="evidence-desc">${escapeHtml(ev.description)}</div>
          <div class="evidence-footer">
            <span>📅 ${ev.date}</span>
            <span style="color:var(--primary-light);font-weight:600;">Ver Prova →</span>
          </div>
        </div>
      `;
      evidenceContainer.appendChild(card);
    });
  }

  // --- 5. RENDER AUDIO VAULT ---
  const audioVaultContainer = document.getElementById('audio-vault-container');
  const audioSearchInput = document.getElementById('audio-search');

  function renderAudioVault(query = '') {
    if (!audioVaultContainer) return;
    audioVaultContainer.innerHTML = '';

    const filtered = data.audioVault.filter(a => {
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return a.transcription.toLowerCase().includes(q) || a.author.toLowerCase().includes(q) || a.filename.toLowerCase().includes(q);
    });

    filtered.forEach(a => {
      const isGustavo = a.author.toLowerCase().includes('gustavo');
      const authorClass = isGustavo ? 'gustavo' : 'camila';

      const card = document.createElement('div');
      card.className = 'audio-card';
      card.innerHTML = `
        <div class="audio-card-header">
          <span class="event-author ${authorClass}">${escapeHtml(a.author)}</span>
          <span style="color:var(--text-dim);">${a.date} ${a.time} (${a.duration}s)</span>
        </div>
        <audio controls preload="none" src="${a.filename}"></audio>
        <div class="audio-text">
          "${escapeHtml(a.transcription)}"
        </div>
      `;
      audioVaultContainer.appendChild(card);
    });

    const audioCountEl = document.getElementById('audio-count-display');
    if (audioCountEl) {
      audioCountEl.innerText = `${filtered.length} áudios encontrados`;
    }
  }

  if (audioSearchInput) {
    audioSearchInput.addEventListener('input', (e) => {
      renderAudioVault(e.target.value);
    });
  }

  renderAudioVault();

  // --- 6. RENDER LEGAL DRAFTS ---
  const draftSelect = document.getElementById('draft-selector');
  const draftTextarea = document.getElementById('draft-content');
  if (draftSelect && draftTextarea) {
    draftTextarea.value = data.legalDrafts[draftSelect.value];
    draftSelect.addEventListener('change', () => {
      draftTextarea.value = data.legalDrafts[draftSelect.value];
    });
  }

  // Initial timeline render
  renderTimeline();
});

// Helper: Escape HTML
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}

// Copy draft to clipboard
function copyLegalDraft() {
  const textarea = document.getElementById('draft-content');
  if (textarea) {
    navigator.clipboard.writeText(textarea.value).then(() => {
      alert('Minuta jurídica copiada para a área de transferência com sucesso!');
    });
  }
}

// Lightbox Modal Functions
function toggleModalZoom() {
  const preview = document.getElementById('modal-preview');
  const btn = document.getElementById('modal-zoom-btn');
  if (preview) {
    const isZoomed = preview.classList.toggle('zoomed');
    if (btn) {
      btn.innerText = isZoomed ? '🔍 Reduzir (-)' : '🔍 Zoom / Expandir';
    }
  }
}

// Master Document & Lightbox Modal Engine
function openDocumentModal({ title, filename, date, origin, destiny, authId, description, ocrText }) {
  const modal = document.getElementById('lightbox-modal');
  const titleEl = document.getElementById('modal-title');
  const preview = document.getElementById('modal-preview');
  const ocrEl = document.getElementById('modal-ocr');
  const authDetails = document.getElementById('modal-auth-details');
  const openTab = document.getElementById('modal-open-tab');
  const zoomBtn = document.getElementById('modal-zoom-btn');

  if (!modal || !preview) return;

  const fname = filename || '';
  const cleanTitle = title || `Evidência Documental: ${fname}`;
  titleEl.innerText = cleanTitle;
  preview.classList.remove('zoomed');
  preview.classList.remove('document-mode');

  const lower = fname.toLowerCase();
  const isImg = lower.match(/\.(jpg|jpeg|png|webp)$/);
  const isPdf = lower.endsWith('.pdf');
  const isDocx = lower.endsWith('.docx');
  const isMedia = lower.match(/\.(opus|mp3|ogg|wav|mp4|mov)$/);

  if (openTab) {
    openTab.href = encodeURI(fname);
    openTab.style.display = 'inline-flex';
  }

  if (isImg) {
    preview.innerHTML = `<img src="${encodeURI(fname)}" alt="${escapeHtml(cleanTitle)}" onclick="toggleModalZoom()" title="Clique para ampliar/reduzir">`;
    if (zoomBtn) {
      zoomBtn.innerText = '🔍 Zoom / Expandir';
      zoomBtn.style.display = 'inline-block';
    }
    if (openTab) {
      openTab.innerText = '↗ Abrir Imagem';
      openTab.removeAttribute('download');
    }
  } else if (isPdf) {
    preview.classList.add('document-mode');
    preview.innerHTML = `
      <iframe src="${encodeURI(fname)}#toolbar=1&navpanes=1" 
              style="width:100%;height:100%;min-height:550px;border:none;border-radius:6px;background:#ffffff;" 
              title="${escapeHtml(cleanTitle)}">
      </iframe>
    `;
    if (zoomBtn) zoomBtn.style.display = 'none';
    if (openTab) {
      openTab.innerText = '📄 Abrir PDF em Nova Aba';
      openTab.removeAttribute('download');
    }
  } else if (isDocx) {
    preview.classList.add('document-mode');
    if (zoomBtn) zoomBtn.style.display = 'none';
    if (openTab) {
      openTab.innerText = '📥 Baixar / Abrir DOCX';
      openTab.setAttribute('download', fname);
    }

    const preRendered = (window.DOCX_PREVIEWS && window.DOCX_PREVIEWS[fname]) ? window.DOCX_PREVIEWS[fname] : null;
    if (preRendered) {
      preview.innerHTML = `
        <div class="docx-render-container">
          <div class="docx-doc-badge">📄 Visualização Direta no Navegador • Documento Word Oficial</div>
          ${preRendered}
        </div>
      `;
    } else {
      preview.innerHTML = `
        <div class="docx-render-container" id="docx-dynamic-view">
          <div style="text-align:center;padding:40px;color:#64748b;">
            <span style="font-size:32px;">⏳</span>
            <p style="margin-top:10px;font-weight:600;">Carregando documento Word no navegador...</p>
          </div>
        </div>
      `;
      if (window.mammoth) {
        fetch(encodeURI(fname))
          .then(res => {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.arrayBuffer();
          })
          .then(ab => window.mammoth.convertToHtml({ arrayBuffer: ab }))
          .then(result => {
            const dyn = document.getElementById('docx-dynamic-view');
            if (dyn) {
              dyn.innerHTML = `
                <div class="docx-doc-badge">📄 Visualização Direta no Navegador • Documento Word Oficial</div>
                ${result.value}
              `;
            }
          })
          .catch(err => {
            const dyn = document.getElementById('docx-dynamic-view');
            if (dyn) {
              dyn.innerHTML = `
                <div style="text-align:center;padding:40px;">
                  <span style="font-size:48px;">📄</span>
                  <p style="margin-top:12px;font-weight:700;color:#0f172a;font-size:16px;">${escapeHtml(fname)}</p>
                  <p style="color:#64748b;font-size:13px;margin:8px 0 16px;">Documento técnico anexado aos autos judiciais.</p>
                  <a href="${encodeURI(fname)}" download class="filter-btn" style="display:inline-block;padding:8px 16px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;">📥 Baixar Arquivo DOCX</a>
                </div>
              `;
            }
          });
      }
    }
  } else if (isMedia) {
    if (zoomBtn) zoomBtn.style.display = 'none';
    if (openTab) {
      openTab.innerText = '↗ Abrir Mídia';
      openTab.removeAttribute('download');
    }
    if (lower.match(/\.(mp4|mov)$/)) {
      preview.innerHTML = `<video controls autoplay src="${encodeURI(fname)}" style="max-width:100%;max-height:80vh;border-radius:6px;"></video>`;
    } else {
      preview.innerHTML = `
        <div style="padding:40px;text-align:center;width:100%;">
          <span style="font-size:48px;">🎙️</span>
          <p style="margin-top:12px;font-weight:700;color:#fff;">${escapeHtml(fname)}</p>
          <audio controls autoplay src="${encodeURI(fname)}" style="margin-top:20px;width:100%;max-width:500px;"></audio>
        </div>
      `;
    }
  } else {
    if (zoomBtn) zoomBtn.style.display = 'none';
    if (openTab) {
      openTab.innerText = '📥 Baixar Arquivo';
      openTab.setAttribute('download', fname);
    }
    preview.innerHTML = `
      <div style="padding:40px;color:var(--text-muted);text-align:center;">
        <span style="font-size:48px;">📎</span>
        <p style="margin-top:10px;font-weight:600;color:#fff;">${escapeHtml(fname)}</p>
        <p style="font-size:12px;margin-top:6px;">Arquivo anexado aos autos</p>
        <a href="${encodeURI(fname)}" download class="filter-btn" style="display:inline-block;margin-top:14px;">📥 Baixar Arquivo</a>
      </div>
    `;
  }

  // Set Auth Details
  if (authDetails) {
    authDetails.innerHTML = `
      <div style="font-size:13px;color:var(--text-muted);line-height:1.6;">
        <div><strong>Data/Hora:</strong> ${date || 'Registrado nos autos'}</div>
        <div><strong>Origem:</strong> ${escapeHtml(origin || 'WhatsApp / Prova Documental')}</div>
        <div><strong>Destino:</strong> ${escapeHtml(destiny || 'Instrução Processual')}</div>
        <div><strong>Identificação do Documento:</strong> <code class="bank-card-code">${escapeHtml(authId || fname)}</code></div>
        <div style="margin-top:8px;color:#e2e8f0;">${escapeHtml(description || 'Documento probatório juntado aos autos.')}</div>
      </div>
    `;
  }

  if (ocrEl) {
    ocrEl.innerText = ocrText || (isDocx ? 'Texto estruturado e formatado renderizado diretamente no visualizador.' : 'Arquivo documental anexado ao acervo probatório.');
  }

  modal.classList.add('active');
}

function openEvidenceModal(ev) {
  openDocumentModal({
    title: ev.title,
    filename: ev.filename,
    date: ev.date,
    origin: ev.origin,
    destiny: ev.destiny,
    authId: ev.authId,
    description: ev.description,
    ocrText: ev.ocrText
  });
}

function openLightboxImage(filename) {
  openDocumentModal({
    title: `Evidência Documental: ${filename}`,
    filename: filename,
    date: 'Anexo Oficial',
    origin: 'WhatsApp / Contratos e Bancos',
    destiny: 'Processo Judicial',
    authId: filename,
    description: 'Documento / Comprovante anexado aos autos.',
    ocrText: ''
  });
}

function closeLightbox() {
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.remove('active');
    const preview = document.getElementById('modal-preview');
    if (preview) preview.classList.remove('zoomed');
  }
}
