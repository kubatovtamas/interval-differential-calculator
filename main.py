# TODO make differential class
# TODO implement diff.cald operators
# TODO make IO script


from __future__ import annotations
from typing import TypeVar
import sympy as sp
import unittest
import math


number = TypeVar('number', int, float)


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# Interval arithmetic
class Interval:
    def __init__(self, interval: list):
        self.interval = interval

    @property
    def low(self) -> number:
        return self.interval[0]

    @low.setter
    def low(self, value):
        self.interval[0] = value

    @property
    def high(self) -> number:
        return self.interval[1]

    @high.setter
    def high(self, value):
        self.interval[1] = value

    def __str__(self: Interval) -> str:
        return f"[{self.low}, {self.high}]"

    def __eq__(self: Interval, other: Interval) -> bool:
        """
            :return: true if the two Intervals low and high is close (rel_tol=0.0001)
            :param other: Interval instance
        """
        if isinstance(other, Interval):
            return math.isclose(self.low, other.low, rel_tol=0.0001) \
                   and math.isclose(self.high, other.high, rel_tol=0.0001)
        raise TypeError

    def __add__(self: Interval, other: Interval) -> Interval:
        """
            [a, b] + [c, d] = [a + c, b + d]

            :param other: Interval instance
            :return: new Interval
        """
        if isinstance(other, Interval):
            left = self.low + other.low
            right = self.high + other.high

            print(f"{self} + {other} = [{self.low} + {other.low}, {self.high} + {other.high}] = "
                  f"{Color.RED}[{left}, {right}]{Color.END}\n")
            return Interval([left, right])
        raise TypeError

    def __sub__(self: Interval, other: Interval) -> Interval:
        """
            [a, b] - [c, d] = [a - d, b - c]

            :param other: Interval instance
            :return: new Interval
        """
        if isinstance(other, Interval):
            left = self.low - other.high
            right = self.high - other.low

            print(f"{self} - {other} = [{self.low} - {other.high}, {self.high} - {other.low}] = "
                  f"{Color.RED}[{left}, {right}]{Color.END}\n")
            return Interval([left, right])
        raise TypeError

    def __mul__(self: Interval, other: Interval) -> Interval:
        """
            [a, b] * [c, d] = [min(ac, ad, bc, bd), max(ac, ad, bc, bd)]

            :param other: Interval instance
            :return: new Interval
        """
        if isinstance(other, Interval):
            left = min(self.low * other.low, self.low * other.high, self.high * other.low, self.high * other.high)
            right = max(self.low * other.low, self.low * other.high, self.high * other.low, self.high * other.high)

            print(
                f"[{self.low}, {self.high}] * [{other.low}, {other.high}] ="
                f"[min({self.low} * {other.low}, {self.low} * {other.high}, "
                f"{self.high} * {other.low}, {self.high} * {other.high}),"
                f" max({self.low:.3f} * {other.low}, {self.low} * {other.high}, "
                f"{self.high} * {other.low}, {self.high} * {other.high})"
                f" = {Color.RED} [{left}, {right}] {Color.END}\n")
            return Interval([left, right])
        raise TypeError

    def __truediv__(self: Interval, other: Interval) -> Interval:
        """
            [a, b] / [c, d] = [a, b] * [1/d, 1/c], if 0 not in [c, d]

            :param other: Interval instance
            :return: new Interval
        """
        if isinstance(other, Interval):
            if other.low <= 0 <= other.high:
                raise ZeroDivisionError

            right = Interval([1 / other.high, 1 / other.low])

            print(f"{self} / {other} = {self} * [1 / {other.high}, 1 / {other.low}] = ")
            return self * right
        raise TypeError

    def __pow__(self: Interval, power: int, modulo=None) -> Interval:
        """
            [a, b] ^ power = {
                [0, b^power] : if power is even, and 0 is in interval [a, b]

                [a^power, b^power] : otherwise
            }

            :param power: int number the Interval is raised to
            :return: new Interval
        """
        if self.low <= 0 <= self.high:
            print(f"{self}^{power} = {Color.RED}[0,{(self.high ** power)}]{Color.END}")
            return Interval([0, (self.high ** power)])
        val1 = self.low ** power
        val2 = self.high ** power

        print(f"{self}^{power} = {Color.RED}[{self.low ** power}, {self.high ** power}]{Color.END}")
        return Interval([min(val1, val2), max(val1, val2)])

    def __rxor__(self: Interval, other: number) -> Interval:
        """
            x^[a, b] = [x^a, x^b]

            :param other: number to be raised to interval Power
            :return: new Interval
        """
        left = other ** self.low
        right = other ** self.high

        print(f"{other}^{self} = {Color.RED}[{other}^{self.low}, {other}^{self.high}]{Color.END}")
        return Interval([left, right])

    def log(self: Interval, base: number = math.e) -> Interval:
        """
            log([a, b]) = [log(a), log(b)]

            :param base: base of log
            :return: new Interval
        """
        if self.low > 0 and self.high > 0 and base > 1:
            print(f"log({self}) = {Color.RED}[log({self.low}), log({self.high})]{Color.END}")
            return Interval([math.log(self.low, base), math.log(self.high, base)])
        raise ValueError

    def sin(self: Interval) -> Interval:
        """
            sin[a, b] = {
                [-1, ...], if 3pi/2 + 2k * pi in [a, b],

                [..., 1] if pi/2 + 2k * pi in [a, b],

                [min(sin(a), sin(b)), max(sin(a), sin(b))] otherwise
            }

            :return: new Interval
        """

        left = min(math.sin(self.low), math.sin(self.high))
        right = max(math.sin(self.low), math.sin(self.high))

        a = self.low
        b = self.high

        # shift a between [0, 2pi]
        while (2 * math.pi) <= a:
            a = a - (2 * math.pi)
            b = b - (2 * math.pi)

        while a < 0:
            a = a + (2 * math.pi)
            b = b + (2 * math.pi)

        # shorten [a, b] to 2*pi length
        if (b - a) >= 2 * math.pi:
            b = a + (2 * math.pi)

        # critical points: 3pi / 2, 7pi / 2, 11pi / 2 -> -1
        if (a <= ((3 * math.pi) / 2) <= b) or (a <= (7 * math.pi) / 2 <= b) or (a <= (11 * math.pi) / 2 <= b):
            left = -1

        # critical points: pi / 2, 5pi / 2, 9pi / 2 -> 1
        if (a <= (math.pi / 2) <= b) or (a <= (5 * math.pi / 2) <= b) or (a <= (9 * math.pi / 2) <= b):
            right = 1

        # Numeric errors close to 0 and 1
        if math.isclose(left, 0, abs_tol=0.0001):
            left = 0
        if math.isclose(right, 0, abs_tol=0.0001):
            right = 0

        print(f"sin({self}) = [min(sin(a), sin(b)), max(sin(a), sin(b))]\n"
              f"[-1, ...] ha 3pi/2 + 2k * pi eleme [a, b]-nek,\n"
              f"[..., 1]  ha pi/2 + 2k * pi eleme [a, b]-nek\n"
              f" => {Color.RED}[{left}, {right}]{Color.END}")
        return Interval([left, right])

    def cos(self: Interval) -> Interval:
        """
            cos[a, b] = {
                [-1, ...], if -pi + 2k * pi in [a, b],

                [..., 1] if 0 + 2k * pi in [a, b],

                [min(cos(a), cos(b)), max(cos(a), cos(b))] otherwise
            }

            :return: new Interval
        """
        left = min(math.cos(self.low), math.cos(self.high))
        right = max(math.cos(self.low), math.cos(self.high))

        a = self.low
        b = self.high

        # shift a between [-pi, pi]
        while math.pi <= a:
            a = a - (2 * math.pi)
            b = b - (2 * math.pi)

        while a < (-1 * math.pi):
            a = a + (2 * math.pi)
            b = b + (2 * math.pi)

        # shorten [a, b] to 2*pi length
        if (b - a) >= 2 * math.pi:
            b = a + (2 * math.pi)

        # critical points: -pi, pi, 3pi
        if (a <= (-1 * math.pi) <= b) or (a <= math.pi <= b) or (a <= 3 * math.pi <= b):
            left = -1

        # critical points: 0, 2pi, 4pi
        if (a <= 0 <= b) or (a <= (2 * math.pi) <= b) or (a <= (4 * math.pi) <= b):
            right = 1

        # Numeric errors close to 0 and 1
        if math.isclose(left, 0, abs_tol=0.0001):
            left = 0
        if math.isclose(right, 0, abs_tol=0.0001):
            right = 0

        print(f"cos({self}) = [min(cos(a), cos(b)), max(cos(a), cos(b))]\n"
              f"[-1, ...] ha -pi + 2k * pi eleme [a, b]-nek,\n"
              f"[..., 1]  ha 0 + 2k * pi eleme [a, b]-nek\n"
              f" => {Color.RED}[{left}, {right}]{Color.END}")
        return Interval([left, right])


