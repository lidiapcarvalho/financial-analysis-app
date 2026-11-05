import pytest

from src.financial_indicators import (
    calculate_operating_margin,
    calculate_net_profit_margin,
    calculate_revenue_growth,
    calculate_financial_indicators
)

# Teste 1: Verifica o cálculo da margem operacional


def test_calculate_operating_margin():

    result = calculate_operating_margin(1000, 200)
    assert result == 20.0

# Teste 2: Verifica o cálculo quando o resultado operacional é negativo


def test_calculate_operating_margin_with_negative_operating_income():

    result = calculate_operating_margin(1000, -200)
    assert result == -20.0

# Teste 3: Verifica o cálculo quando o resultado operacional é zero


def test_calculte_operating_margin_with_zero_operating_income():

    result = calculate_operating_margin(1000, 0)
    assert result == 0.0

# Teste 4: Verifica o comportamento quando a receita é zero


def test_calculate_operating_margin_with_zero_revenue():

    result = calculate_operating_margin(0, 200)

    assert result is None

# Teste 5: Verifica o cálculo correto da margem de lucro líquida


def test_calculate_net_profit_margin():

    result = calculate_net_profit_margin(1000, 150)
    assert result == 15.0

# Teste 6: Verifica o cálculo quando o resultado líquido é negativo


def test_calculate_net_profit_margin_with_negative_income():

    result = calculate_net_profit_margin(1000, -150)
    assert result == -15.0

# Teste 7: Verifica o cálculo quando o resultado líquido é zero


def test_calculate_net_profit_margin_with_zero_income():

    result = calculate_net_profit_margin(1000, 0)
    assert result == 0.0

# Teste 8: Verifica o comportamento quando a receita é zero


def test_calculate_net_profit_margem_with_zero_revenue():

    result = calculate_net_profit_margin(0, 150)
    assert result is None

# Teste 9: Verifica o cálculo do crescimento da receita


def test_calculate_revenue_growth():

    result = calculate_revenue_growth(1200, 1000)
    assert result == 20.0

# Teste 10: Verifica o cálculo quando a receita diminui


def test_calculate_revenue_growth_with_descrease():

    result = calculate_revenue_growth(800, 1000)
    assert result == -20.00

# Teste 11: Verfica o cálculo quando a receita não sofre alterações


def test_calculate_revenue_growth_with_no_change():

    result = calculate_revenue_growth(1000, 1000)
    assert result == 0.0

# Teste 12: Verifica o cálculo quando a receita atual é zero


def test_calculate_revenue_growth_with_zero_current_revenue():

    result = calculate_revenue_growth(0, 1000)
    assert result == -100.00

# Teste 13: Verifica o comportamento quando a receita do ano anterior é zero


def test_calculate_revenue_growth_with_zero_previous_revenue():

    result = calculate_revenue_growth(1200, 0)
    assert result is None

# Teste 14: Verifica o comportamento quando a receita do ano anterior não existe


def test_calculate_revenue_growth_without_previous_revenue():

    result = calculate_revenue_growth(1200, None)
    assert result is None

# Teste 15: Verifica o comportamento quando não existe receita atual


def test_calculate_revenue_growth_without_current_revenue():

    result = calculate_revenue_growth(None, 1000)
    assert result is None

# Teste 16:


def test_calculate_financial_indicators():

    result = calculate_financial_indicators(
        revenue=100000,
        operating_income=20000,
        net_income=15000,
        previous_revenue=80000
    )

    assert result == {
        "operating_margin": 20.0,
        "net_profit_margin": 15.0,
        "revenue_growth": 25.0
    }


# Teste 17:

def test_calculate_financial_indicators_without_previoues_revenue():

    result = calculate_financial_indicators(
        revenue=100000,
        operating_income=20000,
        net_income=15000
    )

    assert result == {
        "operating_margin": 20.0,
        "net_profit_margin": 15.0,
        "revenue_growth": None
    }
