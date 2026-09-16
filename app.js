// DOSSIÊ JURÍDICO & PERICIAL — INTERACTIVE ENGINE & ZERO-KNOWLEDGE DECRYPTION
// Protected under STJ REsp 1.903.273/PR & Art. 188, I, do Código Civil

// --- 1. ZERO-KNOWLEDGE WEBCRYPTO DECRYPTION ---
function base64ToArrayBuffer(base64) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

async function decryptDossier(passwordStr) {
  if (!window.ENCRYPTED_DOSSIER) {
    throw new Error('Payload criptografado não encontrado em data.js.');
  }

  const enc = new TextEncoder();
  const dec = new TextDecoder();
  const encData = window.ENCRYPTED_DOSSIER;

  const salt = base64ToArrayBuffer(encData.salt);
  const iv = base64ToArrayBuffer(encData.iv);
  const ciphertext = base64ToArrayBuffer(encData.data);

  const pwKey = await crypto.subtle.importKey(
    'raw',
    enc.encode(passwordStr),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );

  const aesKey = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    pwKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['decrypt']
  );

  const decryptedBuf = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    aesKey,
    ciphertext
  );

  const jsonString = dec.decode(decryptedBuf);
  return JSON.parse(jsonString);
}

// --- 2. AUTHENTICATION CONTROLLER ---
window.handleAuthSubmit = async function(e) {
  if (e) e.preventDefault();
  const pwdInput = document.getElementById('auth-password');
  const submitBtn = document.getElementById('auth-submit-btn');
  const errorEl = document.getElementById('auth-error');
  if (!pwdInput) return;

  const password = pwdInput.value;
  if (!password) return;

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = '⏳ Descriptografando...';
  }
  if (errorEl) errorEl.textContent = '';

  try {
    const data = await decryptDossier(password);
    window.DOSSIER_DATA = data;
    if (data.docxPreviews) {
      window.DOCX_PREVIEWS = data.docxPreviews;
    }

    // Save session unlock flag
    sessionStorage.setItem('dossier_unlocked', 'true');
    sessionStorage.setItem('dossier_session_key', password);

    // Fade out gate & render UI
    const gate = document.getElementById('auth-gate');
    if (gate) {
      gate.style.opacity = '0';
      gate.style.transition = 'opacity 0.3s ease';
      setTimeout(() => gate.classList.add('hidden'), 300);
    }

    renderFullDossier(data);

  } catch (err) {
    console.error('Decryption failed:', err);
    if (errorEl) {
      errorEl.textContent = '❌ Senha incorreta ou erro na chave de descriptografia. Acesso negado.';
      pwdInput.classList.add('shake');
      setTimeout(() => pwdInput.classList.remove('shake'), 400);
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerText = 'Descriptografar ➔';
    }
  }
};

window.lockDossier = function() {
  sessionStorage.removeItem('dossier_unlocked');
  sessionStorage.removeItem('dossier_session_key');
  window.DOSSIER_DATA = null;
  window.DOCX_PREVIEWS = {};

  const appEl = document.getElementById('dossier-app');
  if (appEl) {
    appEl.innerHTML = '';
    appEl.style.display = 'none';
  }

  const gate = document.getElementById('auth-gate');
  if (gate) {
    gate.style.opacity = '1';
    gate.classList.remove('hidden');
  }

  const pwdInput = document.getElementById('auth-password');
  if (pwdInput) {
    pwdInput.value = '';
    setTimeout(() => pwdInput.focus(), 150);
  }
};

// Auto-unlock if session key exists
document.addEventListener('DOMContentLoaded', async () => {
  const savedKey = sessionStorage.getItem('dossier_session_key');
  if (savedKey) {
    try {
      const data = await decryptDossier(savedKey);
      window.DOSSIER_DATA = data;
      if (data.docxPreviews) {
        window.DOCX_PREVIEWS = data.docxPreviews;
      }
      const gate = document.getElementById('auth-gate');
      if (gate) gate.classList.add('hidden');
      renderFullDossier(data);
      return;
    } catch (e) {
      sessionStorage.removeItem('dossier_session_key');
    }
  }

  const pwdInput = document.getElementById('auth-password');
  if (pwdInput) setTimeout(() => pwdInput.focus(), 150);
});

