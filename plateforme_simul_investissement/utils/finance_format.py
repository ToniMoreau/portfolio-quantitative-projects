def euro(x):
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")

def number(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")

def percent(x):
    return f"{x:.2f} %".replace(".", ",")

def age(x):
    return f"{x} an{"s" if x >1 else ""}."