# Differential arithmetic
# Power rule:

# Chain rule: (f(g(x)))' = f'(g(x)) * g'(x)


class Differential:
    def __init__(self, interval: list):
        self.interval = interval

    @property
    def val(self) -> number:
        return self.interval[0]

    @val.setter
    def val(self, value):
        self.interval[0] = value

    @property
    def diff(self) -> number:
        return self.interval[1]

    @diff.setter
    def diff(self, value):
        self.interval[1] = value

    def __str__(self: Differential) -> str:
        return f"[{self.val}, {self.diff}]"

    def __eq__(self: Differential, other: Differential) -> bool:
        """
            :return: true if the two Differentials val and diff is close (rel_tol=0.0001)
            :param other: Differential instance
        """
        if isinstance(other, Differential):
            return math.isclose(self.val, other.val, rel_tol=0.0001) \
                   and math.isclose(self.diff, other.diff, rel_tol=0.0001)
        raise TypeError

    def __add__(self: Differential, other: Differential) -> Differential:
        """
            (F + G)' = F' + G'

            :param other: Differential instance
            :return: new Differential
        """
        if isinstance(other, Differential):
            left = self.val + other.val
            right = self.diff + other.diff

            print(f"{self} + {other} = {Color.RED}{[left, right]}{Color.END}")
            return Differential([left, right])
        raise TypeError

    def __sub__(self: Differential, other: Differential) -> Differential:
        """
            (F - G)' = F' - G'

            :param other: Differential instance
            :return: new Differential
        """
        if isinstance(other, Differential):
            left = self.val - other.val
            right = self.diff - other.diff

            print(f"{self} - {other} = {Color.RED}{[left, right]}{Color.END}")
            return Differential([left, right])
        raise TypeError

    def __mul__(self: Differential, other: Differential) -> Differential:
        """
            (F * G)' = (F * G') + (F' * G)

            :param other: Differential instance
            :return: new Differential
        """
        if isinstance(other, Differential):
            left = self.val * other.val
            right = self.val * other.diff + self.diff * other.val

            print(f"{self} * {other} = {Color.RED}{[left, right]}{Color.END}")
            return Differential([left, right])
        raise TypeError

    def __truediv__(self: Differential, other: Differential) -> Differential:
        """
            (F / G)' = ((F' * G) - (F * G')) / G^2

            :param other: Differential instance
            :return: new Differential
        """
        if isinstance(other, Differential):
            left = self.val / other.val
            right = (self.diff * other.val - self.val * other.diff) / other.val ** 2

            print(f"{self} / {other} = {Color.RED}{[left, right]}{Color.END}")
            return Differential([left, right])
        raise TypeError

    def __pow__(self: Differential, power: number, modulo=None) -> Differential:
        """
            (F^k)' = k * F^(k-1)

            :param power: the power to which the Differential interval is raised
            :return: new Differential
        """
        if isinstance(power, (int, float)):
            left = self.val ** power
            right = power * self.val ** (power - 1) * self.diff


            print(f"{self}^{power} = {Color.RED}{[left, right]}{Color.END}")
            return Differential([left, right])
        raise TypeError

    def log(self: Differential, base: number = math.e) -> Differential:
        """
            log_e([a,b]) = [log_e(a), b / a] if base == e
            log_a([a,b]) = [log_a(a), b / (a * ln a)] otherwise

            :param base: the logarithm's base
            :return: new Differential
        """
        if isinstance(base, (int, float)):
            if self.val > 0 and self.diff > 0 and base > 1:
                left = math.log(self.val, base)

                if base == math.e:
                    right = self.diff / self.val
                else:
                    right = self.diff / (self.val * math.log(base))

                print(f"log({self}) = {Color.RED}[{left}, {right}]{Color.END}")
                return Differential([left, right])
            raise ValueError
        raise TypeError

    def sin(self: Differential) -> Differential:
        """
            sin([a,b]) = [sin(a), cos(a) * b]

            :return: new Differential
        """
        left = math.sin(self.val)
        right = math.cos(self.val) * self.diff

        print(f"sin({self}) = {Color.RED}[{left}, {right}]{Color.END}")
        return Differential([left, right])

    def cos(self: Differential) -> Differential:
        """
            cos([a,b]) = [cos(a), -1 * sin(a) * b]

            :return: new Differential
        """
        left = math.cos(self.val)
        right = -1 * math.sin(self.val) * self.diff

        print(f"cos({self}) = {Color.RED}[{left}, {right}]{Color.END}")
        return Differential([left, right])