// --- 3. DYNAMIC DOSSIER RENDERER ---
function renderFullDossier(data) {
  const app = document.getElementById('dossier-app');
  if (!app) return;

  const m = data.metadata;

  app.innerHTML = `
    <!-- Top Sticky Navigation -->
    <nav class="top-nav">
      <div class="container nav-wrapper">
        <div class="brand">
          <span class="brand-badge">PROCESSO JUDICIAL</span>
          <span>Castellano x Caruso</span>
        </div>
        <ul class="nav-links">
          <li><a href="#sumario" class="nav-btn">Sumário</a></li>
          <li><a href="#aportes" class="nav-btn">Aportes Pix</a></li>
          <li><a href="#veiculo" class="nav-btn">Dívida Carro (VW)</a></li>
          <li><a href="#ameacas" class="nav-btn">Auditoria Ameaças</a></li>
          <li><a href="#multiagentes" class="nav-btn">Multiagentes (5 Visões)</a></li>
          <li><a href="#timeline" class="nav-btn">Linha do Tempo</a></li>
          <li><a href="#evidencias" class="nav-btn">Provas</a></li>
          <li><a href="#audios" class="nav-btn">Áudios (${m.totalAudiosPericiados})</a></li>
          <li><a href="#pecas" class="nav-btn">Minutas Jurídicas</a></li>
        </ul>
        <div class="nav-actions">
          <button class="btn-print" onclick="window.print()" title="Imprimir ou Salvar em PDF">
            <span>🖨️</span> PDF
          </button>
          <button class="btn-print btn-lock" onclick="lockDossier()" title="Bloquear com senha">
            <span>🔒</span> Bloquear
          </button>
        </div>
      </div>
    </nav>

    <!-- Hero Header -->
    <header class="hero">
      <div class="container">
        <div class="hero-tagline">DOCUMENTO DE INSTRUÇÃO PROBATÓRIA — AUDITORIA COMPLETA DE WHATSAPP</div>
        <h1>DOSSIÊ JURÍDICO E FÁTICO</h1>
        <h2 style="font-size: 20px; font-weight: 600; color: #cbd5e1; margin-bottom: 12px; border:none; padding:0;">
          Caso Gustavo Henrique Castellano x Camila Caruso da Costa Neves (C. Caruso Arquitetura e Interiores Ltda)
        </h2>
        <p class="hero-lead">
          Reconstituição cronológica exaustiva e integral das comunicações mantidas entre <strong>29 de julho de 2026</strong> e <strong>15 de setembro de 2026</strong>. Contém a comprovação documental dos repasses Pix diretos à Ré de <strong>R$ 112.000,00</strong> (R$ 40k em 04/08 e R$ 72k em 19/08), o abatimento formal e expressa exclusão dos <strong>R$ 29.730,00</strong> de gastos próprios de mobilização do Autor (retificando a cláusula inserida por engano no primeiro contrato, demonstrando boa-fé e lealdade processual), a sugestão técnica de indenização por <strong>Danos Morais de R$ 30.000,00</strong> (para instrução do advogado do Autor diante da chantagem com falsa medida protetiva da Lei Maria da Penha e abalo de crédito), a transcrição verbatim de todos os <strong>180 áudios periciados (de 186 do acervo original)</strong> via Whisper, a demonstração da correlação com a dívida de veículo do Banco Volkswagen e a subsunção a <strong>Estelionato (Art. 171 CP)</strong> e <strong>Apropriação Indébita (Art. 168 CP)</strong>.
        </p>

        <!-- Meta Chips -->
        <div class="meta-chips">
          <div class="chip chip-highlight">
            <span class="chip-label">Total Repassado à Ré (Pix Direto):</span>
            <span class="chip-val">R$ 112.000,00</span>
          </div>
          <div class="chip">
            <span class="chip-label">Gastos Próprios de Mobilização:</span>
            <span class="chip-val">R$ 29.730,00 (Abatidos / Não Cobrados)</span>
          </div>
          <div class="chip">
            <span class="chip-label">Sugestão Danos Morais (Advogado):</span>
            <span class="chip-val">R$ 30.000,00 (Abalo & Falsa Protetiva)</span>
          </div>
          <div class="chip chip-highlight" style="border-color: rgba(99, 102, 241, 0.6);">
            <span class="chip-label">Pretensão Inicial da Causa:</span>
            <span class="chip-val">R$ 142.000,00 (Principal + Moral)</span>
          </div>
          <div class="chip">
            <span class="chip-label">1º Pix Emergencial:</span>
            <span class="chip-val">R$ 40.000,00 (04/08 Nubank)</span>
          </div>
          <div class="chip">
            <span class="chip-label">2º Pix Parceria:</span>
            <span class="chip-val">R$ 72.000,00 (19/08 Itaú)</span>
          </div>
          <div class="chip">
            <span class="chip-label">Origem dos Recursos:</span>
            <span class="chip-val">Giro Pronampe Itaú + Capital de Giro Nu</span>
          </div>
          <div class="chip">
            <span class="chip-label">Áudios Periciados:</span>
            <span class="chip-val">${m.totalAudiosPericiados} periciados (${m.totalAudiosAcervo} no acervo)</span>
          </div>
          <div class="chip">
            <span class="chip-label">Mensagens Auditadas:</span>
            <span class="chip-val">${m.totalMessages} mensagens no chat</span>
          </div>
          <div class="chip">
            <span class="chip-label">Dívida do Veículo:</span>
            <span class="chip-val">Linha Investigativa (Ação Banco VW Mogi)</span>
          </div>
          <div class="chip">
            <span class="chip-label">Tipificação Penal:</span>
            <span class="chip-val">Estelionato (Art. 171) & Apropriação (Art. 168)</span>
          </div>
          <div class="chip">
            <span class="chip-label">Análise de Ameaças:</span>
            <span class="chip-val">Gustavo: Exercício Regular | Camila: Falsa Protetiva</span>
          </div>
        </div>

        <!-- Metrics Row -->
        <div class="metrics-row">
          <div class="metric-card danger">
            <div class="metric-title">Repasses Pix Diretos à Ré</div>
            <div class="metric-val">R$ 112.000,00</div>
            <div class="metric-sub">R$ 40k (04/08 Nubank) + R$ 72k (19/08 Itaú) retidos sem restituição</div>
          </div>
          <div class="metric-card info">
            <div class="metric-title">Gastos Próprios de Mobilização (Abatidos)</div>
            <div class="metric-val" style="color: #38bdf8;">R$ 29.730,00</div>
            <div class="metric-sub">Itaú SISPAG 18/08; Custos próprios de Gustavo; R$ 0,00 cobrado da Ré</div>
          </div>
          <div class="metric-card purple">
            <div class="metric-title">Sugestão Danos Morais (Advogado)</div>
            <div class="metric-val" style="color: #c084fc;">R$ 30.000,00</div>
            <div class="metric-sub">Áudios 4874/4880: ameaça com Lei Maria da Penha + abalo de crédito</div>
          </div>
          <div class="metric-card warning">
            <div class="metric-title">Valor Inicial Sugerido da Causa</div>
            <div class="metric-val" style="color: #fbbf24;">R$ 142.000,00</div>
            <div class="metric-sub">R$ 112k principal + R$ 30k danos morais (+ encargos bancários a liquidar)</div>
          </div>
          <div class="metric-card warning">
            <div class="metric-title">Saldo Devedor Atual nos Apps</div>
            <div class="metric-val">R$ 168.940,23</div>
            <div class="metric-sub">Restante a pagar oficial: Itaú 1 + Itaú 2 + Nubank restante</div>
          </div>
          <div class="metric-card success">
            <div class="metric-title">Quitação Antecipada Nubank (13x)</div>
            <div class="metric-val">R$ 18.015,62</div>
            <div class="metric-sub">13 parcelas quitadas (desc. R$ 17.521,40) com recurso do 2º Pronampe</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Itaú Pronampe 1 (Contrato 4887183848)</div>
            <div class="metric-val">R$ 119.343,17</div>
            <div class="metric-sub">Restante a pagar no app (60x R$ 2.324,17; financiou os R$ 72k da Ré)</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Itaú Pronampe 2 (Contrato 4886874439)</div>
            <div class="metric-val">R$ 19.527,27</div>
            <div class="metric-sub">Restante a pagar no app (60x R$ 381,45; quitou as 13x do Nubank)</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Saldo Restante Nubank (11 parcelas)</div>
            <div class="metric-val">R$ 30.069,79</div>
            <div class="metric-sub">11x de R$ 2.733,62 agendadas (ou R$ 24.898,68 p/ quitação à vista hoje)</div>
          </div>
        </div>
      </div>
    </header>

    <main>
      <!-- SECTION 1: SUMÁRIO EXECUTIVO -->
      <section id="sumario" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">${data.summarySection.title}</div>
            <div class="section-sub">${data.summarySection.subtitle}</div>
          </div>

          <div class="card">
            <h3 class="card-title">1. A Trama Fática e a Dinâmica do Golpe</h3>
            ${data.summarySection.paragraphs.map(p => `<p style="color: #cbd5e1; line-height: 1.7; margin-bottom: 16px;">${p}</p>`).join('')}
          </div>
        </div>
      </section>

      <!-- SECTION 2: APORTES FINANCEIROS -->
      <section id="aportes" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">💳 Comprovação Documental dos Aportes e das Operações Bancárias</div>
            <div class="section-sub">Demonstrativo exato dos extratos de tela dos bancos (Itaú Empresas e Nubank PJ)</div>
          </div>

          <div class="card" style="margin-bottom: 20px; border-left: 4px solid var(--info); background: rgba(30, 41, 59, 0.7);">
            <div style="font-weight: 700; color: #fff; font-size: 14px; margin-bottom: 6px;">
              📌 Nota Metodológica: Saldo Devedor Atual nos Extratos vs. Soma Nominal de Parcelas Futuras
            </div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
              <p style="margin-bottom: 6px;">
                <strong>1. Saldo Devedor Contábil Atual nos Aplicativos (Restante a Pagar):</strong> Conforme comprovam as telas dos apps do Itaú e Nubank, o saldo devedor principal atual soma exatamente <strong>R$ 168.940,23</strong> (Itaú Contrato 4887183848: R$ 119.343,17 + Itaú Contrato 4886874439: R$ 19.527,27 + Nubank: R$ 30.069,79; ou R$ 163.769,12 para liquidação à vista hoje com desconto).
              </p>
              <p style="margin-bottom: 6px;">
                <strong>2. Quitação Antecipada de 13 Parcelas do Nubank:</strong> Em 24/08/2026, Gustavo pagou <strong>R$ 18.015,62</strong> à vista (comprovante Nu Financeira cód. <code>6a8c7a93</code>), obtendo <strong>R$ 17.521,40 de desconto</strong> sobre o valor original das parcelas (R$ 35.537,03), utilizando recursos do 2º Pronampe Itaú.
              </p>
              <p style="margin-bottom: 6px;">
                <strong>3. Não-Duplicidade e Substituição de Dívida:</strong> Dos R$ 42.050,90 tomados originalmente no Nubank (com juros de 63,14% a.a.), Gustavo contratou o 2º Pronampe no Itaú (R$ 19.527,27) com taxa Selic mais baixa e usou R$ 18.015,62 para antecipar as 13 parcelas do Nubank. Logo, o 2º Pronampe substituiu essa fatia da dívida cara, agindo Gustavo para conter o prejuízo provocado pelo socorro prestado a Camila.
              </p>
              <p style="margin-bottom: 0;">
                <strong>4. Gastos Próprios de Mobilização do Autor (R$ 29.730,00 em 18/08/2026 — Abatidos e NÃO cobrados da Ré):</strong> Conforme comprovante SISPAG e extrato da conta Itaú Empresas de 18/08/2026, Gustavo realizou desembolsos de R$ 29.730,00 para fornecedores, contratações e compra de equipamentos para estruturar a sua própria empresa (Agilidade para Todos), custos que independem de Camila. Embora o primeiro rascunho de minuta contratual contivesse inadvertidamente previsão de rateio/reembolso, Gustavo formal e expressamente retifica a minuta e deduz integralmente tais despesas da pretensão deduzida em face de Camila. Cobram-se unicamente os <strong>R$ 112.000,00</strong> de aportes Pix transferidos diretamente à conta bancária da Ré, em inequívoca demonstração de absoluta boa-fé objetiva (Art. 422 do CC) e probidade processual (Art. 5º do CPC).
              </p>
            </div>
          </div>

          <div class="bank-cards-grid">
            <!-- Card Pix 1 -->
            <div class="bank-card success-border">
              <div>
                <div class="bank-card-header">
                  <div class="bank-card-header-top">
                    <span class="badge green">1º APORTE PIX</span>
                    <span class="bank-card-source">04/08/2026 às 10:28:49</span>
                  </div>
                </div>
                <div class="bank-card-value-wrap">
                  <div class="bank-card-val val-white">R$ 40.000,00</div>
                  <div class="bank-card-val-sub">Empréstimo emergencial para socorro financeiro imediato à Ré</div>
                </div>
                <div class="bank-card-details">
                  <div><strong>Origem:</strong> Nu Pagamentos S.A. (Agilidade para Todos — CNPJ 27.626.226/0001-59)</div>
                  <div><strong>Destino:</strong> C. CARUSO ARQUITETURA E INTERIORES LTDA (CNPJ 46.788.820/0001-90)</div>
                  <div><strong>Banco Destino:</strong> Banco Santander (Brasil) S.A.</div>
                  <div><strong>ID Transação:</strong> <code class="bank-card-code">E18236120202608041328s14787e325d</code></div>
                  <div style="margin-top:6px;color:#cbd5e1;"><em>Viabilizado por empréstimo de Capital de Giro tomado por Gustavo no Nubank com juros de 63,14% a.a. para socorro urgente.</em></div>
                </div>
              </div>
              <div class="bank-card-actions">
                <button class="filter-btn" onclick="openLightboxImage('00001604-PHOTO-2026-08-04-10-29-00.jpg')">
                  🔍 Ver Comprovante e Autenticação
                </button>
              </div>
            </div>

            <!-- Card Pix 2 -->
            <div class="bank-card success-border">
              <div>
                <div class="bank-card-header">
                  <div class="bank-card-header-top">
                    <span class="badge green">2º APORTE PIX</span>
                    <span class="bank-card-source">19/08/2026 às 16:10:39</span>
                  </div>
                </div>
                <div class="bank-card-value-wrap">
                  <div class="bank-card-val val-white">R$ 72.000,00</div>
                  <div class="bank-card-val-sub">Cédula de Crédito Bancário Pronampe contratada no Itaú</div>
                </div>
                <div class="bank-card-details">
                  <div><strong>Origem:</strong> Itaú Unibanco S.A. SISPAG (Gustavo H. Castellano — Ag 0173 CC 99110-0)</div>
                  <div><strong>Destino:</strong> ARQUITETA CAMILA CARUSO (Banco Santander — CNPJ 46.788.820/0001-90)</div>
                  <div><strong>Mensagem ao Recebedor:</strong> <em>"deposito referente a obra que estamos operando em parceria Camila Caruso e Agilidade para Todos"</em></div>
                  <div><strong>ID Transação:</strong> <code class="bank-card-code">E60701190202608191909DYSMAN3D8X4</code></div>
                  <div><strong>Autenticação:</strong> <code class="bank-card-code">A84590460945ACACFBE66745CC6299E86E69A7A3</code></div>
                  <div style="margin-top:6px;color:#cbd5e1;"><em>Viabilizado por Cédula de Crédito Bancário Giro Pronampe Contrato 4887183848 no Itaú.</em></div>
                </div>
              </div>
              <div class="bank-card-actions">
                <button class="filter-btn" onclick="openLightboxImage('00003448-PHOTO-2026-08-19-16-10-56.jpg')">
                  🔍 Ver Comprovante e Autenticação
                </button>
              </div>
            </div>

            <!-- Card 3: Gastos Próprios de Mobilização (Abatidos) -->
            <div class="bank-card info-border">
              <div>
                <div class="bank-card-header">
                  <div class="bank-card-header-top">
                    <span class="badge blue">EXCLUSIVO DO AUTOR • NÃO COBRADO DA RÉ (ABATIDO)</span>
                    <span class="bank-card-source">18/08/2026 (Itaú SISPAG)</span>
                  </div>
                </div>
                <div class="bank-card-value-wrap">
                  <div class="bank-card-val val-white">R$ 29.730,00</div>
                  <div class="bank-card-val-sub">Mobilização de fornecedores e equipamentos de tecnologia da empresa de Gustavo</div>
                </div>
                <div class="bank-card-details">
                  <div><strong>Origem do Débito:</strong> Itaú Unibanco S.A. SISPAG Fornecedores (Ag 0173 CC 99110-0)</div>
                  <div><strong>Destino:</strong> Contratações, terceiros e equipamentos próprios da Agilidade para Todos</div>
                  <div><strong>Status de Cobrança:</strong> <strong style="color: #38bdf8;">100% ABATIDO • R$ 0,00 COBRADO DE CAMILA</strong></div>
                  <div><strong>Extrato Bancário do Dia:</strong> Saldo de R$ 84.423,00 (após débito SISPAG de R$ 29,7k e crédito de R$ 113,6k de Giro)</div>
                  <div style="margin-top:6px;color:#cbd5e1;"><em>Cláusula de reembolso constante do 1º esboço preliminar expressamente retificada pelo Autor. Despesa absorvida pelo credor em demonstração cabal de lealdade e boa-fé objetiva (Art. 5º CPC e Art. 422 CC).</em></div>
                </div>
              </div>
              <div class="bank-card-actions" style="display:flex;flex-direction:column;gap:8px;">
                <button class="filter-btn" onclick="openLightbox('ev-sispag-29k-detalhes')">
                  🔍 Ver Comprovante SISPAG (R$ 29.730,00)
                </button>
                <button class="filter-btn" onclick="openLightbox('ev-sispag-29k-extrato')">
                  🔍 Ver Extrato Itaú de 18/08/2026
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION 3: PASSIVO AUTOMOTIVO E BANCO VOLKSWAGEN -->
      <section id="veiculo" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">${data.veiculoSection.title}</div>
            <div class="section-sub">${data.veiculoSection.subtitle}</div>
          </div>

          <div class="card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
              <h3 style="font-size:17px;color:#fff;font-family:var(--font-heading);">
                ${data.veiculoSection.processo}
              </h3>
              <span class="badge amber">${data.veiculoSection.natureza}</span>
            </div>
            <p style="font-size:14px;color:#cbd5e1;line-height:1.7;margin-bottom:14px;">
              ${data.veiculoSection.description}
            </p>
            <div style="background:rgba(2, 6, 23, 0.6);border:1px solid var(--border-subtle);border-radius:var(--radius-sm);padding:16px;margin-bottom:16px;">
              <div style="font-weight:700;color:#fca5a5;font-size:13px;margin-bottom:8px;">
                CORRELAÇÃO TEMPORAL NO CHAT (PROVAS DA DESTINAÇÃO AO CARRO):
              </div>
              <ul style="list-style:none;display:flex;flex-direction:column;gap:8px;font-size:13px;color:#cbd5e1;">
                ${data.veiculoSection.quotes.map(q => `<li>• <strong>${q.date}:</strong> ${q.author}: <em>"${q.text}"</em></li>`).join('')}
              </ul>
            </div>
            <p style="font-size:13.5px;color:var(--text-muted);line-height:1.6;">
              <strong>${data.veiculoSection.conclusion}</strong>
            </p>
          </div>
        </div>
      </section>

      <!-- SECTION 4: AUDITORIA DE AMEAÇAS -->
      <section id="ameacas" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">${data.ameacasSection.title}</div>
            <div class="section-sub">${data.ameacasSection.subtitle}</div>
          </div>

          <div class="versus-grid">
            <!-- Gustavo Box -->
            <div class="versus-box author-gustavo">
              <div class="versus-header">
                <span style="color:#60a5fa;">${data.ameacasSection.gustavo.author}</span>
                <span class="badge ${data.ameacasSection.gustavo.statusClass}">${data.ameacasSection.gustavo.status}</span>
              </div>
              <div style="font-size:13px;color:#cbd5e1;line-height:1.6;display:flex;flex-direction:column;gap:10px;">
                <div><strong>Trechos alegados por Camila:</strong>
                  <blockquote style="margin:6px 0;font-size:12.5px;color:var(--text-muted);border-left:3px solid #3b82f6;padding-left:8px;">
                    ${data.ameacasSection.gustavo.allegations.map(a => `"${a}"<br>`).join('')}
                  </blockquote>
                </div>
                <div><strong>Enquadramento Técnico (Art. 147 CP):</strong>
                  ${data.ameacasSection.gustavo.enquadramento}
                </div>
                <div><strong>Postura Reiterada de Pacificação:</strong>
                  ${data.ameacasSection.gustavo.postura}
                </div>
                <div style="color:#86efac;font-weight:600;font-size:12px;border-top:1px solid var(--border-subtle);padding-top:8px;">
                  ${data.ameacasSection.gustavo.conclusao}
                </div>
              </div>
            </div>

            <!-- Camila Box -->
            <div class="versus-box author-camila">
              <div class="versus-header">
                <span style="color:#f87171;">${data.ameacasSection.camila.author}</span>
                <span class="badge ${data.ameacasSection.camila.statusClass}">${data.ameacasSection.camila.status}</span>
              </div>
              <div style="font-size:13px;color:#cbd5e1;line-height:1.6;display:flex;flex-direction:column;gap:10px;">
                <div><strong>Áudios Incontroversos (00004874 e 00004880):</strong>
                  <blockquote style="margin:6px 0;font-size:12.5px;color:#fca5a5;border-left:3px solid #ef4444;padding-left:8px;">
                    ${data.ameacasSection.camila.allegations.map(a => `"${a}"<br>`).join('')}
                  </blockquote>
                </div>
                <div><strong>Enquadramento Técnico:</strong>
                  ${data.ameacasSection.camila.enquadramento}
                </div>
                <div><strong>Intimidação Comercial:</strong>
                  ${data.ameacasSection.camila.postura}
                </div>
                <div style="color:#fca5a5;font-weight:600;font-size:12px;border-top:1px solid var(--border-subtle);padding-top:8px;">
                  ${data.ameacasSection.camila.conclusao}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION 5: ANÁLISE MULTIAGENTE -->
      <section id="multiagentes" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">🤖 Auditoria Especializada Multiagente (5 Perspectivas Jurídicas)</div>
            <div class="section-sub">Pareceres aprofundados emitidos por agentes autônomos com fundamentação de lei e jurisprudência</div>
          </div>

          <div class="card" style="padding: 24px;">
            <div class="tabs-header" id="agent-tabs-header">
              <!-- Injected dynamically -->
            </div>
            <div id="agent-tab-content">
              <!-- Injected dynamically -->
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION 6: TIMELINE PERICIADA -->
      <section id="timeline" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">⏱️ Linha do Tempo Periciada (10 Blocos Cronológicos)</div>
            <div class="section-sub">Reconstituição factual estrita com 93 marcos probatórios filtrados e transcritos</div>
          </div>

          <!-- Filter & Search Toolbar -->
          <div class="card" style="margin-bottom:24px;">
            <div class="filter-toolbar">
              <div class="filter-chips">
                <button class="filter-btn active" data-filter="TODOS">Todos os Fatos</button>
                <button class="filter-btn" data-filter="FINANCEIRO">💳 Aportes & Bancos</button>
                <button class="filter-btn" data-filter="CONTRATO">📝 Contratos & Minutas</button>
                <button class="filter-btn" data-filter="AMEACA_DISPUTA">⚠️ Disputa & Ameaças</button>
                <button class="filter-btn" data-filter="CARRO_DIVIDA">🚗 Carro & VW</button>
              </div>
              <div style="flex:1;min-width:260px;">
                <input type="text" id="timeline-search" class="search-input" placeholder="🔍 Buscar no texto das mensagens, notas ou transcrições...">
              </div>
            </div>
          </div>

          <div id="timeline-blocks-container">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </section>

      <!-- SECTION 7: GALERIA DE EVIDÊNCIAS -->
      <section id="evidencias" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">📑 Galeria de Evidências Documentais Oficiais</div>
            <div class="section-sub">Extratos de tela, autenticações de Pix, recibos de quitação e instrumentos contratuais</div>
          </div>

          <div class="evidence-grid" id="evidence-gallery-container">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </section>

      <!-- SECTION 8: AUDIO VAULT -->
      <section id="audios" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">🎙️ Audio Vault — Repositório com ${m.totalAudiosPericiados} Áudios e Transcrições Whisper</div>
            <div class="section-sub">Acesso direto a todos os arquivos fonográficos originais e texto transcrito na íntegra</div>
          </div>

          <div class="card" style="margin-bottom:20px;">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
              <input type="text" id="audio-search" class="search-input" style="max-width:400px;" placeholder="🔍 Buscar no texto transcrito dos áudios...">
              <span id="audio-count-display" style="font-size:13px;color:var(--text-dim);font-weight:600;">${m.totalAudiosPericiados} áudios indexados</span>
            </div>
          </div>

          <div class="audio-grid" id="audio-vault-container">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </section>

      <!-- SECTION 9: PEÇAS JURÍDICAS PRONTAS -->
      <section id="pecas" class="section">
        <div class="container">
          <div class="section-header">
            <div class="section-title">📝 Kit Processual para o Advogado (Minutas para Ajuizamento Imediato)</div>
            <div class="section-sub">Peças completas fundamentadas e prontas para protocolo judicial e policial</div>
          </div>

          <div class="card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:10px;">
              <div style="flex:1;min-width:0;max-width:100%;">
                <label for="draft-selector" style="display:block;font-size:13px;color:var(--text-dim);font-weight:600;margin-bottom:6px;">Selecione a Minuta:</label>
                <select id="draft-selector" class="search-input" style="max-width:100%;width:100%;padding:8px 12px;text-overflow:ellipsis;">
                  <option value="peticao_civel">Petição Inicial Cível: Ação de Cobrança c/c Arresto Sisbajud (R$ 112.000,00)</option>
                  <option value="noticia_crime">Notícia-Crime: Representação Criminal por Estelionato e Apropriação Indébita (Art. 171/168 CP)</option>
                  <option value="notificacao_extrajudicial">Notificação Extrajudicial: Constituição em Mora (Prazo 48h)</option>
                </select>
              </div>
              <button class="copy-btn" onclick="copyLegalDraft()">📋 Copiar Minuta Completa</button>
            </div>
            <div class="legal-box">
              <textarea id="draft-content" class="legal-textarea" readonly></textarea>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer>
      <div class="container">
        <p>Dossiê Jurídico e Fático — Caso Gustavo Henrique Castellano x Camila Caruso da Costa Neves</p>
        <p style="margin-top:6px;font-size:11.5px;">Elaborado para instrução processual cível e criminal com estrita observância à Lei Geral de Proteção de Dados e ao Código de Processo Civil.</p>
      </div>
    </footer>
  `;

  // Display app container
  app.style.display = 'block';

  // Initialize interactive components
  initMultiAgents(data.multiAgentData);
  initTimeline(data.blocks);
  initEvidenceGallery(data.evidenceGallery);
  initAudioVault(data.audioVault);
  initLegalDrafts(data.legalDrafts);
}

