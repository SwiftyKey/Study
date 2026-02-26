using GRPCServer.Services;
using Microsoft.AspNetCore.Server.Kestrel.Core;

//создаем билдер приложения
var builder = WebApplication.CreateBuilder(args);

//очищаем способы и добавляем логирование в консоль
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

//логируем только предостережния от Microsoft.AspNetCore и дебаг удаленной процедуры
builder.Logging.AddFilter("Microsoft.AspNetCore", LogLevel.Warning);
builder.Logging.AddFilter("GRPCServer.Services.StringComparerService", LogLevel.Debug);

//добавляем опции в сервер приложения
builder.WebHost.ConfigureKestrel(options =>
{
	options.ListenLocalhost(50051, listenOptions =>
	{
		listenOptions.Protocols = HttpProtocols.Http2;
	});
	options.ListenAnyIP(50051, listenOptions => listenOptions.Protocols = HttpProtocols.Http2);
});

builder.Services.AddGrpc();

var app = builder.Build();
app.MapGrpcService<StringComparerService>();
app.Logger.LogInformation("Сервер gRPC запущен на http://localhost:50051");
app.Run();
