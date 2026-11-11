// Jason Stys: synthetic-only loopback HTTP session fixture. Not a real identity provider or public login.
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// definition: Program — line 50
// symbol: port — line 55
// symbol: builder — line 57
// variable: builder — line 57
// variable: options — line 59
// variable: MaxRequestBodySize — line 62
// variable: RequestHeadersTimeout — line 63
// variable: KeepAliveTimeout — line 64
// variable: MaxConcurrentConnections — line 65
// symbol: broker — line 67
// variable: broker — line 67
// symbol: app — line 68
// variable: app — line 68
// symbol: origin — line 69
// variable: origin — line 69
// variable: StatusCode — line 82
// variable: StatusCode — line 91
// variable: StatusCode — line 95
// variable: StatusCode — line 96
// variable: StatusCode — line 97
// variable: nonce — line 101
// variable: character — line 102
// variable: component — line 105
// variable: synthetic — line 105
// variable: MaxDepth — line 109
// variable: document — line 109
// variable: value — line 110
// symbol: token — line 114
// variable: token — line 115
// variable: HttpOnly — line 118
// variable: MaxAge — line 118
// variable: Path — line 118
// variable: SameSite — line 118
// variable: Secure — line 118
// variable: expires_in_seconds — line 119
// variable: synthetic — line 119
// variable: identity — line 123
// variable: HttpOnly — line 129
// variable: Path — line 129
// variable: SameSite — line 129
// variable: Secure — line 129
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
        app.MapGet("/health", (HttpContext context) =>
        {
            string? nonce = Environment.GetEnvironmentVariable("ASRL_OWNED_NONCE");
            if (nonce is not null && nonce.Length == 64 && nonce.All(character => character is >= 'a' and <= 'f' or >= '0' and <= '9'))
                context.Response.Headers["X-Lab-Owned-Nonce"] = nonce;
            context.Response.Headers["X-Lab-Runtime"] = Environment.Version.ToString();
            return Results.Json(new { component = "session", synthetic = true });
        });
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
