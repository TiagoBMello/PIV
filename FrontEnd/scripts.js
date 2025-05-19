// scripts.js (etapa final do Planejamento)

console.log("LIA - Planejamento IA finalizado!");

const user_id = "usuario123"; // virá do login futuramente

// 📌 Adiciona nova meta
async function adicionarMeta() {
  const nome = document.getElementById('nome-meta').value;
  const valor = parseFloat(document.getElementById('valor-meta').value);
  const prazo = parseInt(document.getElementById('prazo-meta').value);
  const prioridade = document.getElementById('prioridade-meta').value;

  if (!nome || isNaN(valor) || isNaN(prazo) || !prioridade) {
    alert('⚠️ Preencha todos os campos!');
    return;
  }

  const resposta = await fetch("http://localhost:5000/metas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome, valor, prazo, prioridade })
  });

  if (resposta.ok) {
    alert("✅ Meta cadastrada!");
    listarMetas();
  } else {
    alert("❌ Erro ao cadastrar a meta.");
  }
}

// 📋 Lista metas e exibe progresso, atraso e botões
async function listarMetas() {
  try {
    const resposta = await fetch(`http://localhost:5000/metas/${user_id}`);
    const metas = await resposta.json();
    const lista = document.getElementById('lista-metas');
    lista.innerHTML = '';

    metas.forEach(meta => {
      const acumulado = meta.acumulado || 0;
      const restante = meta.valor - acumulado;
      const progresso = Math.min(100, (acumulado / meta.valor) * 100).toFixed(0);
      const mesesRestantes = meta.prazo;
      const necessarioPorMes = (meta.valor / meta.prazo).toFixed(2);
      const ritmoAtual = (acumulado / meta.prazo).toFixed(2);
      const previsaoConclusao = ritmoAtual > 0 ? Math.ceil((meta.valor - acumulado) / ritmoAtual) : '∞';
      const atrasado = acumulado < (meta.valor / meta.prazo) * (meta.prazo - mesesRestantes + 1);

      const div = document.createElement('div');
      div.className = 'meta-card';
      div.innerHTML = `
        <p><strong>${meta.nome}</strong></p>
        <p>Valor total: R$${meta.valor.toFixed(2)} | Acumulado: R$${acumulado.toFixed(2)}</p>
        <p>Prazo: ${meta.prazo} meses | Prioridade: <span class="prioridade-${meta.prioridade}">${meta.prioridade.toUpperCase()}</span></p>
        <p>🎯 Progresso: ${progresso}%</p>
        ${atrasado ? `<p style="color: red">⚠️ Atrasado - Se continuar nesse ritmo, você atingirá em ${previsaoConclusao} meses.</p>
        <p>💡 Recomendo guardar R$${necessarioPorMes} por mês para alcançar no prazo.</p>` : ''}
        ${progresso >= 100 ? `<button onclick="retirarFundos('${meta.nome}')">💸 Retirar Fundos</button>` : ''}
      `;

      lista.appendChild(div);
    });
  } catch (erro) {
    console.error("Erro ao listar metas:", erro);
  }
}

// 🤖 Distribuição com IA
async function calcularDistribuicao() {
  const valor_mensal = parseFloat(document.getElementById('valor-mensal').value);
  if (isNaN(valor_mensal) || valor_mensal <= 0) {
    alert("⚠️ Informe quanto você pode guardar por mês.");
    return;
  }

  const resposta = await fetch("http://localhost:5000/metas/contribuir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, valor_mensal })
  });

  const dados = await resposta.json();
  if (resposta.ok) {
    alert("💡 Contribuição aplicada com sucesso!");
    listarMetas();
  } else {
    alert(`❌ Erro: ${dados.erro}`);
  }
}

// 🧹 Remove meta quando concluída
async function retirarFundos(nomeMeta) {
  const confirmacao = confirm(`Tem certeza que deseja retirar fundos da meta "${nomeMeta}"? Ela será encerrada.`);
  if (!confirmacao) return;

  try {
    await fetch(`http://localhost:5000/metas/deletar/${user_id}/${encodeURIComponent(nomeMeta)}`, {
      method: "DELETE"
    });
    listarMetas();
  } catch (erro) {
    alert("❌ Erro ao excluir meta concluída.");
  }
}

// Atualiza aporte e analisa previsão para cada meta

async function analisarMeta(nome) {
  const user_id = "usuario123";

  // Registrar um novo aporte (exemplo automático de R$ 100)
  const valor = 100; // Aqui no futuro você pode pedir pro usuário definir
  await fetch("http://localhost:5000/historico", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome, valor })
  });

  // Consultar análise preditiva
  const resposta = await fetch("http://localhost:5000/projecao", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert(`❌ Erro: ${dados.erro}`);
    return;
  }

  let mensagem = `📈 Acumulado: R$ ${dados.acumulado}\n` +
                 `🎯 Valor restante: R$ ${dados.restante}\n` +
                 `📊 Média mensal: R$ ${dados.media_mensal.toFixed(2)}\n` +
                 `⏳ Estimativa de conclusão: ${dados.meses_estimados} meses\n` +
                 `💡 Sugestão de aporte ideal: R$ ${dados.recomendado_mensal.toFixed(2)}`;

  alert(mensagem);
}

async function calcularPerfil() {
  const perguntas = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'];
  let respostas = [];

  for (let i = 0; i < perguntas.length; i++) {
    const val = document.querySelector(`input[name="${perguntas[i]}"]:checked`);
    if (!val) {
      alert("⚠️ Responda todas as perguntas.");
      return;
    }
    respostas.push(parseInt(val.value));
  }

  const user_id = "usuario123"; // ← depois será dinâmico

  try {
    const response = await fetch("http://localhost:5000/perfil", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, respostas })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(`❌ Erro: ${data.erro}`);
      return;
    }

    const dicaSecao = document.getElementById("dicaPersonalizada");
    const dicaResultado = document.getElementById("dicaResultado");
    dicaSecao.style.display = "block";

    let linksHTML = "";
    if (data.links && data.links.length > 0) {
      linksHTML = `
        <h4>📚 Links Recomendados:</h4>
        <ul>
          ${data.links.map(link => `<li><a href="${link.url}" target="_blank">🔗 ${link.titulo}</a></li>`).join("")}
        </ul>
      `;
    }

    dicaResultado.innerHTML = `
      <div class="investment-card">
        <h3>${data.perfil}</h3>
        <div class="investment-details">
          <p>${data.descricao}</p>
          <ul>
            ${data.detalhes.map(item => `<li>📌 ${item}</li>`).join("")}
          </ul>
          ${data.extra ? `<p><strong>💬 Dica Personalizada:</strong> ${data.extra}</p>` : ""}
          ${linksHTML}
        </div>
      </div>
    `;

    dicaSecao.scrollIntoView({ behavior: 'smooth' });

  } catch (erro) {
    console.error("❌ Erro ao consultar perfil:", erro);
    alert("Erro ao calcular seu perfil. Tente novamente.");
  }
}


// Carrega metas ao abrir a página
window.onload = listarMetas;
