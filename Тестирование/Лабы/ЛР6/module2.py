def sum_between_positives_correct(arr: list[float]) -> float:
	sum_nums = 0
	processing = False

	for i in range(len(arr)):
		if arr[i] > 0:
			if not processing:
				processing = True
				continue
			break

		if processing:
			sum_nums += arr[i]

	return sum_nums

def sum_between_positives_incorrect(arr: list[float]) -> float:
	sum_nums = 0
	processing = True

	for i in range(len(arr)):
		if arr[i] > 0:
			if not processing:
				processing = False
				continue
			elif processing:
				break

		if processing:
			sum_nums += arr[i]

	return sum_nums


def dummy(arr: list[float]) -> float:
	print('Выполнился модуль 2')
