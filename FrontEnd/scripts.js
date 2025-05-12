console.log("LIA - Assistente Financeiro inicializado!");

const user_id = "usuario123"; // Substituir pelo ID real futuramente

// 📌 Adiciona nova meta ao backend
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

// 📋 Lista metas e mostra feedback visual
async function listarMetas() {
  try {
    const resposta = await fetch(`http://localhost:5000/metas/${user_id}`);
    const dados = await resposta.json();

    const lista = document.getElementById('lista-metas');
    lista.innerHTML = '';

    dados.forEach(meta => {
      const progresso = (meta.acumulado / meta.valor) * 100;
      const idealPorMes = meta.valor / meta.prazo;

      const mesesDesdeCriacao = Math.max(1, Math.ceil((new Date() - new Date(meta.criada_em)) / (1000 * 60 * 60 * 24 * 30)));
      const esperado = idealPorMes * mesesDesdeCriacao;

      let statusMsg = '';
      if (meta.acumulado >= meta.valor) {
        statusMsg = "🎉 Meta alcançada!";
      } else if (meta.acumulado >= esperado) {
        statusMsg = "✅ No caminho certo!";
      } else {
        const faltando = (esperado - meta.acumulado).toFixed(2);
        statusMsg = `⚠️ Atrasado: precisa de R$${faltando} a mais.`;
      }

      const div = document.createElement('div');
      div.className = 'meta-card';
      div.innerHTML = `
        <p><strong>${meta.nome}</strong></p>
        <p>Valor total: R$${meta.valor.toFixed(2)}</p>
        <p>Acumulado: R$${(meta.acumulado || 0).toFixed(2)}</p>
        <p>Prazo: ${meta.prazo} meses</p>
        <p>Prioridade: <span class="prioridade-${meta.prioridade}">${meta.prioridade.toUpperCase()}</span></p>
        <div class="progress-bar-container">
          <div class="progress-bar" style="width: ${Math.min(100, progresso)}%"></div>
        </div>
        <p class="status-feedback">${statusMsg}</p>
      `;
      lista.appendChild(div);
    });
  } catch (erro) {
    console.error("Erro ao listar metas:", erro);
  }
}

// 🤖 Distribuição automática baseada em IA
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

// Chama a listagem ao carregar a página
window.onload = listarMetas;
