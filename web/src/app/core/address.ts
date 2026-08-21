import { Address } from '../models/models';

/**
 * Setzt eine strukturierte {@link Address} zu einer menschenlesbaren Zeile
 * `"Straße Hausnummer, PLZ Ort"` zusammen und lässt fehlende (`null`/leere)
 * Bestandteile sauber weg (US-022). Gibt `null` zurück, wenn kein Feld gesetzt
 * ist. Einzige Stelle, an der aus dem Objekt ein Anzeige-String wird (DRY):
 * genutzt von Suche, Detailseiten und ICS-Export.
 */
export function formatAddress(address: Address | null | undefined): string | null {
  if (!address) return null;
  const trim = (value: string | null): string => value?.trim() ?? '';
  const streetLine = [trim(address.street), trim(address.houseNumber)]
    .filter((part) => part.length > 0)
    .join(' ');
  const cityLine = [trim(address.postalCode), trim(address.city)]
    .filter((part) => part.length > 0)
    .join(' ');
  const line = [streetLine, cityLine].filter((part) => part.length > 0).join(', ');
  return line.length > 0 ? line : null;
}
