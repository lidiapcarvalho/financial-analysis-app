from src.financial_indicators import (
    calculate_operating_margin,
    calculate_net_profit_margin,
    calculate_revenue_growth,
    calculate_financial_indicators
)

# Operating Margin tests


def test_calculate_operating_margin():

    result = calculate_operating_margin(1000, 200)
    assert result == 20.0


def test_calculate_operating_margin_with_negative_operating_income():

    result = calculate_operating_margin(1000, -200)
    assert result == -20.0


def test_calculate_operating_margin_with_zero_operating_income():

    result = calculate_operating_margin(1000, 0)
    assert result == 0.0


def test_calculate_operating_margin_with_zero_revenue():

    result = calculate_operating_margin(0, 200)

    assert result is None

# Net Profit Margin tests


def test_calculate_net_profit_margin():

    result = calculate_net_profit_margin(1000, 150)
    assert result == 15.0


def test_calculate_net_profit_margin_with_negative_income():

    result = calculate_net_profit_margin(1000, -150)
    assert result == -15.0


def test_calculate_net_profit_margin_with_zero_income():

    result = calculate_net_profit_margin(1000, 0)
    assert result == 0.0


def test_calculate_net_profit_margin_with_zero_revenue():

    result = calculate_net_profit_margin(0, 150)
    assert result is None

# Revenue Growth tests


def test_calculate_revenue_growth():

    result = calculate_revenue_growth(1200, 1000)
    assert result == 20.0


def test_calculate_revenue_growth_with_decrease():

    result = calculate_revenue_growth(800, 1000)
    assert result == -20.00


def test_calculate_revenue_growth_with_no_change():

    result = calculate_revenue_growth(1000, 1000)
    assert result == 0.0


def test_calculate_revenue_growth_with_zero_current_revenue():

    result = calculate_revenue_growth(0, 1000)
    assert result == -100.00


def test_calculate_revenue_growth_with_zero_previous_revenue():

    result = calculate_revenue_growth(1200, 0)
    assert result is None


def test_calculate_revenue_growth_without_previous_revenue():

    result = calculate_revenue_growth(1200, None)
    assert result is None


def test_calculate_revenue_growth_without_current_revenue():

    result = calculate_revenue_growth(None, 1000)
    assert result is None

# Financial Indicators tests


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


def test_calculate_financial_indicators_without_previous_revenue():

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
