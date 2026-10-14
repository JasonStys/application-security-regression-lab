/** Jason Stys: validate bounded Unicode and render it as text, never markup, attributes, URLs or code. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * definition: label — line 12
 * parameter: value — line 12
 * definition: renderText — line 22
 * parameter: target — line 22
 * parameter: value — line 22
 * definition: sample — line 26
 * parameter: value — line 26
END CODE MAP */
/** Accept Unicode scalar text bounded by UTF8 bytes; reject missing/wrong types and isolated surrogates. */
export function label(value: unknown): string {
  if (
    typeof value !== "string" ||
    new TextEncoder().encode(value).length > 4096 ||
    /[\uD800-\uDFFF]/u.test(value)
  )
    throw new Error("Label must be valid text of at most 4096 UTF8 bytes");
  return value;
}
/** Assign validated text through a safe DOM sink; malformed inputs leave previous output intact. */
export function renderText(target: HTMLElement, value: unknown): void {
  target.textContent = label(value);
}
/** Check runtime JSON shape; static TypeScript cannot validate an untrusted HTTP response. */
export function sample(value: unknown): string {
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value) ||
    Object.keys(value).length !== 3 ||
    !("component" in value) ||
    value.component !== "node" ||
    !("synthetic" in value) ||
    value.synthetic !== true ||
    !("label" in value)
  )
    throw new Error("Invalid synthetic fixture response");
  return label(value.label);
}
