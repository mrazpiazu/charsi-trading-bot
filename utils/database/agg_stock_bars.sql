with raw_bars as (
    select *
    from fact_stock_bars
    where created_at between :start_time and :end_time
--    where created_at between (:start_time AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York') and (:end_date AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York')
)
insert into agg_stock_bars (
    created_at, symbol, open, close, high, low, volume, number_trades, volume_weighted_average_price, aggregation
)
select
    :end_time as created_at,
    symbol,
    round(percentile_cont(0.5) within group (order by open)::NUMERIC, 4) as open,
    round(percentile_cont(0.5) within group (order by close)::NUMERIC, 4) as close,
    round(percentile_cont(0.5) within group (order by high)::NUMERIC, 4) as high,
    round(percentile_cont(0.5) within group (order by low)::NUMERIC, 4) as low,
    round(percentile_cont(0.5) within group (order by volume)::NUMERIC, 4) as volume,
    round(percentile_cont(0.5) within group (order by number_trades)::NUMERIC, 4) as number_trades,
    round(percentile_cont(0.5) within group (order by volume_weighted_average_price)::NUMERIC, 4) as volume_weighted_average_price,
    :aggregation
from raw_bars
group by symbol;
