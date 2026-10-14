"""Jason Stys: actual expected/observed application-boundary cases across four independent native adapters."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: exercise — line 58
# parameter: component — line 58
# parameter: port — line 58
# variable: origin — line 60
# variable: owner — line 61
# variable: mutation — line 62
# variable: cases — line 68
# definition: case — line 70
# parameter: name — line 71
# parameter: expected — line 72
# parameter: path — line 73
# parameter: method — line 74
# parameter: body — line 75
# parameter: headers — line 76
# parameter: contains — line 77
# parameter: absent — line 78
# variable: latency — line 81
# variable: raw — line 81
# variable: received — line 81
# variable: status — line 81
# variable: content — line 82
# variable: content — line 89
# variable: content — line 91
# variable: raw — line 123
# variable: cross — line 135
# variable: name — line 170
# variable: value — line 170
# variable: raw — line 185
# variable: name — line 200
# variable: value — line 200
# variable: data — line 216
# variable: received — line 216
# variable: identifier — line 219
# variable: data — line 222
# variable: received — line 222
# variable: mutation — line 254
# variable: _ — line 292
# variable: first — line 292
# variable: cookie — line 301
# variable: attributes — line 302
# variable: item — line 303
# variable: _ — line 311
# variable: peer — line 311
# variable: peer_cookie — line 319
# END CODE MAP

from __future__ import annotations

import urllib.parse
from typing import Any

from .evidence import LabError, decode
from .transport import request


def exercise(component: str, port: int) -> list[dict[str, Any]]:
    """Evaluate concrete owned-fixture HTTP behavior; every case includes content/privacy invariants, not status alone."""
    origin = "http://127.0.0.1:" + str(port)
    owner = {"Authorization": "Bearer fixture-alpha-owner"}
    mutation = {
        "Origin": origin,
        "X-Lab-Exercise": "synthetic",
        "Content-Type": "application/x-www-form-urlencoded",
        **owner,
    }
    cases = []

    def case(
        name: str,
        expected: int,
        path: str,
        method: str = "GET",
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        contains: bytes | None = None,
        absent: bytes | None = None,
    ) -> tuple[dict[str, str], bytes]:
        """Record evaluated response/status and common no-store/nosniff/no-CORS privacy boundaries."""
        status, received, raw, latency = request(port, path, method, body, headers)
        content = (
            received.get("x-lab-component") == component
            and received.get("cache-control") == "no-store"
            and received.get("x-content-type-options") == "nosniff"
            and "access-control-allow-origin" not in received
        )
        if contains is not None:
            content = content and contains in raw
        if absent is not None:
            content = content and absent not in raw
        cases.append(
            {
                "id": component.upper() + "-" + name,
                "component": component,
                "expected": expected,
                "observed": status,
                "content_ok": content,
                "elapsed_ms": latency,
            }
        )
        return received, raw

    case("HEALTH", 200, "/health", contains=b'"synthetic":true')
    case("HOST", 403, "/health", headers={"Host": "evil.invalid"})
    case("ORIGIN", 403, "/health", headers={"Origin": "http://evil.invalid"})
    case("FETCH-SITE", 403, "/health", headers={"Sec-Fetch-Site": "cross-site"})
    case("UNKNOWN-ROUTE", 404, "/unknown", absent=b"fixture-alpha-owner")
    if component == "java":
        case("READ-OWN", 200, "/record?id=alpha-note", headers=owner, contains=b"Alpha")
        case("READ-CROSS", 404, "/record?id=beta-note", headers=owner, absent=b"Beta")
        case("READ-MISSING", 404, "/record?id=absent", headers=owner)
        case("NO-AUTH", 401, "/record?id=alpha-note", absent=b"Alpha")
        case(
            "FORGED-AUTH",
            401,
            "/record?id=alpha-note",
            headers={"Authorization": "Bearer claimed-admin"},
            absent=b"Alpha",
        )
        case("DUPLICATE-ID", 400, "/record?id=alpha-note&id=beta-note", headers=owner)
        case("CLIENT-SCOPE", 400, "/record?id=alpha-note&tenant=beta", headers=owner)
        raw = urllib.parse.urlencode(
            {"id": "alpha-note", "version": "1", "body": "Synthetic revised record"}
        ).encode()
        case("NO-CSRF", 403, "/record", "POST", raw, owner)
        case(
            "VIEWER-WRITE",
            403,
            "/record",
            "POST",
            raw,
            {**mutation, "Authorization": "Bearer fixture-alpha-viewer"},
        )
        cross = urllib.parse.urlencode(
            {"id": "beta-note", "version": "1", "body": "Changed"}
        ).encode()
        case("CROSS-WRITE", 404, "/record", "POST", cross, mutation, absent=b"Beta")
        case(
            "WRITE-OWN", 200, "/record", "POST", raw, mutation, contains=b'"version":2'
        )
        case("STALE-WRITE", 409, "/record", "POST", raw, mutation)
        case(
            "VERIFY-ATOMIC",
            200,
            "/record?id=alpha-note",
            headers=owner,
            contains=b"Synthetic revised record",
        )
        case("OVERSIZE", 413, "/record", "POST", b"x" * 4097, mutation)
        case("UNKNOWN-METHOD", 405, "/record", "DELETE", headers=owner)
    elif component == "php":
        case(
            "SEARCH-OWN",
            200,
            "/search?q=Alpha",
            headers=owner,
            contains=b"alpha-note",
            absent=b"beta-note",
        )
        case(
            "SEARCH-CROSS",
            200,
            "/search?q=Beta",
            headers=owner,
            contains=b"[]",
            absent=b"Beta",
        )
        case("NO-AUTH", 401, "/search?q=", absent=b"Alpha")
        for name, value in [
            ("SQL-INJECTION", "' OR 1=1 --"),
            ("LIKE-WILDCARD", "%"),
            ("LIKE-UNDERSCORE", "_"),
        ]:
            case(
                name,
                200,
                "/search?" + urllib.parse.urlencode({"q": value}),
                headers=owner,
                contains=b"[]",
                absent=b"beta-note",
            )
        case("DUPLICATE-QUERY", 400, "/search?q=a&q=b", headers=owner)
        case("CLIENT-SCOPE", 400, "/search?q=a&tenant=beta", headers=owner)
        raw = urllib.parse.urlencode(
            {
                "filename": "report.txt",
                "content": "<img src=x onerror=alert(1)> synthetic",
            }
        ).encode()
        case("NO-CSRF", 403, "/upload", "POST", raw, owner)
        case(
            "VIEWER-UPLOAD",
            403,
            "/upload",
            "POST",
            raw,
            {**mutation, "Authorization": "Bearer fixture-alpha-viewer"},
        )
        for name, value in [
            ("TRAVERSAL", "../x.txt"),
            ("SCRIPT", "x.php"),
            ("DOUBLE-EXTENSION", "x.php.txt"),
            ("DEVICE", "CON.txt"),
        ]:
            case(
                name,
                400,
                "/upload",
                "POST",
                urllib.parse.urlencode(
                    {"filename": value, "content": "hello"}
                ).encode(),
                mutation,
            )
        received, data = case(
            "UPLOAD", 200, "/upload", "POST", raw, mutation, contains=b'"id":'
        )
        identifier = decode(data).get("id")
        if not isinstance(identifier, str):
            raise LabError("upload_evidence")
        received, data = case(
            "DOWNLOAD-LITERAL",
            200,
            "/download?id=" + identifier,
            headers=owner,
            contains=b"<img src=x",
        )
        cases[-1]["content_ok"] = (
            cases[-1]["content_ok"]
            and received.get("content-disposition")
            == 'attachment; filename="report.txt"'
            and received.get("content-type", "").startswith("text/plain")
        )
        case(
            "CROSS-DOWNLOAD",
            404,
            "/download?id=" + identifier,
            headers={"Authorization": "Bearer fixture-beta-owner"},
            absent=b"<img",
        )
        case(
            "CONTENT-SIZE",
            400,
            "/upload",
            "POST",
            urllib.parse.urlencode(
                {"filename": "x.txt", "content": "x" * 4097}
            ).encode(),
            mutation,
        )
        case("INVALID-PERCENT", 400, "/search?q=%FF", headers=owner)
    elif component == "session":
        mutation = {
            "Origin": origin,
            "X-Lab-Exercise": "synthetic",
            "Content-Type": "application/json",
        }
        case("NO-COOKIE", 401, "/whoami", absent=b"alpha")
        case(
            "FORGED-COOKIE",
            401,
            "/whoami",
            headers={"Cookie": "lab_session=client-chosen"},
            absent=b"alpha",
        )
        case("NO-CSRF", 403, "/session", "POST", b'{"principal":"alpha-owner"}')
        case(
            "CLIENT-ROLE",
            400,
            "/session",
            "POST",
            b'{"principal":"alpha-owner","role":"admin"}',
            mutation,
        )
        case(
            "DUPLICATE-KEY",
            400,
            "/session",
            "POST",
            b'{"principal":"alpha-owner","principal":"beta-owner"}',
            mutation,
        )
        case(
            "UNKNOWN-IDENTITY",
            400,
            "/session",
            "POST",
            b'{"principal":"claimed-admin"}',
            mutation,
        )
        first, _ = case(
            "ISSUE",
            200,
            "/session",
            "POST",
            b'{"principal":"alpha-owner"}',
            mutation,
            contains=b'"synthetic":true',
        )
        cookie = first.get("set-cookie", "").split(";", 1)[0]
        attributes = {
            item.strip().lower() for item in first.get("set-cookie", "").split(";")[1:]
        }
        cases[-1]["content_ok"] = (
            cases[-1]["content_ok"]
            and cookie.startswith("lab_session=")
            and {"secure", "httponly", "samesite=strict", "path=/", "max-age=120"}
            <= attributes
        )
        peer, _ = case(
            "PEER-ISSUE",
            200,
            "/session",
            "POST",
            b'{"principal":"beta-owner"}',
            mutation,
        )
        peer_cookie = peer.get("set-cookie", "").split(";", 1)[0]
        cases[-1]["content_ok"] = cases[-1]["content_ok"] and cookie != peer_cookie
        case(
            "SCOPE",
            200,
            "/whoami",
            headers={"Cookie": cookie},
            contains=b'"tenant":"alpha"',
            absent=b"beta",
        )
        case(
            "PEER-SCOPE",
            200,
            "/whoami",
            headers={"Cookie": peer_cookie},
            contains=b'"tenant":"beta"',
            absent=b"alpha",
        )
        case("REVOKE", 204, "/logout", "POST", b"{}", {**mutation, "Cookie": cookie})
        case(
            "REVOKED-COOKIE",
            401,
            "/whoami",
            headers={"Cookie": cookie},
            absent=b"alpha",
        )
        case(
            "PEER-STILL-LIVE",
            200,
            "/whoami",
            headers={"Cookie": peer_cookie},
            contains=b"beta",
        )
        case("MALFORMED", 400, "/session", "POST", b"{", mutation)
        case("BODY-LIMIT", 413, "/session", "POST", b"x" * 2049, mutation)
    elif component == "node":
        case("HTML", 200, "/", contains=b"Jason Stys", absent=b"<img")
        case("INERT-FIXTURE", 200, "/sample", contains=b"<img src=x")
        case("TRAVERSAL", 404, "/../sql/schema.sql", absent=b"CREATE TABLE")
        case("PRIVATE-PATH", 404, "/.env")
        case("QUERY-VARIANT", 404, "/sample?label=arbitrary")
        case("NO-MUTATION", 405, "/sample", "POST", b"{}")
    else:
        raise LabError("component")
    return cases
