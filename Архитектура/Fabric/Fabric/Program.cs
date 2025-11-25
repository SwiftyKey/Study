using System;
using System.Collections.Generic;

namespace Fabric;

interface ITransport
{
	void go(string a, string b);
}

interface ICreator
{
	ITransport build();
}

class Car: ITransport
{
	public void go(string a, string b)
	{
		Console.WriteLine($"from {a} to {b} on car");
	}

}

class Ship: ITransport
{
	public void go(string a, string b)
	{
		Console.WriteLine($"from {a} to {b} on ship");
	}
}

class CarCreator: ICreator
{
	public ITransport build()
	{
		return new Car();
	}
}

class ShipCreator: ICreator
{
	public ITransport build()
	{
		return new Ship();
	}
}

public static class MainApp
{
	static void foo(ICreator creator)
	{
		ITransport tran = creator.build();
		tran.go("Kurgan", "Moscow");
	}

	public static void Main(string[] args)
	{
		foo(new CarCreator());
		foo(new ShipCreator());
		Console.Read();
	}
}