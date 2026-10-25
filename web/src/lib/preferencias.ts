import { useEffect, useState } from "react";
import type { Filtros } from "../tipos";

const CHAVE = "corridas-futuras:filtros";

export const FILTROS_PADRAO: Filtros = {
  uf: "",
  cidadeId: null,
  raioKm: 50,
  faixas: [],
  dataInicio: "",
  dataFim: "",
  precoMax: null,
  fontesOcultas: [],
  busca: "",
};

function ler(): Filtros {
  try {
    const salvo = localStorage.getItem(CHAVE);
    return salvo ? { ...FILTROS_PADRAO, ...JSON.parse(salvo) } : FILTROS_PADRAO;
  } catch {
    return FILTROS_PADRAO;
  }
}

/** Filtros lembrados entre visitas (só neste navegador). */
export function useFiltros() {
  const [filtros, setFiltros] = useState<Filtros>(ler);
  useEffect(() => {
    try {
      localStorage.setItem(CHAVE, JSON.stringify(filtros));
    } catch {
      // navegação privada ou armazenamento bloqueado: segue sem lembrar
    }
  }, [filtros]);
  return [filtros, setFiltros] as const;
}