// --- 4. MULTI-AGENTS CONTROLLER ---
function initMultiAgents(multiAgentData) {
  const tabsContainer = document.getElementById('agent-tabs-header');
  const contentContainer = document.getElementById('agent-tab-content');
  if (!tabsContainer || !contentContainer || !multiAgentData) return;

  const agentKeys = Object.keys(multiAgentData);
  tabsContainer.innerHTML = '';

  const agentLabels = {
    agent_penal: '⚖️ 1. Penal & Investigação',
    agent_civil: '📜 2. Civil & Contratos',
    agent_banking: '💳 3. Bancário & Pronampe',
    agent_defense: '🛡️ 4. Teses da Defesa',
    agent_strategy: '🎯 5. Estrategista Processual'
  };

  agentKeys.forEach((key, index) => {
    const agent = multiAgentData[key];
    const btn = document.createElement('button');
    btn.className = `tab-btn ${index === 0 ? 'active' : ''}`;
    btn.setAttribute('data-agent', key);
    btn.innerHTML = `<span>${agentLabels[key] || agent.title}</span>`;
    btn.title = agent.title;
    btn.onclick = () => selectAgent(key);
    tabsContainer.appendChild(btn);
  });

  function selectAgent(selectedKey) {
    const btns = tabsContainer.querySelectorAll('.tab-btn');
    agentKeys.forEach((key, index) => {
      if (key === selectedKey) {
        btns[index].classList.add('active');
      } else {
        btns[index].classList.remove('active');
      }
    });

    const agent = multiAgentData[selectedKey];
    
    // Format section headers and text beautifully
    let rawContent = escapeHtml(agent.content || '').trim();
    let formattedBody = rawContent
      .replace(/^([0-9]+\.\s+[^\n]+)/gm, '<span class="agent-section-heading">$1</span>')
      .replace(/^(ROTEIRO PRÁTICO[^\n]+)/gm, '<span class="agent-section-heading">$1</span>');

    contentContainer.innerHTML = `
      <div class="agent-content-card">
        <div class="agent-content-title">${escapeHtml(agent.title)}</div>
        <div class="agent-content-lead">${escapeHtml(agent.lead)}</div>
        <div class="agent-articles-wrap">
          ${(agent.articles || []).map(a => `<span class="agent-article-badge">⚖️ ${escapeHtml(a)}</span>`).join('')}
        </div>
        <div class="agent-body-text">${formattedBody}</div>
      </div>
    `;
  }

  if (agentKeys.length > 0) {
    selectAgent(agentKeys[0]);
  }
}

