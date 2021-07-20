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

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> str:
        """ """
        return self.value

    def typecheck(self) -> str:
        """ """
        pass


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

    def optimize(self) -> Expr:
        """ """
        self.left = self.left.optimize()
        self.right = self.right.optimize()

        if isinstance(self.left, Literal) and isinstance(self.right, Literal):
            return Literal(self.left.value + self.right.value)

        return self

    def compile(self) -> str:
        """ """
        return f"({self.left.compile()} + {self.right.compile()})"

    def typecheck(self) -> str:
        """ """
        if isinstance(self.left, Print) or isinstance(self.right, Print):
            raise TypeError("Cannot add to None")

        self.left.typecheck()
        self.right.typecheck()


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

    def optimize(self) -> Expr:
        """ """
        self.left = self.left.optimize()
        self.right = self.right.optimize()

        if isinstance(self.left, Literal) and isinstance(self.right, Literal):
            return Literal(self.left.value * self.right.value)

        return self

    def compile(self) -> str:
        """ """
        return f"({self.left.compile()} * {self.right.compile()})"

    def typecheck(self) -> str:
        """ """
        if isinstance(self.left, Print) or isinstance(self.right, Print):
            raise TypeError("Cannot multiply to None")

        self.left.typecheck()
        self.right.typecheck()


class GetNumber(Expr):
    def __repr__(self) -> None:
        """ """
        return "GetNumber()"

    def eval(self) -> int:
        """ """
        return int(input("enter a number: "))

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> str:
        """ """
        return "int(input())"

    def typecheck(self) -> str:
        """ """
        pass


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

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> str:
        """ """
        return f"print({self.value.compile()})"

    def typecheck(self) -> str:
        """ """
        pass


if __name__ == "__main__":
    Plus(Times(Literal(13), Literal(2)), Times(Literal(12), GetNumber())).typecheck()
