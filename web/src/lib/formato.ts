export const NOMES_FONTE: Record<string, string> = {
  ticketsports: "Ticket Sports",
  minhasinscricoes: "Minhas Inscrições",
  brasilquecorre: "Brasil Que Corre",
  corridasbrasil: "Corridas Brasil",
  sympla: "Sympla",
};

export const nomeFonte = (id: string) => NOMES_FONTE[id] ?? id;

const fmtData = new Intl.DateTimeFormat("pt-BR", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });
const fmtDataHora = new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" });
const fmtPreco = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export const formatarData = (iso: string) => fmtData.format(new Date(`${iso}T12:00:00`));
export const formatarDataHora = (iso: string) => fmtDataHora.format(new Date(iso));
export const formatarPreco = (v: number) => (v === 0 ? "Grátis" : `a partir de ${fmtPreco.format(v)}`);

export function formatarDistancia(km: number): string {
  if (Math.abs(km - 21.1) < 0.2) return "21K";
  if (Math.abs(km - 42.195) < 0.2) return "42K";
  return `${km.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}K`;
}