def add_diff(F: list, G: list, do_print: bool = True) -> list:
    """
        :param F: interval_1 as list of len 2
        :param G: interval_2 as list of len 2
        :param do_print: print to stdout if true
        :return: differential interval sum of F and G as list of len 2
    """
    left = F[0] + G[0]
    right = F[1] + G[1]
    if do_print:
        print(f"{F} + {G} = {Color.RED}{[left, right]}{Color.END}")
    return [left, right]


def sub_diff(F: list, G: list, do_print: bool = True) -> list:
    """
        :param F: interval_1 as list of len 2
        :param G: interval_2 as list of len 2
        :param do_print: print to stdout if true
        :return: differential interval difference of F and G as list of len 2
    """
    left = F[0] - G[0]
    right = F[1] - G[1]
    if do_print:
        print(f"{F} - {G} = {Color.RED}{[left, right]}{Color.END}")
    return [left, right]


def mul_diff(F: list, G: list, do_print: bool = True) -> list:
    """
        :param F: interval_1 as list of len 2
        :param G: interval_2 as list of len 2
        :param do_print: print to stdout if true
        :return: differential interval product of F and G as list of len 2
    """
    left = F[0] * G[0]
    right = F[0] * G[1] + F[1] * G[0]
    if do_print:
        print(f"[{F[0]:.3f},{F[1]:.3f}] * [{G[0]:.3f},{G[1]:.3f}] = {Color.RED}{[left, right]}{Color.END}")
    return [left, right]


