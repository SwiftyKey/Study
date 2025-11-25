using System;

namespace Singleton;

class Singleton
{
	private Singleton() { }

	private static Singleton _instance;

	public static Singleton GetInstance()
	{
		_instance ??= new Singleton();
		return _instance;
	}
}


public static class ClassMain
{
	public static void Main(string[] args)
	{
		var a = Singleton.GetInstance();
		var b = a;
		Console.WriteLine(b.GetHashCode() == a.GetHashCode());
	}
}
