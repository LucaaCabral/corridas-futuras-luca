import { useMemo } from "react";
import { CardCorrida } from "./components/CardCorrida";
import { PainelFiltros } from "./components/PainelFiltros";
import { useCorridas, useDadosBase } from "./lib/dados";
import { filtrarCorridas, hojeIso, ufsNoRaio } from "./lib/filtros";
import { formatarDataHora, nomeFonte } from "./lib/formato";
import { FILTROS_PADRAO, useFiltros } from "./lib/preferencias";

export default function App() {
  const { dados, erro } = useDadosBase();
  const [filtros, setFiltros] = useFiltros();

  const centro = useMemo(
    () => dados?.municipios.find((m) => m.id === filtros.cidadeId) ?? null,
    [dados, filtros.cidadeId],
  );
  const ufs = useMemo(
    () => (centro && dados ? ufsNoRaio(centro, filtros.raioKm, dados.municipios) : []),
    [centro, dados, filtros.raioKm],
  );
  const { corridas, carregando } = useCorridas(ufs, dados?.indice ?? null);
  const resultado = useMemo(
    () => (centro ? filtrarCorridas(corridas, centro, filtros, hojeIso()) : []),
    [corridas, centro, filtros],
  );

  if (erro) return <main className="aviso">Não foi possível carregar os dados: {erro}</main>;
  if (!dados) return <main className="aviso">Carregando…</main>;

  const indice = dados.indice;
  const fontes = Object.keys(indice?.fontes ?? {});
  const fontesComErro = fontes.filter((f) => !indice?.fontes[f].ok);

  return (
    <div className="layout">
      <header>
        <h1>🏃 Corridas Futuras</h1>
        <p className="muted">
          {indice
            ? `${indice.total} corridas no Brasil · atualizado em ${formatarDataHora(indice.gerado_em)}`
            : "Nenhuma coleta ainda — rode o coletor (veja o README)."}
        </p>
      </header>

      <PainelFiltros
        filtros={filtros}
        setFiltros={setFiltros}
        estados={dados.estados}
        municipios={dados.municipios}
        fontes={fontes}
        onLimpar={() => setFiltros({ ...FILTROS_PADRAO, uf: filtros.uf, cidadeId: filtros.cidadeId })}
      />

      <main>
        {fontesComErro.length > 0 && (
          <p className="alerta">
            Sem dados recentes de: {fontesComErro.map(nomeFonte).join(", ")}.
          </p>
        )}
        {!centro ? (
          <p className="vazio">Escolha o estado e a cidade para ver as corridas por perto.</p>
        ) : carregando ? (
          <p className="vazio">Carregando corridas…</p>
        ) : resultado.length === 0 ? (
          <p className="vazio">
            Nenhuma corrida encontrada a até {filtros.raioKm} km de {centro.nome}. Tente aumentar o raio ou
            afrouxar os filtros.
          </p>
        ) : (
          <>
            <p className="muted contagem">
              {resultado.length} corrida{resultado.length > 1 ? "s" : ""} a até {filtros.raioKm} km de {centro.nome}
            </p>
            <div className="lista">
              {resultado.map((c) => (
                <CardCorrida key={c.id} corrida={c} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
