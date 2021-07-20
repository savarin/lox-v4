class Expr:
    def eval(self):
        """ """
        pass


class Literal(Expr):
    def __init__(self, value: int) -> None:
        """ """
        self.value = value

    def __repr__(self) -> None:
        """ """
        return f"Literal({str(self.value)})"

    def eval(self) -> int:
        """ """
        return self.value


class Plus(Expr):
    def __init__(self, left: Expr, right: Expr) -> None:
        """ """
        self.left = left
        self.right = right

    def __repr__(self) -> None:
        """ """
        return f"Plus({self.left}, {self.right})"

    def eval(self) -> Expr:
        """ """
        return self.left.eval() + self.right.eval()


class Times(Expr):
    def __init__(self, left: Expr, right: Expr) -> None:
        """ """
        self.left = left
        self.right = right

    def __repr__(self) -> None:
        """ """
        return f"Times({self.left}, {self.right})"

    def eval(self) -> Expr:
        """ """
        return self.left.eval() * self.right.eval()


class GetNumber(Expr):
    def __repr__(self) -> None:
        """ """
        return "GetNumber()"

    def eval(self) -> int:
        """ """
        return int(input("enter a number: "))


class Print(Expr):
    def __init__(self, value: Expr) -> None:
        """ """
        self.value = value

    def __repr__(self) -> None:
        """ """
        return f"Print({self.value})"

    def eval(self) -> None:
        """ """
        print(self.value.eval())


if __name__ == "__main__":
    print(Print(Plus(Times(Literal(13), Literal(2)), Times(GetNumber(), Literal(7)))))
