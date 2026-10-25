import type { Estado, FaixaDistancia, Filtros, Municipio } from "../tipos";
import { FAIXAS } from "../lib/filtros";
import { nomeFonte } from "../lib/formato";
import { SeletorCidade } from "./SeletorCidade";

interface Props {
  filtros: Filtros;
  setFiltros: (f: Filtros) => void;
  estados: Estado[];
  municipios: Municipio[];
  fontes: string[];
  onLimpar: () => void;
}

export function PainelFiltros({ filtros, setFiltros, estados, municipios, fontes, onLimpar }: Props) {
  const mudar = (parcial: Partial<Filtros>) => setFiltros({ ...filtros, ...parcial });
  const alternar = <T,>(lista: T[], item: T) => (lista.includes(item) ? lista.filter((x) => x !== item) : [...lista, item]);

  return (
    <aside className="painel" aria-label="Filtros">
      <SeletorCidade
        estados={estados}
        municipios={municipios}
        uf={filtros.uf}
        cidadeId={filtros.cidadeId}
        onChange={(uf, cidadeId) => mudar({ uf, cidadeId })}
      />

      <label>
        <span>
          Raio: <strong>{filtros.raioKm} km</strong>
        </span>
        <input
          type="range"
          min={5}
          max={200}
          step={5}
          value={filtros.raioKm}
          onChange={(e) => mudar({ raioKm: Number(e.target.value) })}
        />
      </label>

      <fieldset>
        <legend>Distância da prova</legend>
        <div className="chips">
          {FAIXAS.map((f) => (
            <button
              key={f.id}
              type="button"
              className="chip"
              aria-pressed={filtros.faixas.includes(f.id)}
              onClick={() => mudar({ faixas: alternar<FaixaDistancia>(filtros.faixas, f.id) })}
            >
              {f.rotulo}
            </button>
          ))}
        </div>
      </fieldset>

      <div className="grupo">
        <label>
          De
          <input type="date" value={filtros.dataInicio} onChange={(e) => mudar({ dataInicio: e.target.value })} />
        </label>
        <label>
          Até
          <input type="date" value={filtros.dataFim} onChange={(e) => mudar({ dataFim: e.target.value })} />
        </label>
      </div>

      <label>
        Preço máximo (R$)
        <input
          type="number"
          min={0}
          step={10}
          inputMode="numeric"
          placeholder="Sem limite"
          value={filtros.precoMax ?? ""}
          onChange={(e) => mudar({ precoMax: e.target.value === "" ? null : Number(e.target.value) })}
        />
      </label>

      {fontes.length > 0 && (
        <fieldset>
          <legend>Sites</legend>
          {fontes.map((f) => (
            <label key={f} className="check">
              <input
                type="checkbox"
                checked={!filtros.fontesOcultas.includes(f)}
                onChange={() => mudar({ fontesOcultas: alternar(filtros.fontesOcultas, f) })}
              />
              {nomeFonte(f)}
            </label>
          ))}
        </fieldset>
      )}

      <button type="button" className="secundario" onClick={onLimpar}>
        Limpar filtros
      </button>
    </aside>
  );
}
