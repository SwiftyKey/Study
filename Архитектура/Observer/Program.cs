namespace Observer;

public class Video
{
	public string Name { get; set; }
	public string Description { get; set; }
}

public interface IUser
{
	void Notify(Video video);
}

public class AllWatcher: IUser
{
	public void Notify(Video video)
	{
		Console.WriteLine($"Пошел смотреть {video.Name}");
	}
}

public class ConcreteVideoWathcer : IUser
{
	public void Notify(Video video)
	{
		if (video.Description.Contains("машин"))
			Console.WriteLine($"Пошел смотреть {video.Name}");
	}
}

public class NoneWathcer : IUser
{
	public void Notify(Video video)
	{
		Console.WriteLine("Не смотрю видео...");
	}
}

public interface IPublisher
{
	void Subscribe(IUser user);
	void Unsubscribe(IUser user);
	void NotifyAll(Video video);
}

public class Contentmaker: IPublisher
{
	List<IUser> _users = [];

	public void Subscribe(IUser user) => _users.Add(user);

	public void Unsubscribe(IUser user) => _users.Remove(user);

	public void NotifyAll(Video video)
	{
		foreach (var user in _users)
			user.Notify(video);
	}
}

public class MainClass
{
	public static void Main(string[] args)
	{
		var cm = new Contentmaker();
		var user1 = new NoneWathcer();
		cm.Subscribe(user1);
		cm.Subscribe(new AllWatcher());
		cm.Subscribe(new ConcreteVideoWathcer());

		cm.NotifyAll(new Video { Description = "Вышли новые машины", Name = "Видео №1" });
		cm.Unsubscribe(user1);
		cm.NotifyAll(new Video { Description = "Вышли про авто", Name = "Видео №2" });
	}
}