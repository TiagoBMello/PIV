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

// 📋 Lista metas e exibe progresso e botões de aporte/remover
async function listarMetas() {
  try {
    const resposta = await fetch(`http://localhost:5000/metas/${user_id}`);
    const metas = await resposta.json();
    const lista = document.getElementById('lista-metas');
    lista.innerHTML = '';

    metas.forEach(meta => {
      const acumulado = meta.acumulado || 0;
      const progresso = Math.min(100, (acumulado / meta.valor) * 100).toFixed(0);

      const div = document.createElement('div');
      div.className = 'meta-card';
      div.innerHTML = `
        <p><strong>${meta.nome}</strong></p>
        <p>Valor total: R$${meta.valor.toFixed(2)} | Acumulado: R$${acumulado.toFixed(2)}</p>
        <p>Prazo: ${meta.prazo} meses | Prioridade: <span class="prioridade-${meta.prioridade}">${meta.prioridade.toUpperCase()}</span></p>
        <p>🎯 Progresso: ${progresso}%</p>

        ${progresso >= 100
          ? `<button onclick="retirarFundos('${meta.nome}')">💸 Retirar Fundos</button>`
          : `
            <div style="display: flex; gap: 10px; align-items: center; margin-top: 10px;">
              <input type="number" placeholder="Quanto deseja adicionar?" id="aporte-${meta.nome}" style="flex:1; padding: 5px;" />
              <button onclick="fazerAporte('${meta.nome}')">💰 Fazer Aporte</button>
              <button onclick="verGrafico('${meta.nome}')" style="background-color:#007acc;color:#fff;padding:8px;border:none;border-radius:5px;cursor:pointer;">📈 Ver Gráfico</button>
            </div>
          `}
      `;
      lista.appendChild(div);
    });
  } catch (erro) {
    console.error("Erro ao listar metas:", erro);
  }
}



// 🤖 Distribuição automática com IA (opcional)
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
    const resposta = await fetch(`http://localhost:5000/metas/deletar/${user_id}/${encodeURIComponent(nomeMeta)}`, {
      method: "DELETE"
    });

    const dados = await resposta.json();

    if (resposta.ok) {
      alert("✅ Meta removida com sucesso!");
      listarMetas();
    } else {
      alert(`❌ Erro: ${dados.erro || "Erro ao excluir meta concluída."}`);
    }
  } catch (erro) {
    alert("❌ Erro de conexão com o servidor ao tentar excluir a meta.");
    console.error("Erro:", erro);
  }
}

// 🔁 Faz um aporte de R$100 e consulta previsão
async function fazerAporte(nomeMeta) {
  const input = document.getElementById(`aporte-${nomeMeta}`);
  const valor = parseFloat(input.value);
  if (isNaN(valor) || valor <= 0) {
    alert("⚠️ Informe um valor válido para o aporte.");
    return;
  }

  // Registra o histórico no backend
  const res = await fetch("http://localhost:5000/historico", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome: nomeMeta, valor })
  });

  const dados = await res.json();

  if (res.ok) {
    alert("✅ Aporte registrado com sucesso!");
    input.value = ""; // limpa o campo
    listarMetas(); // atualiza a tela
  } else {
    alert("❌ Erro ao registrar aporte: " + dados.erro);
  }
}


// Calcula perfil de investidor
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

async function fazerAporte(nome) {
  const input = document.getElementById(`aporte-${nome}`);
  const valor = parseFloat(input.value);

  if (isNaN(valor) || valor <= 0) {
    alert("⚠️ Digite um valor válido para o aporte.");
    return;
  }

  // Registra no histórico
  await fetch("http://localhost:5000/historico", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, nome, valor })
  });

  // Atualiza o acumulado na meta
  const respostaAtualiza = await fetch(`http://localhost:5000/metas/${user_id}/atualizar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, valor })
  });

  const dados = await respostaAtualiza.json();

  if (respostaAtualiza.ok) {
    alert("✅ Aporte realizado com sucesso!");
    listarMetas();  // Atualiza a UI com o novo acumulado
  } else {
    alert(`❌ Erro: ${dados.erro || "Erro ao atualizar meta."}`);
  }
}


function verGrafico(nomeMeta) {
  localStorage.setItem('metaParaGrafico', nomeMeta);
  window.location.href = 'grafico_regressao.html';
}


// Carrega metas ao abrir
window.onload = listarMetas;
