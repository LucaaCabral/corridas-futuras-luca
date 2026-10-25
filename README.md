# 🏃 Corridas Futuras

Reúne corridas de rua dos principais sites de inscrição do Brasil e mostra as que acontecem
perto de você. No site você escolhe estado, cidade e raio (padrão 50 km) e filtra por distância
da prova, data, preço e site de origem.

```
coletor (Python, sob demanda) ──> 5 sites
   │ normaliza, remove duplicadas, localiza a cidade (base IBGE)
   ▼
web/public/data/corridas/<UF>.json + indice.json
   │
web (React + Vite, estático) ──> GitHub Pages / Vercel
```

Não há servidor nem banco de dados: os JSONs gerados pelo coletor são a base de dados do site.

## Fontes

| Fonte | Status |
| --- | --- |
| [Ticket Sports](https://www.ticketsports.com.br) | ⚠️ URLs pendentes de validação |
| [Minhas Inscrições](https://www.minhasinscricoes.com.br) | ⚠️ URLs pendentes de validação |
| [Brasil Que Corre](https://brasilquecorre.com) | ⚠️ URLs pendentes de validação |
| [Corridas Brasil](https://www.corridasbrasil.com.br) | ⚠️ URLs pendentes de validação |
| [Sympla](https://www.sympla.com.br) | ⚠️ URLs pendentes de validação |

Cada fonte (`coletor/coletor/fontes/*.py`) baixa as páginas de calendário e extrai os eventos
publicados em JSON-LD (schema.org `Event`/`SportsEvent`); se a listagem não tiver JSON-LD, segue os
links de evento e extrai de cada página. Os padrões de URL foram escritos sem acesso aos sites e
precisam ser conferidos — veja "Validar uma fonte" abaixo.

## Coletar corridas

```bash
cd coletor
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e '.[dev]'

python -m coletor                       # todas as fontes
python -m coletor --fontes sympla       # só uma (as outras vêm do cache)
python -m coletor --so-exportar         # regera os JSONs a partir do cache, sem acessar os sites
```

O coletor respeita `robots.txt`, espera 1,5 s entre requisições ao mesmo site e guarda o último
resultado bom de cada fonte em `coletor/.cache/`. Se uma fonte falhar ou vier vazia, o site continua
mostrando os dados anteriores dela e exibe um aviso.

Depois de coletar, publique:

```bash
git add web/public/data && git commit -m "Atualiza corridas" && git push
```

### Validar uma fonte

```bash
python -m coletor --fontes ticketsports --salvar-html /tmp/ts -v
```

Abra os HTMLs salvos em `/tmp/ts`. Se a fonte retornar 0 corridas, ajuste `urls_listagem()` e
`padrao_link_evento` no arquivo da fonte (use a aba Rede do navegador para achar a URL do calendário
ou uma API JSON) e salve uma página como fixture em `coletor/tests/fixtures/` com um teste.

## Rodar o site

```bash
cd web
npm install
npm run dev        # http://localhost:5173
npm test
npm run build      # gera web/dist
```

## Publicar

**GitHub Pages:** em *Settings → Pages*, escolha *Source: GitHub Actions*. Cada push na `main` que
altere `web/` (incluindo novos dados) publica o site via `.github/workflows/deploy.yml`.

**Vercel (futuro):** importe o repositório, defina *Root Directory* = `web`; o preset Vite já
funciona (build `npm run build`, saída `dist`).

## Testes

- `coletor/`: `pytest` — normalização de datas/distâncias/preços, extração JSON-LD, deduplicação,
  geolocalização e exportação.
- `web/`: `npm test` — distância (haversine), faixas de distância, UFs no raio e filtros.

## Dados de municípios

`dados/municipios.json` (códigos IBGE e coordenadas) vem de
[kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) (licença MIT).
Para atualizar: `python coletor/scripts/gerar_municipios.py`.
