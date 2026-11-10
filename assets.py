import pandas as pd
from dagster import asset, Output, MetadataValue

@asset
def raw_sales():
    """Сырые данные о продажах (имитация)."""
    data = {
        "order_id": [1, 2, 3, 4, 5],
        "product": ["A", "B", "A", "C", "B"],
        "quantity": [10, 5, 8, 3, 7],
        "price": [100, 200, 100, 300, 200]
    }
    df = pd.DataFrame(data)
    return Output(
        df,
        metadata={
            "num_rows": len(df),
            "preview": MetadataValue.md(df.to_markdown())
        }
    )

@asset
def clean_sales(raw_sales: pd.DataFrame):
    """Очищенные данные: убираем строки с quantity = 0 и считаем выручку."""
    df = raw_sales.copy()
    df = df[df["quantity"] > 0]
    df["revenue"] = df["quantity"] * df["price"]
    return Output(
        df,
        metadata={
            "num_rows": len(df),
            "total_revenue": float(df["revenue"].sum())
        }
    )

@asset
def analytics_summary(clean_sales: pd.DataFrame):
    """Итоговая витрина: выручка по продуктам."""
    summary = clean_sales.groupby("product")["revenue"].sum().reset_index()
    return Output(
        summary,
        metadata={
            "preview": MetadataValue.md(summary.to_markdown())
        }
    )

from dagster import Definitions, fs_io_manager

defs = Definitions(
    assets=[raw_sales, clean_sales, analytics_summary],
    resources={"io_manager": fs_io_manager}
)