def div_diff(F: list, G: list, do_print: bool = True) -> list:
    """
        :param F: interval_1 as list of len 2
        :param G: interval_2 as list of len 2
        :param do_print: print to stdout if true
        :return: differential interval quotient of F and G as list of len 2
    """
    left = F[0] / G[0]
    right = (F[1] * G[0] - F[0] * G[1]) / G[0] ** 2
    if do_print:
        print(f"{F} / {G} = {Color.RED}[{left:.3f}, {right:.3f}]{Color.END}")
    return [left, right]


def pow_diff(F: list, k: int, do_print: bool = True) -> list:
    """
        :param F: the base interval as list of len 2
        :param k: the power to which F is raised
        :param do_print: print to stdout if true
        :return: differential interval F raised to power k as list of len 2
    """
    left = F[0] ** k
    right = k * F[0] ** (k - 1) * F[1]
    if do_print:
        print(f"{F}^{k} = {Color.RED}{[left, right]}{Color.END}")
    return [left, right]


def log_diff(F: list, do_print: bool = True) -> list:
    """
        log([a,b]) = [log(a), b / a]

        :param F: interval as list of len 2
        :param do_print: print to stdout if true
        :return: [log(a), log(a)'] as list of len 2
    """

    left = math.log(F[0], math.e)
    right = F[1] / F[0]

    if do_print:
        print(f"log({F}) = {Color.RED}[{left:.3f}, {right:.3f}]{Color.END}")
    return [left, right]


def sin_diff(F: list, do_print: bool = True) -> list:
    """
        sin([a,b]) = [sin(a), cos(a) * b]

        :param F: interval as list of len 2
        :param do_print: print to stdout if true
        :return: [sin(a), sin(a)'] as list of len 2
    """

    left = math.sin(F[0])
    right = math.cos(F[0]) * F[1]

    if do_print:
        print(f"sin({F}) = {Color.RED}[{left:.3f}, {right:.3f}]{Color.END}")
    return [left, right]


def cos_diff(F: list, do_print: bool = True) -> list:
    """
        cos([a,b]) = [cos(a), -1 * sin(a) * b]

        :param F: interval as list of len 2
        :param do_print: print to stdout if true
        :return: [cos(a), cos(a)'] as list of len 2
    """

    left = math.cos(F[0])
    right = -1 * math.sin(F[0]) * F[1]

    if do_print:
        print(f"cos({F}) = {Color.RED}[{left:.3f}, {right:.3f}]{Color.END}")
    return [left, right]


