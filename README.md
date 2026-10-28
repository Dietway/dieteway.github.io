# Dietway — publicação

Publica no Instagram os posts de [@diet_way](https://www.instagram.com/diet_way/) no horário de cada um, pelo GitHub Actions.

- `queue.json`: a fila. O workflow `publish` marca cada post como publicado.
- `gh-pages`: redirecionamento para https://dietway.com.br, o painel de status e a mídia que o Instagram baixa. Fica em https://dieteway.github.io.
- `publisher/`, `shared/` e `.github/` são copiados de um repositório privado a cada lote semanal. Alterações feitas aqui são sobrescritas.

Painel de publicação: https://dieteway.github.io/status.html
