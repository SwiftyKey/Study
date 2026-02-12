using SomeNamespace;

namespace Memento;

class Memento(int velocity, float mileage)
{
	public int Velocity { get; private set; } = velocity;
	public float Mileage { get; private set; } = mileage;
	public DateTime CreatedAt { get; private set; } = DateTime.Now;
}

class Car(int velocity, float mileage)
{
	public int Velocity { get; set; } = velocity;
	public float Mileage { get; set; } = mileage;

	public Memento GetMemento() => new(Velocity, Mileage);

	public void Restore(Memento memento)
	{
		Velocity = memento.Velocity;
		Mileage = memento.Mileage;
	}

	public override string ToString() => $"Скорость = {Velocity}, Пробег = {Mileage}";
}

class Caretaker(Car car)
{
	public Car Car { get; private set; } = car;
	Stack<Memento> Mementos = [];

	public void Backup() => Mementos.Push(Car.GetMemento());

	public void Restore() => Car.Restore(Mementos.Pop());
}

class Program
{
	public static void Main()
	{
		var car = new Car(100, 127.5f);
		var caretaker = new Caretaker(car);
		caretaker.Backup();
		Console.WriteLine(car);

		car.Velocity = 180;
		car.Mileage = 130.2f;
		Console.WriteLine(car);
		
		caretaker.Restore();
		Console.WriteLine(car);
		
		var sc = new SomeClass();
		sc.SomeFunction(5, 6);
	}
}