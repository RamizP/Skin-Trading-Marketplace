from auth.models import User


class TransferService:
    def transfer(self, from_user: User, to_user: User, amount: float):
        from_user.balance += amount
        to_user.balance -= amount
