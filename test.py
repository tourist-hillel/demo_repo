def calc(x: int, y: int) -> int:
    return x.__mul__(y) # x*y -> x.__mul__(y)


print(calc(3.0, 5))


a = '2'

if hasattr(a, '__mul__') and isinstance(a, int):
    print(a*a)
else:
    print(f'"{a}" is a string and we cant do multiply')
