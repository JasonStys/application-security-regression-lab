/** Jason Stys: accessible browser encoding exercise. Java/C#/PHP are independent native fixture services. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * variable: revision — line 16
 * definition: element — line 18
 * parameter: id — line 18
 * variable: result — line 19
 * definition: run — line 24
 * parameter: action — line 24
 * parameter: error — line 25
 * definition: preview — line 31
 * variable: requestedRevision — line 45
 * variable: response — line 46
 * variable: value — line 50
END CODE MAP */
import { renderText, sample } from "./text.js";
let revision = 0;
/** Require the known authored controls instead of silently accepting a broken UI contract. */
function element<T extends HTMLElement>(id: string): T {
  const result = document.getElementById(id);
  if (!result) throw new Error("Missing authored control");
  return result as T;
}
/** Run explicit local work and announce errors without reflecting labels as executable HTML. */
function run(action: () => Promise<void>): void {
  void action().catch((error) => {
    element("status").textContent =
      error instanceof Error ? error.message : "Local operation failed";
  });
}
/** Render only user-supplied literal text; no input is transmitted by this exercise. */
async function preview(): Promise<void> {
  renderText(element("preview"), element<HTMLTextAreaElement>("label").value);
  element("status").textContent =
    "Rendered as literal text; no code, links or image elements were created.";
}
element("label").addEventListener("input", () => {
  revision++;
});
element("render").addEventListener("click", () => {
  revision++;
  run(preview);
});
element("fetch").addEventListener("click", () =>
  run(async () => {
    const requestedRevision = ++revision;
    const response = await fetch("/sample", {
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) throw new Error("Local fixture unavailable");
    const value = sample((await response.json()) as unknown);
    if (requestedRevision !== revision) {
      element("status").textContent =
        "Earlier fixture response ignored because your input changed.";
      return;
    }
    element<HTMLTextAreaElement>("label").value = value;
    await preview();
    element("status").textContent =
      "Fetched local fixture and rendered as literal text.";
  }),
);
run(preview);
