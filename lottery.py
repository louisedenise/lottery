import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self):
        #storage
        self.init(
            players=sp.map(l={}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost=sp.tez(1),
            tickets_available=sp.nat(10),
            max_tickets=sp.nat(10),
            operator=sp.test_account("admin").address
        )

    @sp.entry_point
    def buy_ticket(self, number_tickets):
        sp.set_type(number_tickets, sp.TNat)

        # assertions
        sp.verify(self.data.tickets_available > 0, "NO TICKETS AVAILABLE")
        sp.verify(sp.amount >= sp.tez(1), "INVALID AMOUNT")

        # storage changes
        self.data.players[sp.len(self.data.players)] = sp.sender
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - number_tickets)

        # return extra tez
        extra_amount = sp.amount - self.data.ticket_cost
        sp.if extra_amount > sp.tez(0):
            sp.send(sp.sender, extra_amount)

    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)

        # assertion
        sp.verify(self.data.tickets_available == 0, "GAME IS STILL ON")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORIZED")

        # generate a winning index
        winner_index = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]

        #send reward to the winner
        sp.send(winner_address, sp.balance)

        # reset the game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def change_cost(self, new_cost):
        #sp.set_type(new_cost, sp.tez)

        # assertion
        sp.verify(self.data.tickets_available == self.data.max_tickets, "GAME IS STILL ON")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORIZED")

        # change ticket cost
        self.data.ticket_cost = new_cost

    @sp.entry_point
    def max_tickets(self, new_max):
        #sp.set_type(new_cost, sp.tez)

        # assertion
        sp.verify(self.data.tickets_available == self.data.max_tickets, "GAME IS STILL ON")
        sp.verify(new_max >= self.data.tickets_available, "INVALID VALUE")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORIZED")

        # change ticket cost
        self.data.max_tickets = new_max


@sp.add_test(name="main")
def test():
    scenario = sp.test_scenario()

    # Test Accounts
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    john = sp.test_account("john")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")

    # Contract Instance
    lottery = Lottery()
    scenario += lottery

    # end game
    #scenario = lottery.end_game(23).run(now = sp.timestamp(4), sender = admin)
    scenario = lottery.change_cost(sp.tez(2)).run(sender = admin)
    scenario = lottery.max_tickets(sp.nat(10)).run(sender = admin)
    scenario = lottery.buy_ticket(2).run(amount=sp.tez(10), sender=alice)


