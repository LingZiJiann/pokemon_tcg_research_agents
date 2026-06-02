import numpy as np
import pandas as pd
from anthropic import AsyncAnthropic

from config.config import settings


class EdaAgent:
    def __init__(self):
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, ebay_df: pd.DataFrame) -> str:
        stats = self._compute_stats(ebay_df)
        prompt = self._build_prompt(stats, ebay_df)
        message = await self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=512,
            system="You are a data analyst specialising in Pokemon card pricing.",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _compute_stats(self, df: pd.DataFrame) -> dict:
        prices = df["price"].dropna()
        q1, q3 = prices.quantile(0.25), prices.quantile(0.75)
        iqr = q3 - q1
        outliers = prices[(prices < q1 - 1.5 * iqr) | (prices > q3 + 1.5 * iqr)]

        sold_dates = pd.to_datetime(df["sold_date"], errors="coerce").dropna()
        date_range = (
            f"{sold_dates.min().date()} to {sold_dates.max().date()}"
            if not sold_dates.empty
            else "unknown"
        )

        return {
            "count": int(prices.count()),
            "mean": round(float(prices.mean()), 2),
            "median": round(float(prices.median()), 2),
            "std": round(float(prices.std()), 2),
            "min": round(float(prices.min()), 2),
            "max": round(float(prices.max()), 2),
            "outlier_count": int(outliers.count()),
            "outlier_values": [round(float(v), 2) for v in outliers.tolist()],
            "date_range": date_range,
        }

    def _build_prompt(self, stats: dict, df: pd.DataFrame) -> str:
        prices = df["price"].dropna().round(2).tolist()
        return (
            f"Listing count: {stats['count']}\n"
            f"Mean: ${stats['mean']}\n"
            f"Median: ${stats['median']}\n"
            f"Std dev: ${stats['std']}\n"
            f"Min: ${stats['min']}  Max: ${stats['max']}\n"
            f"IQR outliers ({stats['outlier_count']}): {stats['outlier_values']}\n"
            f"Date range: {stats['date_range']}\n\n"
            f"Raw prices: {prices}\n\n"
            "Give a concise plain-language interpretation of the pricing data above, "
            "highlighting any notable trends, outliers, or signals relevant to a buyer."
        )
