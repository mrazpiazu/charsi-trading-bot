with raw_bars as (
    select
        *
    from fact_stock_bars
    where created_at between :start_time and :end_time
)
insert into agg_stock_bars
    (created_at, symbol, open, close, high, low, volume, number_trades, volume_weighted_average_price, aggregation)
select
    :end_time as created_at,
    symbol,
    median(open) as open,
    median(close) as close,
    median(high) as high,
    median(low) as low,
    median(volume) as volume,
    median(number_trades) as number_trades,
    median(volume_weighted_average_price) as volume_weighted_average_price,
    :aggregation
from raw_bars
group by created_at, symbol;