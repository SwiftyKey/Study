interface ITransport
{
	void Drive(string road);
}

class Auto : ITransport
{
	public void Drive(string road)
	{
		Console.WriteLine($"Машина едет по: {road}");
	}
}

class Driver
{
	public void Travel(ITransport transport, string some)
	{
		transport.Drive(some);
	}
}

interface IAnimal
{
	void Move(int num);
}

class Camel : IAnimal
{
	public void Move(int num)
	{
		Console.WriteLine($"Верблюд идет по пескам пустыни в {num} часов вечера");
	}
}

class CamelToTransportAdapter(Camel c) : ITransport
{
	readonly Camel camel = c;

	public void Drive(string road)
	{
		int hour = 0;
		if (!Int32.TryParse(road, out hour))
		{
			hour = 10;
		}
		camel.Move(hour);
	}
}

class Program
{
	static void Main(string[] args)
	{
		Driver driver = new();
		Auto auto = new();
		driver.Travel(auto, "дорога");

		Camel camel = new();
		ITransport camelTransport = new CamelToTransportAdapter(camel);
		driver.Travel(camelTransport, "9");

		Console.Read();
	}
}