// --- 5. TIMELINE CONTROLLER ---
function initTimeline(blocks) {
  const container = document.getElementById('timeline-blocks-container');
  const searchInput = document.getElementById('timeline-search');
  const filterBtns = document.querySelectorAll('.filter-btn[data-filter]');
  if (!container || !blocks) return;

  let currentFilter = 'TODOS';
  let searchQuery = '';

  function render() {
    container.innerHTML = '';
    let totalRenderedEvents = 0;

    blocks.forEach(block => {
      const filteredEvents = block.events.filter(ev => {
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
          } else {
            matches = tList.includes(currentFilter);
          }
          if (!matches) return false;
        }

        if (searchQuery.trim() !== '') {
          const q = searchQuery.toLowerCase();
          const matchesContent = (ev.content || '').toLowerCase().includes(q);
          const matchesTranscription = (ev.audio_transcription || '').toLowerCase().includes(q);
          const matchesAuthor = (ev.author || '').toLowerCase().includes(q);
          const matchesAtt = (ev.attachment || '').toLowerCase().includes(q);
          const matchesNote = (ev.customNote || '').toLowerCase().includes(q);
          return matchesContent || matchesTranscription || matchesAuthor || matchesAtt || matchesNote;
        }
        return true;
      });

      if (filteredEvents.length === 0) return;
      totalRenderedEvents += filteredEvents.length;

      const timelineBlock = document.createElement('div');
      timelineBlock.className = 'timeline-block';
      timelineBlock.id = `block-${block.id}`;

      timelineBlock.innerHTML = `
        <div class="block-header">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <h3 class="block-title">${escapeHtml(block.title)}</h3>
            <span class="badge ${block.badgeClass || 'blue'}">${escapeHtml(block.badge)}</span>
          </div>
          <div style="font-size:12px;color:var(--text-dim);font-weight:600;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span>📅 ${escapeHtml(block.dates)}</span>
            <span>•</span>
            <span class="badge" style="background:rgba(255,255,255,0.06);color:#cbd5e1;border:1px solid rgba(255,255,255,0.08);">${filteredEvents.length} eventos periciados</span>
          </div>
        </div>
        <div class="block-summary">${escapeHtml(block.summary)}</div>
        <div class="timeline-events"></div>
      `;

      const eventsContainer = timelineBlock.querySelector('.timeline-events');

      filteredEvents.forEach(ev => {
        const isCamila = ev.author && ev.author.toLowerCase().includes('camila');
        const isCrit = (ev.tags && ev.tags.some(t => t.includes('CRIME') || t.includes('AMEACA') || t.includes('PROTETIVA'))) || (ev.customBadge && ev.customBadge.toLowerCase().includes('chantagem'));
        const isAudio = ev.attachment && (ev.attachment.includes('AUDIO') || ev.attachment.endsWith('.opus') || ev.attachment.endsWith('.mp3'));
        const isDocx = ev.attachment && ev.attachment.endsWith('.docx');
        const isImg = ev.attachment && ev.attachment.match(/\.(jpg|jpeg|png)$/i);

        const eventItem = document.createElement('div');
        eventItem.className = `event-item ${isCrit ? 'crit' : ''}`;

        eventItem.innerHTML = `
          <div class="event-meta">
            <span class="event-author ${isCamila ? 'camila' : 'gustavo'}">
              ${isCamila ? '🔴 CAMILA CARUSO' : '🔵 GUSTAVO CASTELLANO'}
            </span>
            <span class="event-time">📅 ${escapeHtml(ev.date || '')} às ${escapeHtml(ev.time || '')}</span>
            <span class="badge" style="background:rgba(255,255,255,0.05);color:var(--text-dim);border:none;font-size:10.5px;">Msg #${ev.id}</span>
            ${ev.customBadge ? `<span class="badge ${isCamila ? 'red' : 'green'}">${escapeHtml(ev.customBadge)}</span>` : ''}
          </div>

          ${ev.content ? `<div class="event-content">${escapeHtml(ev.content)}</div>` : ''}

          ${ev.customNote ? `
            <div class="custom-forensic-note" style="margin-top:10px;background:rgba(30,41,59,0.75);border-left:3px solid #3b82f6;padding:10px 14px;border-radius:4px;font-size:13px;color:#cbd5e1;line-height:1.5;">
              📌 <strong>Nota Pericial:</strong> ${escapeHtml(ev.customNote)}
            </div>
          ` : ''}

          ${isAudio ? `
            <div class="event-audio-box">
              <audio controls preload="none" src="${encodeURI(ev.attachment)}" style="width:100%;height:36px;margin-bottom:8px;"></audio>
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;font-size:11.5px;color:var(--text-dim);margin-bottom:6px;">
                <span>🎙️ Arquivo: <code>${escapeHtml(ev.attachment)}</code></span>
              </div>
              ${ev.audio_transcription ? `
                <div class="event-transcription">
                  <strong style="color:#93c5fd;font-style:normal;">Transcrição Whisper:</strong> "${escapeHtml(ev.audio_transcription)}"
                </div>
              ` : ''}
            </div>
          ` : ''}

          ${(isDocx || isImg) ? `
            <div style="margin-top:12px;">
              <button class="filter-btn" style="padding:6px 14px;font-size:12px;display:inline-flex;align-items:center;gap:6px;" onclick="openLightboxImage('${ev.attachment}')">
                ${isDocx ? '📄 Ver Minuta de Contrato / DOCX' : '🔍 Ver Documento / Comprovante Oficial'}
              </button>
            </div>
          ` : ''}

          ${(ev.tags && ev.tags.length > 0) ? `
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:10px;">
              ${ev.tags.map(t => `<span class="badge" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);color:var(--text-dim);font-size:10px;">#${escapeHtml(t)}</span>`).join('')}
            </div>
          ` : ''}
        `;

        eventsContainer.appendChild(eventItem);
      });

      container.appendChild(timelineBlock);
    });

    if (totalRenderedEvents === 0) {
      container.innerHTML = `
        <div class="card" style="text-align:center;padding:40px;color:var(--text-muted);">
          <span style="font-size:32px;">🔍</span>
          <p style="margin-top:10px;font-weight:600;">Nenhum evento localizado para os critérios informados.</p>
        </div>
      `;
    }
  }

  filterBtns.forEach(btn => {
    btn.onclick = () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-filter');
      render();
    };
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      render();
    });
  }

  render();
}

