# TeamLineup

API para gerenciamento de jogadores, eventos e escalações, desenvolvida com Django e Django REST Framework.

## Requisitos

- Docker e Docker Compose
- VS Code com a extensão Python Debugger para depuração

## Configuração

Crie o arquivo de configuração na raiz do projeto:

```sh
cp .env.example .env
```

Se o `.env` já existir, atualize as variáveis nele. Defina a chave da aplicação e as credenciais do PostgreSQL antes de iniciar os serviços.

| Variável | Descrição |
| --- | --- |
| `DJANGO_SECRET_KEY` | Chave da aplicação |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `DB_POOL_SIZE` | Limite de conexões por pool |
| `APP_PORT` | Porta HTTP, inicialmente `8000` |
| `DEBUG_PORT` | Porta do debugger, inicialmente `5678` |
| `BIND_HOST` | Interface de publicação das portas, inicialmente `127.0.0.1` |
| `APP_PREFIX` | Prefixo de URL quando a aplicação estiver atrás de um proxy |

O Compose conecta a aplicação ao PostgreSQL em `db:5432` e habilita `DJANGO_DEBUG`. Fora do Docker, o Django usa `POSTGRES_HOST`, `POSTGRES_PORT` e `DJANGO_DEBUG` do ambiente. As variáveis `POSTGRES_*` têm prioridade sobre `DATABASE_URL` quando `POSTGRES_DB` está definida.

## Execução

```sh
docker compose up --build -d
```

As migrações são aplicadas na inicialização, após o banco estar disponível. Com as portas do `.env.example`, os endereços são:

- API: http://localhost:8000/api/v1/
- Documentação: http://localhost:8000/api/v1/docs/
- Administração: http://localhost:8000/admin/

Para acompanhar os logs:

```sh
docker compose logs -f app
```

Para criar um administrador:

```sh
docker compose exec app python manage.py createsuperuser
```

Para encerrar os serviços:

```sh
docker compose down
```

Os dados permanecem no volume `postgres_data`. As credenciais de inicialização do PostgreSQL são aplicadas apenas quando o volume está vazio. Em um banco existente, a alteração das credenciais deve ser feita também no PostgreSQL.

## Depuração

Com os serviços em execução, selecione **Django: Docker (attach)** no painel **Executar e Depurar** do VS Code e pressione **F5**. Defina os breakpoints e faça uma requisição à aplicação.

Se alterar `DEBUG_PORT`, atualize `connect.port` em `.vscode/launch.json` com o mesmo valor.

O código local é montado em `/app`. Como o servidor roda com `--noreload`, reinicie a aplicação após alterações e reconecte o debugger:

```sh
docker compose restart app
```

`BIND_HOST=127.0.0.1` restringe o acesso à máquina local. O valor `0.0.0.0` publica as portas HTTP e de debug em todas as interfaces de rede.

## Pre-commit

Os hooks executam Black, Ruff e Mypy com as configurações do `pyproject.toml`.
Black e Ruff podem alterar os arquivos; revise as alterações antes do commit.

Construa a imagem e valide a configuração:

```sh
docker compose build app
docker compose run --rm --no-deps app pre-commit validate-config
```

Execute os hooks em todos os arquivos versionados, sem iniciar o banco:

```sh
docker compose run --rm --no-deps app pre-commit run --all-files
```

Para executar apenas um hook, informe `black`, `ruff` ou `mypy`:

```sh
docker compose run --rm --no-deps app pre-commit run mypy --all-files
```

A primeira execução baixa os repositórios e instala as dependências dos hooks.

### Execução sem verificação SSL

Para executar com a verificação SSL desativada apenas no Git:

```sh
docker compose run --rm --no-deps -e GIT_SSL_NO_VERIFY=true app pre-commit run --all-files
```

Se o pip também apresentar erro de certificado ao instalar as dependências dos
hooks, adicione `PIP_TRUSTED_HOST` para os hosts do PyPI:

```sh
docker compose run --rm --no-deps -e GIT_SSL_NO_VERIFY=true -e PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org" app pre-commit run --all-files
```

Essas opções valem apenas para o comando executado. Para uso regular, configure
o certificado da rede.

A execução via Docker é manual. Para executar os hooks automaticamente no
`git commit` feito no host, instale o pre-commit no ambiente Python local:

```sh
python -m pip install ".[dev]"
pre-commit install
```
