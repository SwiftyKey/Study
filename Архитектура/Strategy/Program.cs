interface IMovable
{
	int Distance { get; set; }
	int Capacity { get; set; }
	void Move(int dx);
	void DisplayInfo();
}

class PetrolMove(int dist, int capacity) : IMovable
{
	public int Distance { get; set; } = dist;
	public int Capacity { get; set; } = capacity;

	public void Move(int dx)
	{
		Distance += dx;
		Capacity -= dx / 10;
		Console.WriteLine($"Перемещение на бензине на {dx} км.");
	}

	public void DisplayInfo()
	{
		Console.WriteLine($"Всего пройдено: {Distance} км. Оставшееся количество бензина: {Capacity} л.");
	}
}

class ElectricMove(int dist, int capacity) : IMovable
{
	public int Distance { get; set; } = dist;
	public int Capacity { get; set; } = capacity;

	public void Move(int dx)
	{
		Distance += dx;
		Capacity -= dx / 5;
		Console.WriteLine($"Перемещение на электричестве на {dx} км.");
	}

	public void DisplayInfo()
	{
		Console.WriteLine($"Всего пройдено: {Distance} км. Оставшаяся емкость АКБ: {Capacity} кВт/ч.");
	}
}

class Car(int num, string model, IMovable mov)
{
	protected int passengers = num;
	protected string model = model;

	public IMovable Movable { private get; set; } = mov;

	public void Move(int dx) =>	Movable.Move(dx);

	public void DisplayInfo() => Movable.DisplayInfo();
}

class Program
{
	static void Main(string[] args)
	{
		Car auto = new(4, "Volvo", new PetrolMove(0, 50));
		auto.Move(10);
		auto.DisplayInfo();
		auto.Movable = new ElectricMove(0, 90);
		auto.Move(10);
		auto.DisplayInfo();

		Console.ReadLine();
	}
}