# x  -> (x,1)
# c  -> (c,0)
def auto_diff(expr: str, evalAt: number, *consts: number) -> None:
    """
        Evaluate auto_diff first, and use differential arithmetic functions for intermediate results

        Multiple variable differential:

        (x,y)' by x -> (x, 1), y -> (y, 0)

        (x,y)' by y -> (y, 1), x -> (x, 0)

        :param expr: The expression to be evaluated                             eg. "x^2 + 3"
        :param evalAt: The value of x for the expression to be evaluated at     eg. 4
        :param consts: The constants                                            eg. 3
    """
    print(f"\n---------- f(x) = {expr}, az x = {evalAt} helyen: ----------\n")

    variable_pair_form = f"({evalAt}, 1)"
    expr_str = str(expr)
    for i in range(len(consts)):
        constant_pair_form = f"({consts[i]},0)"
        expr_str = expr_str.replace(str(consts[i]), constant_pair_form)
    print(f"f(x) = {expr_str}")
    print(f"f({evalAt}) = {expr_str.replace('x', variable_pair_form)}")

    print("\n>> Use mul_diff(F, G) / add_diff(F, G) / sub_diff(F, G) / "
          "div_diff(F, G) / pow_diff(F, k) for intermediate results <<\n")

    x = sp.Symbol('x')
    f = sp.lambdify(x, expr)
    f_prime = sp.diff(expr, x)
    f_prime = sp.lambdify(x, f_prime)

    print(f"= {Color.RED}[{float(f(evalAt)):.3f}, {float(f_prime(evalAt)):.3f}]{Color.END}")


# Examples for interval arithmetic:
# add_interval([0, 1], [2, 3])
# sub_interval([2, 3], [0, 1])
# mul_interval([-2, 3], [-1, 4])
# div_interval([8, 12], [6, 5])
# pow_interval([-1, 5], 2)

# Examples for differential arithmetic:
# mul_diff([3, 1], [3, 1])
# add_diff([16, 8], [3, 0])
# sub_diff([16, 8], [-3, 0])
# div_diff([6, 1], [3, 0])
# pow_diff([4, 1], 2)

# Examples for auto_diff:
# (x^2+3)^2, x = 2, constants = 3
# auto_diff("(x^2+3)^2", 2, 3)
# tmp = pow_diff([2, 1], 2)
# tmp2 = add_diff(tmp, [3, 0])
# res = pow_diff(tmp2, 2)

# (x+4) / 3, x = 2, constants = 4, 3
# auto_diff("(x+4)/3", 2, 4, 3)
# tmp = add_diff([2, 1], [4, 0])
# tmp2 = div_diff(tmp, [3, 0])

# (1/x), x = 1, constants = 1
# auto_diff("1/x", 1, 1)
# tmp = div_diff([1, 0], [1, 1])


