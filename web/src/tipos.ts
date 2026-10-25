export interface Estado {
  uf: string;
  nome: string;
}

export interface Municipio {
  id: number;
  nome: string;
  uf: string;
  lat: number;
  lon: number;
}

export interface Link {
  fonte: string;
  url: string;
}

export interface Corrida {
  id: string;
  nome: string;
  data: string; // AAAA-MM-DD
  cidade: string;
  uf: string;
  codigo_ibge: number;
  lat: number;
  lon: number;
  distancias_km: number[];
  preco_min: number | null;
  links: Link[];
}

export interface InfoFonte {
  ok: boolean;
  total?: number;
  coletado_em?: string | null;
  erro?: string;
}

export interface Indice {
  gerado_em: string;
  total: number;
  por_uf: Record<string, number>;
  fontes: Record<string, InfoFonte>;
}

export type FaixaDistancia = "5k" | "10k" | "21k" | "42k" | "outras";

export interface Filtros {
  uf: string;
  cidadeId: number | null;
  raioKm: number;
  faixas: FaixaDistancia[];
  dataInicio: string;
  dataFim: string;
  precoMax: number | null;
  fontesOcultas: string[];
  busca: string;
}
