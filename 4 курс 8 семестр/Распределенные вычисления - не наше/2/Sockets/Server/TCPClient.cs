//using System.Net.Sockets;
//using System.Text;

//class ChatClient
//{
//	private const string SERVER_IP = "192.168.11.227";
//	private const int PORT = 5555;
//	private static TcpClient? _client;
//	private static NetworkStream? _stream;
//	private static readonly CancellationTokenSource _cts = new();

//	static async Task Main(string[] args)
//	{
//		try
//		{
//			_client = new TcpClient();
//			Console.WriteLine($"Подключение к {SERVER_IP}:{PORT}...");
//			await _client.ConnectAsync(SERVER_IP, PORT);
//			_stream = _client.GetStream();

//			Console.WriteLine("Подключено! Введите сообщение для отправки (Ctrl+C для выхода):\n");

//			// Запуск приёма и отправки сообщений параллельно
//			var receiveTask = ReceiveMessagesAsync(_cts.Token);
//			var sendTask = SendMessagesAsync(_cts.Token);

//			// Ожидание завершения любой задачи (например, при разрыве соединения)
//			await Task.WhenAny(receiveTask, sendTask);

//			// Завершение всех операций
//			_cts.Cancel();
//			await Task.WhenAll(receiveTask, sendTask);
//		}
//		catch (SocketException ex)
//		{
//			Console.WriteLine($"Ошибка подключения: {ex.Message}");
//		}
//		catch (OperationCanceledException)
//		{
//			// Нормальное завершение при отмене
//		}
//		catch (Exception ex)
//		{
//			Console.WriteLine($"Критическая ошибка: {ex.Message}");
//		}
//		finally
//		{
//			Cleanup();
//		}
//	}

//	private static async Task ReceiveMessagesAsync(CancellationToken token)
//	{
//		var buffer = new byte[1024];
//		try
//		{
//			while (!token.IsCancellationRequested && _stream != null && _stream.CanRead)
//			{
//				int bytesRead = await _stream.ReadAsync(buffer, 0, buffer.Length, token);
//				if (bytesRead == 0) break; // Соединение закрыто сервером

//				string message = Encoding.UTF8.GetString(buffer, 0, bytesRead).TrimEnd('\n', '\r');
//				Console.WriteLine($"\r[Сервер]: {message}\n> ");
//			}
//		}
//		catch (OperationCanceledException) { }
//		catch (Exception ex)
//		{
//			Console.WriteLine($"\rОшибка приёма: {ex.Message}\n> ");
//		}
//	}

//	private static async Task SendMessagesAsync(CancellationToken token)
//	{
//		try
//		{
//			Console.Write("> ");
//			while (!token.IsCancellationRequested && _stream != null && _stream.CanWrite)
//			{
//				string? message = Console.ReadLine();
//				if (string.IsNullOrWhiteSpace(message)) continue;

//				if (message.Equals("/exit", StringComparison.OrdinalIgnoreCase))
//				{
//					Console.WriteLine("Отключение...");
//					break;
//				}

//				byte[] data = Encoding.UTF8.GetBytes(message + "\n");
//				await _stream.WriteAsync(data, 0, data.Length, token);
//				await _stream.FlushAsync(token);
//				Console.Write("> ");
//			}
//		}
//		catch (OperationCanceledException) { }
//		catch (Exception ex)
//		{
//			Console.WriteLine($"\rОшибка отправки: {ex.Message}\n> ");
//		}
//	}

//	private static void Cleanup()
//	{
//		_cts.Cancel();
//		_stream?.Dispose();
//		_client?.Close();
//		_client?.Dispose();
//		Console.WriteLine("\nСоединение закрыто.");
//	}
//}