class IntervalClassTestCase(unittest.TestCase):
    def test_interval_init(self):
        t1 = Interval([1, 5])
        self.assertIsInstance(t1, Interval)
        self.assertEqual(t1.low, t1.interval[0])
        self.assertEqual(t1.high, t1.interval[1])
        self.assertEqual(t1.low, 1)
        self.assertEqual(t1.high, 5)

    def test_interval_str(self):
        t1 = Interval([1, 5])
        t3 = Interval([1.0001, 5])
        self.assertEqual(str(t1), "[1, 5]")
        self.assertEqual(str(t3), "[1.0001, 5]")

    def test_interval_eq(self):
        t1 = Interval([1, 5])
        t2 = Interval([1, 5])
        t3 = Interval([1.0001, 5])
        t4 = Interval([1.0002, 5])
        self.assertTrue(t1 == t2)
        self.assertTrue(t1 == t3)
        self.assertFalse(t1 == t4)

    def test_interval_add(self):
        t1 = Interval([0, 1])
        t2 = Interval([2, 3])
        t3 = Interval([1, 2])
        t4 = Interval([-3, 4])

        self.assertTrue((t1 + t2) == Interval([2, 4]))
        self.assertTrue((t3 + t4) == Interval([-2, 6]))

        self.assertTrue((t3 + t4) == (t4 + t3))
        self.assertTrue((t3 + t4) == (t4 + t3))

        t5 = (t3 + t4)
        self.assertTrue(t5 == (t4 + t3))
        self.assertTrue(t5 + t1 == (t4 + t3) + t1)

        self.assertTrue(t1 + t2 + t3 == Interval([3, 6]))

    def test_interval_sub(self):
        t1 = Interval([0, 1])
        t2 = Interval([2, 3])
        t3 = Interval([1, 2])
        t4 = Interval([-3, 4])

        self.assertTrue(t1 - t2 == Interval([-3, -1]))
        self.assertTrue(t2 - t1 == Interval([1, 3]))
        self.assertTrue(t3 - t4 == Interval([-3, 5]))

    def test_interval_mul(self):
        t1 = Interval([0, 1])
        t2 = Interval([2, 3])
        t3 = Interval([1, 2])
        t4 = Interval([-3, 4])

        self.assertTrue(t1 * t2 == Interval([0, 3]))
        self.assertTrue(t3 * t4 == Interval([-6, 8]))

    def test_interval_div(self):
        t1 = Interval([1, 2])
        t2 = Interval([-3, 4])

        with self.assertRaises(ZeroDivisionError):
            t3 = t1 / t2
        self.assertTrue(t1 / t1 == Interval([0.5, 2]))

    def test_interval_pow(self):
        t1 = Interval([-1, 2])
        t2 = Interval([1, 2])
        t3 = Interval([-2, -1])
        t4 = Interval([-3, -2])

        self.assertTrue(t1 ** 3 == Interval([0, 8]))
        self.assertTrue(t1 ** 2 == Interval([0, 4]))

        self.assertTrue(t2 ** 2 == Interval([1, 4]))
        self.assertTrue(t2 ** 0 == Interval([1, 1]))
        self.assertTrue(t2 ** 1 == t2)
        self.assertTrue(t2 ** 3 == Interval([1, 8]))

        self.assertTrue(t2 ** -1 == Interval([0.5, 1]))
        self.assertTrue(t2 ** -2 == Interval([0.25, 1]))
        self.assertTrue(t2 ** -3 == Interval([1/8, 1]))

        self.assertTrue(t3 ** -1 == Interval([-1, -1/2]))
        self.assertTrue(t3 ** -3 == Interval([-1, -1/8]))
        self.assertTrue(t3 ** -4 == Interval([1/16, 1]))

        self.assertTrue(t4 ** -3 == Interval([-1/8, -1/27]))
        self.assertTrue(t4 ** 0 == Interval([1, 1]))

    def test_interval_exp(self):
        t1 = Interval([1, 2])
        t2 = Interval([-2, 2])
        t3 = Interval([-6, 8])
        t4 = Interval([0, 2])

        self.assertTrue(math.e ^ t1 == Interval([math.e, math.e ** 2]))
        self.assertTrue(2 ^ t2 == Interval([2 ** -2, 2 ** 2]))
        self.assertTrue(math.pi ^ t3 == Interval([math.pi ** -6, math.pi ** 8]))
        self.assertTrue(2 ^ t4 == Interval([1, 4]))

    def test_interval_log(self):
        t1 = Interval([-1, 2])
        t2 = Interval([0, 2])
        t3 = Interval([2, 5])
        t4 = Interval([1, 3])

        with self.assertRaises(ValueError):
            Interval.log(t1)
            Interval.log(t2)
            Interval.log(t3, 0)
            Interval.log(t3, 0.5)

        self.assertEqual(Interval.log(t3), Interval([math.log(2), math.log(5)]))
        self.assertEqual(Interval.log(t4), Interval([math.log(1), math.log(3)]))

    def test_interval_sin(self):
        t1 = Interval([0, math.pi])
        t2 = Interval([-4 * math.pi, 5 * math.pi / 2])
        t3 = Interval([math.pi, 4 * math.pi])
        t4 = Interval([0, 4])
        t5 = Interval([0, 2 * math.pi])
        t6 = Interval([-1 * math.pi / 2, 0])
        t7 = Interval([-1 * math.pi / 2, 1])

        self.assertTrue(Interval.sin(t1) == Interval([0, 1]))
        self.assertTrue(Interval.sin(t2) == Interval([-1, 1]))
        self.assertTrue(Interval.sin(t3) == Interval([-1, 1]))
        self.assertTrue(Interval.sin(t4) == Interval([-0.7568, 1]))
        self.assertTrue(Interval.sin(t5) == Interval([-1, 1]))
        self.assertTrue(Interval.sin(t6) == Interval([-1, 0]))
        self.assertTrue(Interval.sin(t7) == Interval([-1, math.sin(1)]))

    def test_cos_interval(self):
        t1 = Interval([0, 4])
        t2 = Interval([math.pi, 4 * math.pi])
        t3 = Interval([0, 13])
        t4 = Interval([0, 7])
        t5 = Interval([-math.pi / 2, 0])
        t6 = Interval([-math.pi, -math.pi / 2])

        self.assertTrue(Interval.cos(t1) == Interval([-1, 1]))
        self.assertTrue(Interval.cos(t2) == Interval([-1, 1]))
        self.assertTrue(Interval.cos(t3) == Interval([-1, 1]))
        self.assertTrue(Interval.cos(t4) == Interval([-1, 1]))
        self.assertTrue(Interval.cos(t5) == Interval([0, 1]))
        self.assertTrue(Interval.cos(t6) == Interval([-1, 0]))


