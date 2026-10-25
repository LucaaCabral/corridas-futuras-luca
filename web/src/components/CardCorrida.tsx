import type { CorridaComDistancia } from "../lib/filtros";
import { formatarData, formatarDistancia, formatarPreco, nomeFonte } from "../lib/formato";

export function CardCorrida({ corrida }: { corrida: CorridaComDistancia }) {
  return (
    <article className="card">
      <div className="card-data">{formatarData(corrida.data)}</div>
      <h3>{corrida.nome}</h3>
      <p className="card-local">
        {corrida.cidade} – {corrida.uf}
        <span className="muted"> · {Math.round(corrida.distanciaCentroKm)} km de você</span>
      </p>
      {corrida.distancias_km.length > 0 && (
        <ul className="distancias">
          {corrida.distancias_km.map((km) => (
            <li key={km}>{formatarDistancia(km)}</li>
          ))}
        </ul>
      )}
      <div className="card-rodape">
        <span className="preco">{corrida.preco_min !== null ? formatarPreco(corrida.preco_min) : "Preço no site"}</span>
        <span className="links">
          {corrida.links.map((l) => (
            <a key={l.url} href={l.url} target="_blank" rel="noopener noreferrer">
              {nomeFonte(l.fonte)} ↗
            </a>
          ))}
        </span>
      </div>
    </article>
  );
}
