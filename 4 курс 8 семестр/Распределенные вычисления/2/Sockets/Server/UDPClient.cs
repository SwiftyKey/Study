using System;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

class UdpChatPeer
{
	private const int LISTEN_PORT = 5555;          // Порт для приёма сообщений (как сервер)
	private const int TIMEOUT_SECONDS = 60;        // Таймаут неактивности
	private const int TIMEOUT_CHECK_INTERVAL = 5;  // Проверка таймаутов каждые 5 сек

	// Опционально: центральный сервер для подключения (если не указан — чистый P2P)
	private static readonly string? CENTRAL_SERVER_IP = "192.168.11.227"; // "192.168.1.100"
	private static readonly int CENTRAL_SERVER_PORT = 5555;

	private static UdpClient? _serverUdp;          // Для приёма сообщений (серверная роль)
	private static UdpClient? _clientUdp;          // Для отправки сообщений (клиентская роль)
	private static IPEndPoint? _centralServerEp;   // Адрес центрального сервера (если есть)

	// Список подключённых клиентов: адрес -> информация
	private static readonly ConcurrentDictionary<IPEndPoint, ClientInfo> _clients = new();

	private static string _myNickname = "";
	private static readonly CancellationTokenSource _cts = new();

	// Информация о клиенте
	private class ClientInfo
	{
		public string Nickname { get; set; }
		public DateTime LastSeen { get; set; }
	}

	static async Task Main(string[] args)
	{
		Console.OutputEncoding = Encoding.UTF8;
		Console.InputEncoding = Encoding.UTF8;

		try
		{
			// 1. Запуск серверной части (приём сообщений)
			_serverUdp = new UdpClient(LISTEN_PORT);
			_serverUdp.Client.ReceiveTimeout = 1000; // Для корректного завершения
			Console.WriteLine($"📡 Сервер запущен на порту {LISTEN_PORT}");

			// 2. Запуск клиентской части (отправка)
			_clientUdp = new UdpClient(); // Случайный локальный порт для отправки

			// 3. Подключение к центральному серверу (опционально)
			if (!string.IsNullOrEmpty(CENTRAL_SERVER_IP))
			{
				_centralServerEp = new IPEndPoint(IPAddress.Parse(CENTRAL_SERVER_IP), CENTRAL_SERVER_PORT);
				Console.WriteLine($"🔗 Подключение к центральному серверу {CENTRAL_SERVER_IP}:{CENTRAL_SERVER_PORT}");
			}

			// 4. Регистрация в чате
			Console.Write("👤 Введите ник: ");
			_myNickname = Console.ReadLine()?.Trim() ?? "User" + new Random().Next(1000, 9999);

			// Отправка /join на центральный сервер (если есть) ИЛИ локальная регистрация
			if (_centralServerEp != null)
			{
				await SendAsync($"/join {_myNickname}", _centralServerEp);
				Console.WriteLine($"✅ Вы в чате как '{_myNickname}' (подключены к центральному серверу)\n");
			}
			else
			{
				// Локальная регистрация (чистый P2P)
				var localEp = new IPEndPoint(IPAddress.Loopback, LISTEN_PORT);
				RegisterClient(localEp, _myNickname);
				Console.WriteLine($"✅ Вы в чате как '{_myNickname}' (P2P режим)\n");
			}

			// 5. Запуск фоновых задач
			var serverTask = StartServerAsync(_cts.Token);
			var timeoutTask = CheckTimeoutsAsync(_cts.Token);
			var clientTask = StartClientAsync(_cts.Token);

			// 6. Ожидание завершения
			await Task.WhenAny(serverTask, clientTask);
			_cts.Cancel();
			await Task.WhenAll(serverTask, timeoutTask, clientTask);
		}
		catch (Exception ex)
		{
			Console.WriteLine($"❌ Критическая ошибка: {ex.Message}");
		}
		finally
		{
			Cleanup();
		}
	}

	// === СЕРВЕРНАЯ ЧАСТЬ: приём сообщений ===
	private static async Task StartServerAsync(CancellationToken token)
	{
		Console.WriteLine("📨 Сервер ожидает сообщения...\n");

		while (!token.IsCancellationRequested && _serverUdp != null)
		{
			try
			{
				var result = await _serverUdp.ReceiveAsync();
				HandleMessage(result.Buffer, result.RemoteEndPoint);
			}
			catch (SocketException) { /* Таймаут или прерывание */ }
			catch (ObjectDisposedException) { break; }
			catch (Exception ex)
			{
				Console.WriteLine($"⚠️ Ошибка приёма: {ex.Message}");
			}
		}
	}

