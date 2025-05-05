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
    round(percentile_cont(0.5) within group (order by open), 4) as open,
    round(percentile_cont(0.5) within group (order by close), 4) as close,
    round(percentile_cont(0.5) within group (order by high), 4) as high,
    round(percentile_cont(0.5) within group (order by low), 4) as low,
    round(percentile_cont(0.5) within group (order by volume), 4) as volume,
    round(percentile_cont(0.5) within group (order by number_trades), 4) as number_trades,
    round(percentile_cont(0.5) within group (order by volume_weighted_average_price), 4) as volume_weighted_average_price,
    :aggregation
from raw_bars
group by symbol;
