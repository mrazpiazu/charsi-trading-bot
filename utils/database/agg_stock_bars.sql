with raw_bars as (
    select *
    from fact_stock_bars
    where created_at between :start_time and :end_time
)
insert into agg_stock_bars (
    created_at, symbol, open, close, high, low, volume, number_trades, volume_weighted_average_price, aggregation
)
select
    :end_time as created_at,
    symbol,
    percentile_cont(0.5) within group (order by open) as open,
    percentile_cont(0.5) within group (order by close) as close,
    percentile_cont(0.5) within group (order by high) as high,
    percentile_cont(0.5) within group (order by low) as low,
    percentile_cont(0.5) within group (order by volume) as volume,
    percentile_cont(0.5) within group (order by number_trades) as number_trades,
    percentile_cont(0.5) within group (order by volume_weighted_average_price) as volume_weighted_average_price,
    :aggregation
from raw_bars
group by symbol;
