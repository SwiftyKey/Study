using Grpc.Net.Client;
using StringComparisonService;

//указываем адрес сервера
const string serverAddress = "http://localhost:50051";

//настраиваем канал взаимодействия с сервером
var channel = GrpcChannel.ForAddress(serverAddress, new GrpcChannelOptions
{
	// Для HTTP/2 без TLS требуется указать непосредственно протокол
	HttpHandler = new System.Net.Http.SocketsHttpHandler
	{
		EnableMultipleHttp2Connections = true
	}
});

//создаем клиента
var client = new StringComparisonService.StringComparer.StringComparerClient(channel);

//получаем от пользователя строки
Console.WriteLine("Введите первую строку:");
string a = Console.ReadLine();
Console.WriteLine("Введите вторую строку:");
string c = Console.ReadLine();

Console.WriteLine($"Строка A (n={a.Length}): {a}");
Console.WriteLine($"Строка C (k={c.Length}): {c}");

//формируем запрос
var request = new CompareRequest { A = a, C = c };
//получаем ответ от сервера через асинхронный вызов
var response = await client.CompareStringsAsync(request);

Console.WriteLine($"\nРезультат сравнения: {(response.Equal ? "СОВПАДАЮТ" : "НЕ СОВПАДАЮТ")}");
Console.WriteLine($"Пояснение: {(a.Length != c.Length ? $"длины различаются ({a.Length} != {c.Length})" : "строки идентичны")}");
