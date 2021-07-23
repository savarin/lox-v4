class Expr:
    def pprint(self, *args) -> str:
        """ """
        return f"{self.__class__.__name__}({', '.join(map(str, args))})"

    def __repr__(self) -> str:
        """ """
        return self.pprint()

    def eval(self):
        """ """
        pass

    def optimize(self):
        """ """
        pass

    def compile(self):
        """ """
        pass

    def typecheck(self):
        """ """
        pass


class Literal(Expr):
    def __init__(self, value: int) -> None:
        """ """
        self.value = value

    def __repr__(self) -> str:
        """ """
        return self.pprint(self.value)

    def eval(self) -> int:
        """ """
        return self.value

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> int:
        """ """
        return self.value

    def typecheck(self) -> None:
        """ """
        pass


class Plus(Expr):
    def __init__(self, left: Expr, right: Expr) -> None:
        """ """
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """ """
        return self.pprint(self.left, self.right)

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

    def typecheck(self) -> None:
        """ """
        if isinstance(self.left, Print) or isinstance(self.right, Print):
            raise TypeError("Cannot operate on None")

        self.left.typecheck()
        self.right.typecheck()


class Times(Expr):
    def __init__(self, left: Expr, right: Expr) -> None:
        """ """
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """ """
        return self.pprint(self.left, self.right)

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

    def typecheck(self) -> None:
        """ """
        if isinstance(self.left, Print) or isinstance(self.right, Print):
            raise TypeError("Cannot operate on None")

        self.left.typecheck()
        self.right.typecheck()


class GetNumber(Expr):
    def eval(self) -> int:
        """ """
        return int(input("enter a number: "))

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> str:
        """ """
        return 'int(input("enter a number: ""))'

    def typecheck(self) -> None:
        """ """
        pass


class Print(Expr):
    def __init__(self, value: Expr) -> None:
        """ """
        self.value = value

    def __repr__(self) -> str:
        """ """
        return self.pprint(self.value)

    def eval(self) -> None:
        """ """
        print(self.value.eval())

    def optimize(self) -> Expr:
        """ """
        return self

    def compile(self) -> str:
        """ """
        return f"print({self.value.compile()})"

    def typecheck(self) -> None:
        """ """
        pass


if __name__ == "__main__":
    print(Plus(Times(Literal(13), Literal(2)), Times(Literal(12), GetNumber())).optimize().compile())
