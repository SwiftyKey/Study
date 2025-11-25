abstract class Pizza(string n)
{
	public string Name { get; protected set; } = n;

	public abstract int GetCost();

	public virtual void Display()
	{
		Console.WriteLine("Название: {0}", Name);
		Console.WriteLine("Цена: {0}", GetCost());
	}
}

class ItalianPizza : Pizza
{
	public ItalianPizza() : base("Итальянская пицца")
	{ }

	public override int GetCost() => 10;
}

class BulgerianPizza : Pizza
{
	public BulgerianPizza() : base("Болгарская пицца")
	{ }

	public override int GetCost() => 8;
}

abstract class Topping(string n, Pizza pizza) : Pizza(n)
{
	protected Pizza pizza = pizza;
	protected List<string> Toppings { get; set; } = [];

	public override void Display()
	{
		Console.WriteLine("Название: {0}", GetBaseName(pizza));
		Console.WriteLine("Цена: {0}", GetCost());

		var allToppings = GetAllToppings();
		if (allToppings.Count != 0)
		{
			Console.WriteLine("Добавки: " + string.Join(", ", allToppings));
		}
	}

	private string GetBaseName(Pizza p)
	{
		return (p is Topping topping) ? GetBaseName(topping.pizza) : p.Name;
	}

	private List<string> GetAllToppings()
	{
		var list = new List<string>();
		if (pizza is Topping topping)
			list.AddRange(topping.GetAllToppings());
		list.AddRange(Toppings);
		return list;
	}
}

class TomatoTopping : Topping
{
	public TomatoTopping(Pizza p) : base(p.Name + ", с томатами", p)
	{
		Toppings.Add("Томаты");
	}

	public override int GetCost() => pizza.GetCost() + 3;
}

class CheeseTopping : Topping
{
	public CheeseTopping(Pizza p) : base(p.Name + ", с сыром", p)
	{
		Toppings.Add("Сыр");
	}

	public override int GetCost() => pizza.GetCost() + 5;
}

class Program
{
	static void Main(string[] args)
	{
		Pizza italianPizzaWithTomato = new ItalianPizza();
		italianPizzaWithTomato = new TomatoTopping(italianPizzaWithTomato);
		italianPizzaWithTomato.Display();
		Console.WriteLine("------------------");

		Pizza italianPizzaWithCheese = new ItalianPizza();
		italianPizzaWithCheese = new CheeseTopping(italianPizzaWithCheese);
		italianPizzaWithCheese.Display();
		Console.WriteLine("------------------");

		Pizza bulgerianPizzaWithTomatoAndCheese = new BulgerianPizza();
		bulgerianPizzaWithTomatoAndCheese = new TomatoTopping(bulgerianPizzaWithTomatoAndCheese);
		bulgerianPizzaWithTomatoAndCheese = new CheeseTopping(bulgerianPizzaWithTomatoAndCheese);
		bulgerianPizzaWithTomatoAndCheese.Display();

		Console.ReadLine();
	}
}