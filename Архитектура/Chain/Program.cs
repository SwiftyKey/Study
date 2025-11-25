class Receiver(bool bt, bool sbpt, bool b2pt)
{
	public bool BankTransfer { get; set; } = bt;
	public bool SBPTransfer { get; set; } = sbpt;
	public bool Bet2PayTransfer { get; set; } = b2pt;
}

abstract class PaymentHandler
{
	public PaymentHandler Successor { get; set; }
	public abstract void Handle(Receiver receiver);
}

class BankPaymentHandler : PaymentHandler
{
	public override void Handle(Receiver receiver)
	{
		if (receiver.BankTransfer)
			Console.WriteLine("Выполняем банковский перевод");
		else
			Successor?.Handle(receiver);
	}
}

class Best2PayPaymentHandler : PaymentHandler
{
	public override void Handle(Receiver receiver)
	{
		if (receiver.Bet2PayTransfer)
			Console.WriteLine("Выполняем перевод через Best2Pay");
		else
			Successor?.Handle(receiver);
	}
}

class SBPPaymentHandler : PaymentHandler
{
	public override void Handle(Receiver receiver)
	{
		if (receiver.SBPTransfer)
			Console.WriteLine("Выполняем перевод через SBP");
		else
			Successor?.Handle(receiver);
	}
}

class Program
{
	static void Main(string[] args)
	{
		Receiver receiver = new(false, true, true);

		PaymentHandler bankPaymentHandler = new BankPaymentHandler();
		PaymentHandler sbpPaymentHandler = new SBPPaymentHandler();
		PaymentHandler best2payPaymentHandler = new Best2PayPaymentHandler();

		bankPaymentHandler.Successor = best2payPaymentHandler;
		best2payPaymentHandler.Successor = sbpPaymentHandler;

		bankPaymentHandler.Handle(receiver);

		Console.Read();
	}
}