class DifferentialTestCase(unittest.TestCase):
    def test_differential_init(self):
        d1 = Differential([1, 5])

        self.assertIsInstance(d1, Differential)
        self.assertEqual(d1.val, d1.interval[0])
        self.assertEqual(d1.diff, d1.interval[1])
        self.assertEqual(d1.val, 1)
        self.assertEqual(d1.diff, 5)

    def test_differential_add(self):
        d1 = Differential([2,1])
        d2 = Differential([13,1])
        c1 = Differential([3,0])
        c2 = Differential([1,0])

        self.assertTrue(d1 + c1 == Differential([5, 1]))
        self.assertTrue(c1 + d1 == Differential([5, 1]))
        self.assertTrue(c2 + d2 == Differential([14, 1]))

    def test_differential_sub(self):
        d1 = Differential([2, 1])
        d2 = Differential([13, 1])
        d3 = Differential([-5, 1])
        c1 = Differential([3, 0])
        c2 = Differential([1, 0])
        c3 = Differential([-5, 0])

        self.assertTrue(d1 - c1 == Differential([-1, 1]))
        self.assertTrue(c1 - d1 == Differential([1, -1]))
        self.assertTrue(d2 - c2 == Differential([12, 1]))
        self.assertTrue(d3 - c3 == Differential([0, 1]))

    def test_differential_mul(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])
        c1 = Differential([3, 0])
        c2 = Differential([12, 0])
        c3 = Differential([8, 0])

        self.assertTrue(d1 * c1 == Differential([6, 3]))
        self.assertTrue(c1 * d1 == Differential([6, 3]))
        self.assertTrue(c2 * d2 == Differential([120, 12]))
        self.assertTrue(c3 * d3 == Differential([-40, 8]))

    def test_differential_truediv(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])
        c1 = Differential([3, 0])
        c2 = Differential([12, 0])
        c3 = Differential([8, 0])

        self.assertTrue(d1 / c1 == Differential([2/3, 1/3]))
        self.assertTrue(c1 / d1 == Differential([3/2, -3/4]))
        self.assertTrue(d2 / c2 == Differential([5/6, 1/12]))
        self.assertTrue(d3 / c3 == Differential([-5/8, 1/8]))

    def test_differential_pow(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])

        self.assertTrue(d1 ** 0 == Differential([1, 0]))
        self.assertTrue(d1 ** 1 == Differential([2, 1]))
        self.assertTrue(d1 ** -1 == Differential([1/2, -1/4]))

        self.assertTrue(d2 ** 3 == Differential([1000, 300]))

        self.assertTrue(d3 ** 3 == Differential([-125, 75]))
        self.assertTrue(d3 ** -3 == Differential([-1/125, -3/625]))

    def test_differential_log(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])

        self.assertTrue(d1.log() == Differential([math.log(2), 1/2]))
        self.assertTrue(d2.log() == Differential([math.log(10), 1/10]))
        self.assertEqual(d2.log(2).interval[0], math.log(10) / math.log(2))
        self.assertEqual(d2.log(2).interval[1], 1 / math.log(1024))

        with self.assertRaises(ValueError):
            d3.log()

    def test_differential_sin(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])

        self.assertTrue(d1.sin() == Differential([math.sin(2), math.cos(2)]))
        self.assertTrue(d2.sin() == Differential([math.sin(10), math.cos(10)]))
        self.assertTrue(d3.sin() == Differential([- math.sin(5), math.cos(5)]))

    def test_differential_cos(self):
        d1 = Differential([2, 1])
        d2 = Differential([10, 1])
        d3 = Differential([-5, 1])

        self.assertTrue(d1.cos() == Differential([math.cos(2), -math.sin(2)]))
        self.assertTrue(d2.cos() == Differential([math.cos(10), -math.sin(10)]))
        self.assertTrue(d3.cos() == Differential([math.cos(5), math.sin(5)]))


