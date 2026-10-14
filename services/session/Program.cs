// Jason Stys: synthetic-only loopback HTTP session fixture. Not a real identity provider or public login.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: Program — line 48
// symbol: port — line 53
// symbol: builder — line 55
// variable: builder — line 55
// variable: options — line 57
// variable: MaxRequestBodySize — line 60
// variable: RequestHeadersTimeout — line 61
// variable: KeepAliveTimeout — line 62
// variable: MaxConcurrentConnections — line 63
// symbol: broker — line 65
// variable: broker — line 65
// symbol: app — line 66
// variable: app — line 66
// symbol: origin — line 67
// variable: origin — line 67
// variable: StatusCode — line 80
// variable: StatusCode — line 89
// variable: StatusCode — line 93
// variable: StatusCode — line 94
// variable: StatusCode — line 95
// variable: component — line 97
// variable: synthetic — line 97
// variable: MaxDepth — line 100
// variable: document — line 100
// variable: value — line 101
// symbol: token — line 105
// variable: token — line 106
// variable: HttpOnly — line 109
// variable: MaxAge — line 109
// variable: Path — line 109
// variable: SameSite — line 109
// variable: Secure — line 109
// variable: expires_in_seconds — line 110
// variable: synthetic — line 110
// variable: identity — line 114
// variable: HttpOnly — line 120
// variable: Path — line 120
// variable: SameSite — line 120
// variable: Secure — line 120
// END CODE MAP
using System.Net;
using System.Text.Json;
using SessionLab;

/// <summary>Serve only synthetic session lifecycle routes on numeric loopback with mutation guards.</summary>
internal static class Program
{
    /// <summary>Bind a validated port, configure finite body/header limits, suppress token/path logging.</summary>
    internal static async Task Main(string[] args)
    {
        if (args.Length != 1 || !int.TryParse(args[0], out int port) || port < 1 || port > 65535)
            throw new ArgumentException("one_loopback_port_required");
        var builder = WebApplication.CreateSlimBuilder([]);
        builder.Logging.ClearProviders();
        builder.WebHost.ConfigureKestrel(options =>
        {
            options.Listen(IPAddress.Loopback, port);
            options.Limits.MaxRequestBodySize = 2048;
            options.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(5);
            options.Limits.KeepAliveTimeout = TimeSpan.FromSeconds(5);
            options.Limits.MaxConcurrentConnections = 16;
        });
        var broker = new Broker(TimeProvider.System, TimeSpan.FromMinutes(2));
        var app = builder.Build();
        string origin = "http://127.0.0.1:" + port;
        app.Use(async (context, next) =>
        {
            context.Response.Headers["X-Lab-Component"] = "session";
            context.Response.Headers["Cache-Control"] = "no-store";
            context.Response.Headers["X-Content-Type-Options"] = "nosniff";
            context.Response.Headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'";
            context.Response.Headers["Referrer-Policy"] = "no-referrer";
            if (context.Request.Host.Value != "127.0.0.1:" + port ||
                context.Request.Headers.Origin.Count > 1 ||
                context.Request.Headers.Origin.Count == 1 && context.Request.Headers.Origin != origin ||
                context.Request.Headers["Sec-Fetch-Site"] == "cross-site")
            {
                context.Response.StatusCode = 403;
                return;
            }
            if (context.Request.Method == "POST" &&
                (context.Request.Headers.Origin != origin ||
                 context.Request.Headers["X-Lab-Exercise"] != "synthetic" ||
                 context.Request.ContentType != "application/json" ||
                 context.Request.Headers.ContainsKey("Transfer-Encoding")))
            {
                context.Response.StatusCode = 403;
                return;
            }
            try { await next(context); }
            catch (JsonException) { context.Response.StatusCode = 400; }
            catch (BadHttpRequestException error) { context.Response.StatusCode = error.StatusCode; }
            catch (InvalidOperationException) { context.Response.StatusCode = 429; }
        });
        app.MapGet("/health", () => Results.Json(new { component = "session", synthetic = true }));
        app.MapPost("/session", async (HttpContext context) =>
        {
            using JsonDocument document = await JsonDocument.ParseAsync(context.Request.Body, new JsonDocumentOptions { MaxDepth = 8 });
            JsonElement value = document.RootElement;
            if (value.ValueKind != JsonValueKind.Object || value.EnumerateObject().Count() != 1 ||
                !value.TryGetProperty("principal", out JsonElement principal) || principal.ValueKind != JsonValueKind.String)
                return Results.BadRequest();
            string token;
            try { token = broker.Issue(principal.GetString()!); }
            catch (ArgumentException) { return Results.BadRequest(); }
            context.Response.Cookies.Append("lab_session", token,
                new CookieOptions { Secure = true, HttpOnly = true, SameSite = SameSiteMode.Strict, Path = "/", MaxAge = TimeSpan.FromMinutes(2) });
            return Results.Json(new { synthetic = true, expires_in_seconds = 120 });
        });
        app.MapGet("/whoami", (HttpContext context) =>
        {
            Principal? identity = broker.Resolve(context.Request.Cookies["lab_session"]);
            return identity is null ? Results.Unauthorized() : Results.Json(new { identity.Tenant, identity.Role });
        });
        app.MapPost("/logout", (HttpContext context) =>
        {
            broker.Revoke(context.Request.Cookies["lab_session"]);
            context.Response.Cookies.Delete("lab_session", new CookieOptions { Secure = true, HttpOnly = true, SameSite = SameSiteMode.Strict, Path = "/" });
            return Results.NoContent();
        });
        Console.WriteLine("Local synthetic session fixture: " + origin);
        await app.RunAsync();
    }
}
