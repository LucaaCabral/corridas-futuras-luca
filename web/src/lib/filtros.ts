import type { Corrida, FaixaDistancia, Filtros, Municipio } from "../tipos";

const RAIO_TERRA_KM = 6371;

export function distanciaKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const rad = (g: number) => (g * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat);
  const dLon = rad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * RAIO_TERRA_KM * Math.asin(Math.sqrt(h));
}

export const FAIXAS: { id: FaixaDistancia; rotulo: string }[] = [
  { id: "5k", rotulo: "5 km" },
  { id: "10k", rotulo: "10 km" },
  { id: "21k", rotulo: "21 km" },
  { id: "42k", rotulo: "42 km" },
  { id: "outras", rotulo: "Outras" },
];

export function faixaDe(km: number): FaixaDistancia {
  if (km >= 4 && km <= 6) return "5k";
  if (km >= 8 && km <= 12) return "10k";
  if (km >= 20 && km <= 22.5) return "21k";
  if (km >= 40 && km <= 45) return "42k";
  return "outras";
}

/** UFs que têm algum município dentro do raio — um raio de 50 km pode cruzar a divisa. */
export function ufsNoRaio(centro: Municipio, raioKm: number, municipios: Municipio[]): string[] {
  const ufs = new Set([centro.uf]);
  for (const m of municipios) {
    if (!ufs.has(m.uf) && distanciaKm(centro, m) <= raioKm) ufs.add(m.uf);
  }
  return [...ufs].sort();
}

export interface CorridaComDistancia extends Corrida {
  distanciaCentroKm: number;
}

export function filtrarCorridas(
  corridas: Corrida[],
  centro: Municipio,
  filtros: Filtros,
  hoje: string,
): CorridaComDistancia[] {
  const busca = normalizar(filtros.busca);
  const inicio = filtros.dataInicio && filtros.dataInicio > hoje ? filtros.dataInicio : hoje;

  return corridas
    .map((c) => ({ ...c, distanciaCentroKm: distanciaKm(centro, c) }))
    .filter((c) => {
      if (c.distanciaCentroKm > filtros.raioKm) return false;
      if (c.data < inicio) return false;
      if (filtros.dataFim && c.data > filtros.dataFim) return false;
      if (filtros.precoMax !== null && c.preco_min !== null && c.preco_min > filtros.precoMax) return false;
      if (filtros.fontesOcultas.length && c.links.every((l) => filtros.fontesOcultas.includes(l.fonte))) return false;
      if (filtros.faixas.length && !c.distancias_km.some((km) => filtros.faixas.includes(faixaDe(km)))) return false;
      if (busca && !normalizar(`${c.nome} ${c.cidade}`).includes(busca)) return false;
      return true;
    })
    .sort((a, b) => a.data.localeCompare(b.data) || a.distanciaCentroKm - b.distanciaCentroKm);
}

export function normalizar(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();
}

export function hojeIso(agora = new Date()): string {
  const local = new Date(agora.getTime() - agora.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}