	// Обработка входящего сообщения
	private static void HandleMessage(byte[] buffer, IPEndPoint sender)
	{
		string message = Encoding.UTF8.GetString(buffer).TrimEnd('\n', '\r');

		// Команда регистрации
		if (message.StartsWith("/join "))
		{
			string nick = message[6..].Trim();
			RegisterClient(sender, nick);
			Console.WriteLine($"✅ {nick} подключился {sender}");
			Broadcast($"🔔 {nick} вошёл в чат", exclude: sender);
			return;
		}

		// Проверка регистрации
		if (!_clients.ContainsKey(sender))
		{
			Send("Сначала: /join твой_ник", sender);
			return;
		}

		// Обновление активности
		if (_clients.TryGetValue(sender, out var client))
		{
			client.LastSeen = DateTime.Now;
			Console.WriteLine($"{client.Nickname}: {message}");
			Broadcast($"{client.Nickname}: {message}", exclude: sender);
		}
	}

	// Регистрация клиента
	private static void RegisterClient(IPEndPoint addr, string nick)
	{
		_clients[addr] = new ClientInfo
		{
			Nickname = nick,
			LastSeen = DateTime.Now
		};
	}

	// === КЛИЕНТСКАЯ ЧАСТЬ: отправка сообщений ===
	private static async Task StartClientAsync(CancellationToken token)
	{
		Console.Write("> ");
		while (!token.IsCancellationRequested && _clientUdp != null)
		{
			try
			{
				// Неблокирующее чтение из консоли
				var messageTask = Task.Run(() => Console.ReadLine(), token);
				var completed = await Task.WhenAny(messageTask, Task.Delay(-1, token));

				if (token.IsCancellationRequested) break;

				string? message = await messageTask;
				if (string.IsNullOrWhiteSpace(message)) continue;

				if (message.Equals("/exit", StringComparison.OrdinalIgnoreCase))
				{
					Console.WriteLine("👋 Отключение...");
					break;
				}

				if (message.Equals("/users", StringComparison.OrdinalIgnoreCase))
				{
					ShowConnectedUsers();
					Console.Write("> ");
					continue;
				}

				// Отправка на центральный сервер или рассылка всем локальным клиентам
				if (_centralServerEp != null)
				{
					await SendAsync(message, _centralServerEp);
				}
				else
				{
					Broadcast(message);
				}

				Console.Write("> ");
			}
			catch (OperationCanceledException) { break; }
			catch (Exception ex)
			{
				Console.WriteLine($"\r⚠️ Ошибка отправки: {ex.Message}\n> ");
			}
		}
	}

	// === РАССЫЛКА СООБЩЕНИЙ ===
	private static void Broadcast(string message, IPEndPoint? exclude = null)
	{
		byte[] data = Encoding.UTF8.GetBytes(message + "\n");

		foreach (var client in _clients)
		{
			if (client.Key.Equals(exclude)) continue;

			try
			{
				_serverUdp?.Send(data, data.Length, client.Key);
			}
			catch { /* Игнорируем ошибки отправки */ }
		}
	}

	private static async Task SendAsync(string message, IPEndPoint target)
	{
		byte[] data = Encoding.UTF8.GetBytes(message + "\n");
		await _clientUdp!.SendAsync(data, data.Length, target);
	}

	private static void Send(string message, IPEndPoint target)
	{
		byte[] data = Encoding.UTF8.GetBytes(message + "\n");
		_serverUdp?.Send(data, data.Length, target);
	}

	// === ПРОВЕРКА ТАЙМАУТОВ ===
	private static async Task CheckTimeoutsAsync(CancellationToken token)
	{
		while (!token.IsCancellationRequested)
		{
			await Task.Delay(TIMEOUT_CHECK_INTERVAL * 1000, token);

			var now = DateTime.Now;
			var toRemove = new List<IPEndPoint>();

			foreach (var client in _clients)
			{
				if ((now - client.Value.LastSeen).TotalSeconds > TIMEOUT_SECONDS)
				{
					toRemove.Add(client.Key);
				}
			}

			foreach (var addr in toRemove)
			{
				if (_clients.TryRemove(addr, out var clientInfo))
				{
					Console.WriteLine($"❌ {clientInfo.Nickname} отключён (таймаут)");
					Broadcast($"❌ {clientInfo.Nickname} вышел");
				}
			}
		}
	}

	// === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
	private static void ShowConnectedUsers()
	{
		Console.WriteLine("\n👥 Подключённые пользователи:");
		if (_clients.Count == 0)
		{
			Console.WriteLine("   Никого нет");
		}
		else
		{
			foreach (var client in _clients)
			{
				TimeSpan idle = DateTime.Now - client.Value.LastSeen;
				Console.WriteLine($"   {client.Value.Nickname} ({client.Key}) — бездействие: {idle.Seconds}с");
			}
		}
		Console.WriteLine();
	}

	private static void Cleanup()
	{
		_cts.Cancel();
		_serverUdp?.Close();
		_serverUdp?.Dispose();
		_clientUdp?.Close();
		_clientUdp?.Dispose();
		Console.WriteLine("\n🔌 Чат остановлен.");
	}
}