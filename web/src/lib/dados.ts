import { useEffect, useState } from "react";
import type { Corrida, Estado, Indice, Municipio } from "../tipos";

async function buscarJson<T>(caminho: string): Promise<T> {
  const resp = await fetch(`${import.meta.env.BASE_URL}data/${caminho}`);
  if (!resp.ok) throw new Error(`Falha ao carregar ${caminho} (HTTP ${resp.status})`);
  return resp.json() as Promise<T>;
}

export interface DadosBase {
  estados: Estado[];
  municipios: Municipio[];
  indice: Indice | null;
}

export function useDadosBase() {
  const [dados, setDados] = useState<DadosBase | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      buscarJson<Estado[]>("estados.json"),
      buscarJson<Municipio[]>("municipios.json"),
      // Sem indice.json o coletor ainda não rodou: o site abre mesmo assim.
      buscarJson<Indice>("indice.json").catch(() => null),
    ])
      .then(([estados, municipios, indice]) => setDados({ estados, municipios, indice }))
      .catch((e: Error) => setErro(e.message));
  }, []);

  return { dados, erro };
}

const cacheUf = new Map<string, Promise<Corrida[]>>();

function corridasDaUf(uf: string): Promise<Corrida[]> {
  let p = cacheUf.get(uf);
  if (!p) {
    p = buscarJson<Corrida[]>(`corridas/${uf}.json`).catch(() => {
      cacheUf.delete(uf);
      return [];
    });
    cacheUf.set(uf, p);
  }
  return p;
}

/** Carrega (com cache) as corridas das UFs pedidas que existem no índice. */
export function useCorridas(ufs: string[], indice: Indice | null) {
  const [corridas, setCorridas] = useState<Corrida[]>([]);
  const [carregando, setCarregando] = useState(false);
  const chave = ufs.filter((uf) => indice?.por_uf[uf]).join(",");

  useEffect(() => {
    if (!chave) {
      setCorridas([]);
      return;
    }
    let ativo = true;
    setCarregando(true);
    Promise.all(chave.split(",").map(corridasDaUf)).then((listas) => {
      if (ativo) {
        setCorridas(listas.flat());
        setCarregando(false);
      }
    });
    return () => {
      ativo = false;
    };
  }, [chave]);

  return { corridas, carregando };
}