// --- 6. EVIDENCE GALLERY CONTROLLER ---
function initEvidenceGallery(evidenceGallery) {
  const container = document.getElementById('evidence-gallery-container');
  if (!container || !evidenceGallery) return;

  container.innerHTML = '';

  evidenceGallery.forEach(ev => {
    const card = document.createElement('div');
    card.className = 'evidence-card';
    card.onclick = () => openEvidenceModal(ev);

    const isDocx = ev.filename.endsWith('.docx');
    const isImg = ev.filename.match(/\.(jpg|jpeg|png)$/i);

    card.innerHTML = `
      <div class="evidence-thumb-wrap">
        ${isImg ? `
          <img src="${encodeURI(ev.filename)}" alt="${escapeHtml(ev.title)}" class="evidence-thumb" loading="lazy">
        ` : isDocx ? `
          <div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg, #1e3a8a, #0f172a);color:#fff;">
            <span style="font-size:36px;">📄</span>
            <span style="font-size:11px;font-weight:700;margin-top:6px;letter-spacing:0.05em;color:#93c5fd;">DOCUMENTO WORD</span>
          </div>
        ` : `
          <div style="height:100%;display:flex;align-items:center;justify-content:center;background:#1e293b;color:var(--text-muted);">
            <span style="font-size:36px;">📎</span>
          </div>
        `}
      </div>
      <div class="evidence-card-body">
        <div class="evidence-category-badge">${escapeHtml(ev.category || 'Prova Oficial')}</div>
        <div class="evidence-card-title">${escapeHtml(ev.title)}</div>
        <div class="evidence-meta-row">
          <span>📅 ${escapeHtml(ev.date || '')}</span>
          <span>🏛️ Prova Oficial</span>
        </div>
        <div class="evidence-desc-snippet">${escapeHtml(ev.description || '')}</div>
      </div>
    `;

    container.appendChild(card);
  });
}

