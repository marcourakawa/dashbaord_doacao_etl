def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")