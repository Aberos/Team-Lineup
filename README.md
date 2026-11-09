# TeamLineup

Sistema para organizar eventos esportivos: cadastro de jogadores, inscrição em eventos, montagem de times e registro de partidas.

## Funcionalidades

- Cadastro de jogadores, com foto, e das funções (posições) em que atuam, com uma função principal
- Atributos dos jogadores (ex.: velocidade, passe), com nota de 0 a 100; até 6 aparecem na carta do jogador, com sigla e posição
- Nota geral do jogador calculada pela média dos atributos da carta ou por uma fórmula em Lua configurada pelo administrador
- Listagem de jogadores paginada, com busca por nome, filtro por função e ordenação
- Eventos com data e local
- Inscrição de jogadores nos eventos, com pontuação
- Montagem de times dentro de cada evento
- Partidas entre os times, com placar e situação
- Login com JWT, com opções de manter conectado e lembrar o usuário

## Tecnologias

- **Backend:** Python 3.12, Django 6, Django REST Framework, Simple JWT e drf-spectacular
- **Banco de dados:** PostgreSQL 17
- **Frontend:** React, TypeScript, Vite, Tailwind CSS e shadcn/ui
- **Ambiente:** Docker e Docker Compose

## Estrutura

```
apps/
  core/       autenticação e dados do usuário
  players/    jogadores, funções e atributos
  events/     eventos, participantes, times e partidas
config/       configurações do Django
frontend/     aplicação React
scripts/      script de inicialização do container
```

## Como executar

Copie o arquivo de exemplo e ajuste as variáveis:

```sh
cp .env.example .env
```

Suba os serviços:

```sh
docker compose up --build -d
```

Na inicialização, o container instala as dependências do frontend, gera o build, aplica as migrações, cadastra as funções e os atributos padrão e inicia o Django. Endereços:

- Aplicação: http://localhost:8000/
- API: http://localhost:8000/api/v1/
- Documentação da API: http://localhost:8000/api/v1/docs/
- Admin: http://localhost:8000/admin/

Para ver os logs e para parar os serviços:

```sh
docker compose logs -f app
docker compose down
```

Os dados do banco ficam no volume `postgres_data`.

## Dados iniciais

O sistema já vem com estas funções e atributos cadastrados:

- **Funções:** DEF, MID e ATK
- **Atributos:** Velocidade, Passe, Finalização, Drible, Defesa e Físico

O cadastro é feito pelo comando abaixo, executado automaticamente ao subir o container. Ele só cria o que ainda não existe, então pode ser rodado mais de uma vez:

```sh
docker compose exec app python manage.py seed_defaults
```

## Criar superusuário

Com os serviços em execução, crie o usuário administrador. Ele é usado para entrar na aplicação e no admin do Django:

```sh
docker compose exec app python manage.py createsuperuser
```

O comando pede usuário, e-mail e senha. Para criar sem perguntas, informe os dados por variáveis de ambiente:

```sh
docker compose exec \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  -e DJANGO_SUPERUSER_PASSWORD=troque-esta-senha \
  app python manage.py createsuperuser --noinput
```

## Fórmula da nota geral

Usuários administradores (`is_staff`, os mesmos que acessam o admin do Django) veem o menu **Fórmula**, onde escrevem em Lua como a nota geral é calculada. O script define `overall(notas, funcoes, principal)` e retorna um número de 0 a 100, ou `nil` para "sem avaliação":

```lua
function overall(notas, funcoes, principal)
  local base = notas.VEL or 0
  if principal == "DEF" then base = base + 10 end
  return math.min(100, base)
end
```

Cada fórmula salva vira uma versão; antes de ativar, é possível testá-la com os jogadores cadastrados. A ativação roda a fórmula em todos os jogadores e só acontece se ela funcionar para todos. O script roda em um ambiente isolado, sem acesso a arquivos, rede ou sistema, com limite de instruções e de memória. Sem fórmula ativa, vale a média simples.

## Variáveis de ambiente

| Variável | Descrição |
| --- | --- |
| `DJANGO_SECRET_KEY` | Chave secreta do Django |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `DB_POOL_SIZE` | Limite de conexões do pool |
| `APP_PORT` | Porta da aplicação (padrão `8000`) |
| `DEBUG_PORT` | Porta do debugger (padrão `5678`) |
| `BIND_HOST` | Interface onde as portas são publicadas (padrão `127.0.0.1`) |
| `APP_PREFIX` | Prefixo de URL quando a aplicação roda atrás de um proxy |
| `JWT_ACCESS_MINUTES` | Validade do token de acesso, em minutos (padrão `15`) |
| `JWT_REFRESH_DAYS` | Validade da sessão com "Manter conectado", em dias (padrão `7`); cada uso renova o prazo |

## Desenvolvimento

### Frontend

Com o Docker em execução, o frontend é recompilado a cada alteração; basta recarregar a página.

Para usar o servidor do Vite com recarga instantânea (em http://localhost:5173/, com o backend rodando na porta 8000):

```sh
cd frontend
npm install
npm run dev
```

### Testes e qualidade

Backend:

```sh
docker compose exec app python manage.py test
docker compose run --rm --no-deps app pre-commit run --all-files
```

Frontend:

```sh
cd frontend
npm run lint
npm run typecheck
npm run test -- --run
```

Para rodar o pre-commit automaticamente a cada commit:

```sh
python -m pip install ".[dev]"
pre-commit install
```

### Depuração

Com os serviços em execução, use a configuração **Django: Docker (attach)** do VS Code (F5). Como o servidor roda sem recarga automática, reinicie após alterar o backend:

```sh
docker compose restart app
```

## Produção

A imagem gerada pelo `Dockerfile` já inclui o build do frontend e os arquivos estáticos coletados. As fotos dos jogadores são gravadas em `media/` (no Docker, dentro do projeto montado em `/app`); em produção, essa pasta precisa de armazenamento persistente e o proxy deve servir `<APP_PREFIX>/media/` a partir dela. Quando `APP_PREFIX` estiver definido, o proxy deve remover o prefixo antes de repassar as requisições e servir `<APP_PREFIX>/static/` a partir da pasta `staticfiles/`.
