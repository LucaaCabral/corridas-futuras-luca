import { useEffect, useMemo, useState } from "react";
import type { Estado, Municipio } from "../tipos";
import { normalizar } from "../lib/filtros";

interface Props {
  estados: Estado[];
  municipios: Municipio[];
  uf: string;
  cidadeId: number | null;
  onChange: (uf: string, cidadeId: number | null) => void;
}

export function SeletorCidade({ estados, municipios, uf, cidadeId, onChange }: Props) {
  const daUf = useMemo(() => municipios.filter((m) => m.uf === uf), [municipios, uf]);
  const atual = daUf.find((m) => m.id === cidadeId);
  const [texto, setTexto] = useState(atual?.nome ?? "");

  useEffect(() => setTexto(atual?.nome ?? ""), [atual?.nome]);

  function escolherCidade(valor: string) {
    setTexto(valor);
    const alvo = normalizar(valor);
    const m = daUf.find((c) => normalizar(c.nome) === alvo);
    if (m) onChange(uf, m.id);
  }

  return (
    <div className="grupo">
      <label>
        Estado
        <select value={uf} onChange={(e) => onChange(e.target.value, null)}>
          <option value="">Selecione…</option>
          {estados.map((e) => (
            <option key={e.uf} value={e.uf}>
              {e.nome}
            </option>
          ))}
        </select>
      </label>
      <label>
        Cidade
        <input
          list="lista-cidades"
          value={texto}
          disabled={!uf}
          placeholder={uf ? "Digite a cidade" : "Escolha o estado primeiro"}
          onChange={(e) => escolherCidade(e.target.value)}
          aria-invalid={texto !== "" && !atual}
        />
        <datalist id="lista-cidades">
          {daUf.map((m) => (
            <option key={m.id} value={m.nome} />
          ))}
        </datalist>
      </label>
    </div>
  );
}
