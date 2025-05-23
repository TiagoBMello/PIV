console.log("LIA - Planejamento IA iniciado");

const user_id = "usuario123"; // vindo do login futuramente

// ✅ Adicionar meta
async function adicionarMeta() {
  const nome = document.getElementById('nome-meta').value.trim();
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


// ✅ Listar metas e gerar HTML
async function listarMetas() {
  try {
    const resposta = await fetch(`http://localhost:5000/metas/${user_id}`);
    const metas = await resposta.json();
    const lista = document.getElementById('lista-metas');
    lista.innerHTML = '';

    metas.forEach(meta => {
      const acumulado = meta.acumulado || 0;
      const progresso = Math.min(100, (acumulado / meta.valor) * 100).toFixed(0);

      // Corrigir espaços no nome
      const safeName = meta.nome.replace(/\s+/g, '_');

      const div = document.createElement('div');
      div.className = 'meta-card';

      div.innerHTML = `
        <p><strong>${meta.nome}</strong></p>
        <p>Valor total: R$${meta.valor.toFixed(2)} | Acumulado: R$${acumulado.toFixed(2)}</p>
        <p>Prazo: ${meta.prazo} meses | Prioridade: <span class="prioridade-${meta.prioridade}">${meta.prioridade.toUpperCase()}</span></p>
        <p>🎯 Progresso: ${progresso}%</p>

        ${progresso >= 100
          ? `<button onclick="retirarFundos('${safeName}')">💸 Retirar Fundos</button>`
          : `
            <div style="display: flex; gap: 10px; align-items: center; margin-top: 10px;">
              <input type="number" placeholder="Quanto deseja adicionar?" id="aporte-${safeName}" style="flex:1; padding: 5px;" />
              <button onclick="fazerAporte('${safeName}')">💰 Fazer Aporte</button>
              <button onclick="verGrafico('${safeName}')" style="background-color:#007acc;color:#fff;padding:8px;border:none;border-radius:5px;cursor:pointer;">📈 Ver Gráfico</button>
            </div>
          `}
      `;

      lista.appendChild(div);
    });
  } catch (erro) {
    console.error("❌ Erro ao listar metas:", erro);
  }
}

// ✅ Fazer aporte
async function fazerAporte(nomeSafe) {
  const nomeOriginal = nomeSafe.replace(/_/g, ' ');
  const input = document.getElementById(`aporte-${nomeSafe}`);
  const valor = parseFloat(input.value);

  if (isNaN(valor) || valor <= 0) {
    alert("⚠️ Digite um valor válido para o aporte.");
    return;
  }

  // Registrar no histórico
  await fetch("http://localhost:5000/historico", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome: nomeOriginal, valor })
  });

  // Atualizar o acumulado na meta
  const resposta = await fetch(`http://localhost:5000/metas/${user_id}/atualizar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome: nomeOriginal, valor })
  });

  const dados = await resposta.json();

  if (resposta.ok) {
    alert("✅ Aporte realizado com sucesso!");
    input.value = '';
    listarMetas();
  } else {
    alert(`❌ Erro: ${dados.erro || "Erro ao atualizar meta."}`);
  }
}

// ✅ Remover meta (retirar fundos)
async function retirarFundos(nomeSafe) {
  const nomeOriginal = nomeSafe.replace(/_/g, ' ');

  const confirmacao = confirm(`Deseja retirar fundos da meta "${nomeOriginal}"? Ela será excluída.`);
  if (!confirmacao) return;

  const resposta = await fetch(`http://localhost:5000/metas/deletar/${user_id}/${encodeURIComponent(nomeOriginal)}`, {
    method: "DELETE"
  });

  const dados = await resposta.json();

  if (resposta.ok) {
    alert("✅ Meta removida com sucesso!");
    listarMetas();
  } else {
    alert(`❌ Erro: ${dados.erro}`);
  }
}

// ✅ Ver gráfico
function verGrafico(nomeSafe) {
  const nomeOriginal = nomeSafe.replace(/_/g, ' ');
  localStorage.setItem('metaParaGrafico', nomeOriginal);
  window.location.href = 'grafico_regressao.html';
}

// ✅ Distribuição automática IA
async function calcularDistribuicao() {
  const valor_mensal = parseFloat(prompt("Quanto você deseja distribuir entre as metas esse mês?"));

  if (isNaN(valor_mensal) || valor_mensal <= 0) {
    alert("⚠️ Valor inválido.");
    return;
  }

  const resposta = await fetch("http://localhost:5000/metas/contribuir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, valor_mensal })
  });

  const dados = await resposta.json();

  if (resposta.ok) {
    alert("💡 Distribuição feita com sucesso!");
    listarMetas();
  } else {
    alert(`❌ Erro: ${dados.erro}`);
  }
}

// ✅ Carregar metas ao iniciar
window.onload = listarMetas;
