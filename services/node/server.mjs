/** Jason Stys: launch the corrected synthetic browser fixture on numeric loopback only. */
/* BEGIN CODE MAP (generated; npm run code-map)
 * variable: port — line 9
 * variable: instance — line 12
 * definition: stop — line 21
END CODE MAP */
import { server } from "./http.mjs";
import { fileURLToPath } from "node:url";
const port = process.argv[2] === undefined ? 0 : Number(process.argv[2]);
if (!Number.isInteger(port) || port < 0 || port > 65535)
  throw new Error("port_range");
const instance = server(fileURLToPath(new URL("../../dist", import.meta.url)));
instance.listen(port, "127.0.0.1", () =>
  console.log(
    "Local: http://127.0.0.1:" +
      instance.address().port +
      "/ — Jason Stys; synthetic encoding lab",
  ),
);
/** Stop only this owned listener; no other host processes/settings are touched. */
function stop() {
  instance.close(() => process.exit(0));
}
process.on("SIGTERM", stop);
process.on("SIGINT", stop);
