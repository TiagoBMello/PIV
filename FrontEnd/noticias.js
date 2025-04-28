const apiKey = '8bf93bb8d063484b8a90e16df8a6c403';

async function buscarNoticias(categoria) {
    const url = `https://gnews.io/api/v4/top-headlines?category=${categoria}&lang=pt&country=br&max=5&apikey=${apiKey}`;

    try {
        const resposta = await fetch(url);
        const dados = await resposta.json();

        const noticiasArea = document.getElementById('noticias-area');
        noticiasArea.innerHTML = ''; // Limpa

        if (dados.articles && dados.articles.length > 0) {
            dados.articles.forEach(noticia => {
                const noticiaDiv = document.createElement('div');
                noticiaDiv.classList.add('noticia');

                noticiaDiv.innerHTML = `
                    <h3>${noticia.title}</h3>
                    <p>${noticia.description || ''}</p>
                    <a href="${noticia.url}" target="_blank">🔗 Ler mais</a>
                `;
                noticiasArea.appendChild(noticiaDiv);
            });
        } else {
            noticiasArea.innerHTML = '<p>⚠️ Nenhuma notícia encontrada para esta categoria.</p>';
        }
    } catch (error) {
        console.error('Erro ao buscar notícias:', error);
        noticiasArea.innerHTML = '<p>❌ Erro ao carregar notícias. Tente novamente mais tarde.</p>';
    }
}
