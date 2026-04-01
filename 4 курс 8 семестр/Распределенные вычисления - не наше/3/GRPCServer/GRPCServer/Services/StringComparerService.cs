using Grpc.Core;
using StringComparisonService;

namespace GRPCServer.Services;

public class StringComparerService : StringComparisonService.StringComparer.StringComparerBase
{
	private readonly ILogger<StringComparerService> _logger;

	public StringComparerService(ILogger<StringComparerService> logger)
	{
		_logger = logger;
	}

	public override Task<CompareResponse> CompareStrings(
		CompareRequest request,
		ServerCallContext context)
	{
		//создаем уникальный идентификатор запроса
		var correlationId = Guid.NewGuid().ToString()[..8];

		//логируем запрос от клиента
		_logger.LogInformation("[{CorrelationId}] Получен запрос на сравнение строк", correlationId);
		_logger.LogDebug("[{CorrelationId}] Строка A (длина {ALength}): {A}", correlationId, request.A?.Length ?? 0, request.A ?? "null");
		_logger.LogDebug("[{CorrelationId}] Строка C (длина {CLength}): {C}", correlationId, request.C?.Length ?? 0, request.C ?? "null");

		if (string.IsNullOrEmpty(request.A) || string.IsNullOrEmpty(request.C))
		{
			_logger.LogWarning("[{CorrelationId}] Одна из строк пустая или отсутствует", correlationId);
		}

		//сравниваем строки на совпадение
		bool equal = request.A.Length == request.C.Length && request.A == request.C;
		var result = equal ? "СОВПАДАЮТ" : "НЕ СОВПАДАЮТ";

		//логируем результат запроса
		_logger.LogInformation(
			"[{CorrelationId}] Результат: {Result} | Длина A: {ALength}, Длина C: {CLength}",
			correlationId,
			result,
			request.A.Length,
			request.C.Length);

		//отправляем ответ
		return Task.FromResult(new CompareResponse { Equal = equal });
	}
}