from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"
SAIDA_WEB = RAIZ / "web" / "public" / "data"

USER_AGENT = "CorridasFuturasBot/0.1 (+https://github.com/lucaacabral/corridas-futuras-luca)"
TIMEOUT_S = 30
# Pausa entre requisições ao mesmo site, para não sobrecarregá-lo.
INTERVALO_S = 1.5
# Limites de segurança por fonte em cada execução.
MAX_PAGINAS_LISTAGEM = 30
MAX_PAGINAS_EVENTO = 400