def main():
    # print("Team1 [1;4]+[-1;2]/[-5;-1]-[-2;1] = [1;4]+[-1;2]*[-1;-1/5]-[-2;1] = "
    #       "[1;4]+[-2;1] -[-2;1] = [-1;5] -[-2;1] = [-2;7]")
    #
    # i1 = Interval([1, 4])
    # i2 = Interval([-1, 2])
    # i3 = Interval([-5, -1])
    # i4 = Interval([-2, 1])
    #
    # i1 + i2 / i3 - i4


    d1 = Differential([2, 1])
    c1 = Differential([3, 0])
    d1 + c1

    # Gyak 3:
    # I. Intervallum aritmetika

    # sub_interval(add_interval([1, 4], div_interval([-1, 2], [-5, -1])), [-2, 1])

    # Team2 X=[-1;2] intervallumon a x^2+3x függvényt, minél szűkebb megoldást
    # add_interval(pow_interval([-1, 2], 2), [-3, 6])  # f1(x) = x^2+3x
    # add_interval(mul_interval([-1, 2], [-1, 2]), [-3, 6])  # f2(x) = x * x + 3x
    # mul_interval([-1, 2], add_interval([-1, 2], [3*-1, 3*2]))  # f3(x) = x*(x+3x)
    # f4(x) = (x+3/2)^2-9/4

    # II. Automatikus differenciálás
    # Team 3. a log(x)(x^2+2x+4) -t az x = 3 helyen
    # auto_diff("log(x) * (x^2 + 2*x + 4)", 3, 4)
    # mul_diff(log_diff([3, 1]), add_diff(add_diff(pow_diff([3, 1], 2), [2*3, 2*1]), [4, 0]))

    # Team 4. a (x^3 - x^2 + 5)(x + 4) -t az x = 2 helyen
    # auto_diff("(x^3 - x^2 + 5) * (x + 4)", 2, 5, 4)
    # mul_diff(add_diff(sub_diff(pow_diff([2, 1], 3), pow_diff([2, 1], 2)), [5, 0]), add_diff([2, 1], [4, 0]))

    # Extra: sin(x^2)(y^3+2), x = 1, y = 2
    # diff x
    # auto_diff("sin(x^2) * (2^3 + 2)", 1, 2)
    # mul_diff(sin_diff(pow_diff([1, 1], 2)), add_diff(pow_diff([2, 0], 3), [2, 0]))

    # diff y
    # auto_diff("sin(1^2) * (x^3 + 2)", 2, 1, 2)
    # mul_diff(sin_diff(pow_diff([1, 0], 2)), add_diff(pow_diff([2, 1], 3), [2, 0]))

    # 3. Mi lesz az f(x,y) = x^3+y^2/x+x*cos(y)+4 kétváltozós függvény
    # automatikus deriváltja x = 2 és y = 3 helyen?
    # auto_diff("x^3 + 3^2 / x + x * cos(3) + 4", 2, 3, 4)  # x szerinti
    # add_diff(add_diff(add_diff(pow_diff([2, 1], 3), div_diff(pow_diff([3, 0], 2), [2, 1])), mul_diff([2, 1], cos_diff([3, 0]))), [4, 0])
    #
    # auto_diff("2^3 + x^2 / 2 + 2 * cos(x) + 4", 3, 3, 4)  # y szerinti
    # add_diff(add_diff(add_diff(pow_diff([2, 0], 3), div_diff(pow_diff([3, 1], 2), [2, 0])), mul_diff([2, 0], cos_diff([3, 1]))), [4, 0])

    # 4. Értékeld ki a fenti f(x,y) függvényt az x=[-1;1] és y=[0,4] intervallumon!
    # (((x ^ 3) + ((y ^ 2) / x)) + (x * (cos(y)))) + 4

    # pass
    # print(Interval([4, 3]) + Interval([-2, 5]))
    # print(Interval([1.0001, 5]))


if __name__ == '__main__':
    # unittest.main()
    main()