// --- 7. AUDIO VAULT CONTROLLER ---
function initAudioVault(audioVault) {
  const container = document.getElementById('audio-vault-container');
  const searchInput = document.getElementById('audio-search');
  const countEl = document.getElementById('audio-count-display');
  if (!container || !audioVault) return;

  function render(filterQuery = '') {
    container.innerHTML = '';
    const q = filterQuery.toLowerCase().trim();

    const filtered = audioVault.filter(a => {
      if (!q) return true;
      const t = (a.transcription || '').toLowerCase();
      const f = (a.filename || '').toLowerCase();
      const auth = (a.author || '').toLowerCase();
      return t.includes(q) || f.includes(q) || auth.includes(q);
    });

    filtered.forEach(a => {
      const isCamila = a.author && a.author.toLowerCase().includes('camila');
      const card = document.createElement('div');
      card.className = `audio-card ${isCamila ? 'author-camila' : 'author-gustavo'}`;

      card.innerHTML = `
        <div class="audio-card-header">
          <span class="audio-card-author ${isCamila ? 'author-camila' : 'author-gustavo'}">
            ${escapeHtml(a.author || 'Áudio')}
          </span>
          <span class="audio-card-time">📅 ${escapeHtml(a.date || '')} às ${escapeHtml(a.time || '')}</span>
        </div>
        <div class="audio-card-file">
          <span class="badge ${a.category === 'AMEACA_CRIME' ? 'red' : a.category === 'FINANCEIRO' ? 'green' : 'blue'}">
            ${escapeHtml(a.badge || a.category)}
          </span>
          <code>Msg #${a.id}</code>
        </div>
        <audio controls src="${encodeURI(a.filename)}" style="width:100%;height:32px;margin:8px 0;"></audio>
        <div class="audio-card-transcription">
          ${a.transcription ? `"${escapeHtml(a.transcription)}"` : '<em style="color:var(--text-dim);">[Sem transcrição Whisper disponível]</em>'}
        </div>
      `;

      container.appendChild(card);
    });

    if (countEl) {
      countEl.innerText = `${filtered.length} áudios encontrados (de ${audioVault.length})`;
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      render(e.target.value);
    });
  }

  render();
}

