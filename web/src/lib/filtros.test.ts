import { describe, expect, it } from "vitest";
import type { Corrida, Filtros, Municipio } from "../tipos";
import { distanciaKm, faixaDe, filtrarCorridas, ufsNoRaio } from "./filtros";

const campinas: Municipio = { id: 3509502, nome: "Campinas", uf: "SP", lat: -22.9053, lon: -47.0659 };
const saoPaulo: Municipio = { id: 3550308, nome: "São Paulo", uf: "SP", lat: -23.5329, lon: -46.6395 };
const extrema: Municipio = { id: 3125101, nome: "Extrema", uf: "MG", lat: -22.854, lon: -46.3178 };
const manaus: Municipio = { id: 1302603, nome: "Manaus", uf: "AM", lat: -3.1019, lon: -60.025 };

function corrida(parcial: Partial<Corrida>): Corrida {
  return {
    id: "x", nome: "Corrida", data: "2099-01-01", cidade: "Campinas", uf: "SP", codigo_ibge: 3509502,
    lat: campinas.lat, lon: campinas.lon, distancias_km: [5], preco_min: 100,
    links: [{ fonte: "sympla", url: "https://x" }], ...parcial,
  };
}

const base: Filtros = {
  uf: "SP", cidadeId: campinas.id, raioKm: 50, faixas: [], dataInicio: "", dataFim: "",
  precoMax: null, fontesOcultas: [], busca: "",
};

describe("distanciaKm", () => {
  it("Campinas–São Paulo ≈ 84 km", () => {
    expect(distanciaKm(campinas, saoPaulo)).toBeGreaterThan(80);
    expect(distanciaKm(campinas, saoPaulo)).toBeLessThan(90);
  });
});

describe("faixaDe", () => {
  it.each([[5, "5k"], [10, "10k"], [21.1, "21k"], [42.195, "42k"], [15, "outras"], [3, "outras"]])("%s km → %s", (km, f) => {
    expect(faixaDe(km)).toBe(f);
  });
});

describe("ufsNoRaio", () => {
  it("inclui MG para Campinas com 100 km", () => {
    expect(ufsNoRaio(campinas, 100, [campinas, extrema, manaus])).toEqual(["MG", "SP"]);
  });
  it("só a própria UF com raio pequeno", () => {
    expect(ufsNoRaio(campinas, 10, [campinas, extrema])).toEqual(["SP"]);
  });
});

describe("filtrarCorridas", () => {
  const hoje = "2026-10-25";

  it("aplica raio, data passada, faixa, preço, fonte e busca", () => {
    const corridas = [
      corrida({ id: "ok", nome: "Noturna de Campinas" }),
      corrida({ id: "longe", lat: saoPaulo.lat, lon: saoPaulo.lon }),
      corrida({ id: "passada", data: "2026-10-24" }),
      corrida({ id: "cara", preco_min: 500 }),
      corrida({ id: "10k", distancias_km: [10] }),
      corrida({ id: "oculta", links: [{ fonte: "ticketsports", url: "https://y" }] }),
    ];
    const r = filtrarCorridas(corridas, campinas, { ...base, faixas: ["5k"], precoMax: 200, fontesOcultas: ["ticketsports"] }, hoje);
    expect(r.map((c) => c.id)).toEqual(["ok"]);
    expect(filtrarCorridas(corridas, campinas, { ...base, busca: "NOTURNA" }, hoje).map((c) => c.id)).toEqual(["ok"]);
  });

  it("ordena por data e depois por distância", () => {
    const r = filtrarCorridas(
      [
        corrida({ id: "b", data: "2099-02-01" }),
        corrida({ id: "a-longe", data: "2099-01-01", lat: -23.1, lon: -47.2 }),
        corrida({ id: "a-perto", data: "2099-01-01" }),
      ],
      campinas, base, hoje,
    );
    expect(r.map((c) => c.id)).toEqual(["a-perto", "a-longe", "b"]);
  });

  it("corrida sem preço não é escondida pelo filtro de preço", () => {
    expect(filtrarCorridas([corrida({ preco_min: null })], campinas, { ...base, precoMax: 50 }, hoje)).toHaveLength(1);
  });
});
