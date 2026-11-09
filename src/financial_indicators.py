# Margem Operacional (%)

def calculate_operating_margin(revenue, operating_income):
    """Calcula a margem operacional em percentagem."""
    if revenue == 0:
        return None

    operating_margin = (operating_income / revenue) * 100
    return operating_margin

# Margem de Lucro Líquida (%)


def calculate_net_profit_margin(revenue, net_income):
    """Calcula a margem de lucro líquida em percentagem"""
    if revenue == 0:
        return None

    net_profit_margin = (net_income / revenue) * 100
    return net_profit_margin

# Taxa de Crescimento da Receita (%)


def calculate_revenue_growth(current_revenue, previous_revenue):

    if current_revenue is None or previous_revenue is None:
        return None

    if previous_revenue == 0:
        return None

    revenue_growth = ((current_revenue - previous_revenue) /
                      previous_revenue) * 100
    return revenue_growth

# Rendibilidade do Ativo (ROA)


def calculate_roa(net_income, total_assets):
    """Calcula a rendibilidade do ativo em percentagem"""

    if net_income is None or total_assets is None or total_assets == 0:
        return None

    roa = (net_income / total_assets) * 100

    return roa

# Rendibilidade do Capital Próprio (ROE)


def calculate_roe(net_income, equity):
    """Calcula a rendibilidade do capital prórpio em percentagem"""

    if net_income is None or equity is None or equity == 0:
        return None

    roe = (net_income / equity) * 100

    return roe

# Calcula e reúne os indicadores financeiros


def calculate_financial_indicators(
        revenue,
        operating_income,
        net_income,
        previous_revenue=None,
        total_assets=None,
        equity=None
):

    return {
        "operating_margin": calculate_operating_margin(
            revenue, operating_income
        ),
        "net_profit_margin": calculate_net_profit_margin(
            revenue, net_income
        ),
        "revenue_growth": calculate_revenue_growth(
            revenue, previous_revenue
        ),
        "roa": calculate_roa(
            net_income, total_assets
        ),
        "roe": calculate_roe(
            net_income, equity
        )
    }