// --- 8. LEGAL DRAFTS CONTROLLER ---
function initLegalDrafts(legalDrafts) {
  const select = document.getElementById('draft-selector');
  const textarea = document.getElementById('draft-content');
  if (!select || !textarea || !legalDrafts) return;

  function update() {
    const val = select.value;
    textarea.value = legalDrafts[val] || '';
  }

  select.addEventListener('change', update);
  update();
}

window.copyLegalDraft = function() {
  const textarea = document.getElementById('draft-content');
  if (textarea) {
    navigator.clipboard.writeText(textarea.value).then(() => {
      alert('Minuta jurídica copiada para a área de transferência com sucesso!');
    });
  }
};

// --- 9. LIGHTBOX & DOCUMENT PREVIEW MODAL ---
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
  const isDocx = lower.endsWith('.docx');

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
  } else if (isDocx) {
    preview.classList.add('document-mode');
    if (zoomBtn) zoomBtn.style.display = 'none';
    if (openTab) {
      openTab.innerText = '📥 Baixar DOCX';
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
        <p style="font-size:12px;margin-top:6px;">Arquivo probatório oficial</p>
        <a href="${encodeURI(fname)}" download class="filter-btn" style="display:inline-block;margin-top:14px;">📥 Baixar Arquivo</a>
      </div>
    `;
  }

  if (authDetails) {
    authDetails.innerHTML = `
      <div style="font-size:13px;color:var(--text-muted);line-height:1.6;">
        <div><strong>Data/Hora:</strong> ${date || 'Registrado nos autos'}</div>
        <div><strong>Origem:</strong> ${escapeHtml(origin || 'WhatsApp / Prova Documental')}</div>
        <div><strong>Destino:</strong> ${escapeHtml(destiny || 'Instrução Processual')}</div>
        <div><strong>Identificação:</strong> <code class="bank-card-code">${escapeHtml(authId || fname)}</code></div>
        <div style="margin-top:8px;color:#e2e8f0;">${escapeHtml(description || 'Documento probatório juntado aos autos.')}</div>
      </div>
    `;
  }

  if (ocrEl) {
    ocrEl.innerText = ocrText || (isDocx ? 'Texto estruturado e formatado renderizado diretamente no visualizador.' : 'Arquivo documental anexado ao acervo probatório.');
  }

  modal.classList.add('active');
}

window.openEvidenceModal = function(ev) {
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
};

window.openLightbox = function(idOrFilename) {
  if (window.DOSSIER_DATA && window.DOSSIER_DATA.evidenceGallery) {
    const ev = window.DOSSIER_DATA.evidenceGallery.find(e => e.id === idOrFilename);
    if (ev) {
      window.openEvidenceModal(ev);
      return;
    }
  }
  window.openLightboxImage(idOrFilename);
};

window.openLightboxImage = function(filename) {
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
};

window.closeLightbox = function() {
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.remove('active');
    const preview = document.getElementById('modal-preview');
    if (preview) preview.classList.remove('zoomed');
  }
};

window.toggleModalZoom = function() {
  const preview = document.getElementById('modal-preview');
  const btn = document.getElementById('modal-zoom-btn');
  if (preview) {
    const isZoomed = preview.classList.toggle('zoomed');
    if (btn) {
      btn.innerText = isZoomed ? '🔍 Reduzir (-)' : '🔍 Zoom / Expandir';
    }
  }
};

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
