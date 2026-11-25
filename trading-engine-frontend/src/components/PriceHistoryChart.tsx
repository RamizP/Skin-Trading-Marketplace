import { useCallback, useId, useState } from "react";
import { getPriceHistory } from "../api/entities";
import type { Entity, PriceHistoryPoint } from "../api/types";
import useQuery from "../hooks/useQuery";
import { formatCurrency, formatDateTime, getErrorMessage } from "../utils/format";

const chart = {
  width: 760,
  height: 220,
  left: 76,
  right: 16,
  top: 14,
  bottom: 174,
};

function dateValue(value: string) {
  const hasTimezone = value.endsWith("Z") || /[+-]\d\d:\d\d$/.test(value);
  return new Date(hasTimezone ? value : `${value}Z`);
}

function shortDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(dateValue(value));
}

function PriceChart({ points, entityName }: { points: PriceHistoryPoint[]; entityName: string }) {
  const [activeIndex, setActiveIndex] = useState(points.length - 1);
  const gradientId = `price-history-fill-${useId().replace(/:/g, "")}`;
  const prices = points.map((point) => Number(point.price));
  const rawMin = Math.min(...prices);
  const rawMax = Math.max(...prices);
  const padding = Math.max((rawMax - rawMin) * 0.16, rawMax * 0.025, 0.01);
  const min = rawMin - padding;
  const max = rawMax + padding;
  const plotWidth = chart.width - chart.left - chart.right;
  const plotHeight = chart.bottom - chart.top;
  const coordinates = points.map((point, index) => ({
    x:
      chart.left +
      (points.length === 1 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth),
    y: chart.bottom - ((Number(point.price) - min) / (max - min)) * plotHeight,
  }));
  const line = coordinates
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  const lastIndex = points.length - 1;
  const firstPoint = points[0]!;
  const lastPoint = points[lastIndex]!;
  const firstCoordinate = coordinates[0]!;
  const lastCoordinate = coordinates[lastIndex]!;
  const area = `${line} L ${lastCoordinate.x} ${chart.bottom} L ${firstCoordinate.x} ${chart.bottom} Z`;
  const activePoint = points[activeIndex] || lastPoint;
  const firstPrice = prices[0];
  const lastPrice = prices[lastIndex]!;
  const change = firstPrice ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0;
  const spanDays = Math.round(
    (dateValue(lastPoint.created_at).getTime() -
      dateValue(firstPoint.created_at).getTime()) /
      86_400_000,
  );
  const ticks = [...new Set([0, Math.round((points.length - 1) / 2), points.length - 1])];

  return (
    <div className="price-chart-content">
      <div className="price-chart-heading">
        <div>
          <span className="eyebrow">LAST SALE</span>
          <strong className="price-chart-current">
            {formatCurrency(activePoint.price)}
          </strong>
          <span className="price-chart-date">
            {formatDateTime(activePoint.created_at)}
          </span>
        </div>
        <div className="price-chart-summary">
          <span>{points.length} {points.length === 1 ? "sale" : "sales"}</span>
          {spanDays > 0 && <span>over {spanDays} days</span>}
          {points.length > 1 && (
            <strong className={change >= 0 ? "trend-up" : "trend-down"}>
              {change > 0 ? "+" : ""}{change.toFixed(1)}%
            </strong>
          )}
        </div>
      </div>

      <div className="price-chart-plot">
        <svg
          viewBox={`0 0 ${chart.width} ${chart.height}`}
          preserveAspectRatio="none"
          role="img"
          aria-label={`Sale price history for ${entityName}, ${points.length} trades`}
        >
          <defs>
            <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="var(--orange)" stopOpacity="0.24" />
              <stop offset="100%" stopColor="var(--orange)" stopOpacity="0" />
            </linearGradient>
          </defs>
          {[0, 0.5, 1].map((ratio) => {
            const y = chart.top + plotHeight * ratio;
            const value = max - (max - min) * ratio;
            return (
              <g key={ratio}>
                <line className="price-chart-grid" x1={chart.left} x2={chart.width - chart.right} y1={y} y2={y} />
                <text className="price-chart-axis" x={chart.left - 10} y={y + 4} textAnchor="end">
                  {formatCurrency(value)}
                </text>
              </g>
            );
          })}
          <path d={area} fill={`url(#${gradientId})`} />
          <path className="price-chart-line" d={line} />
          {coordinates.map((point, index) => {
            const selected = index === activeIndex;
            const label = `${formatCurrency(points[index]!.price)} sold ${formatDateTime(points[index]!.created_at)}`;
            return (
              <circle
                key={`${points[index]!.created_at}-${index}`}
                className={`price-chart-point${selected ? " selected" : ""}`}
                cx={point.x}
                cy={point.y}
                r={selected ? 5 : 3}
                tabIndex={0}
                role="img"
                aria-label={label}
                onMouseEnter={() => setActiveIndex(index)}
                onFocus={() => setActiveIndex(index)}
                onBlur={() => setActiveIndex(points.length - 1)}
              >
                <title>{label}</title>
              </circle>
            );
          })}
          {ticks.map((index) => (
            <text
              className="price-chart-axis price-chart-date-axis"
              key={index}
              x={coordinates[index]!.x}
              y={chart.height - 12}
              textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}
            >
              {shortDate(points[index]!.created_at)}
            </text>
          ))}
        </svg>
      </div>
      <p className="price-chart-footnote">Completed sales - Hover or focus a point to inspect it</p>
    </div>
  );
}

export default function PriceHistoryChart({ entity }: { entity: Entity }) {
  const fetchHistory = useCallback(() => getPriceHistory(entity.id), [entity.id]);
  const query = useQuery(fetchHistory, []);

  return (
    <section className="price-history-panel" aria-label={`Price history for ${entity.name}`}>
      <div className="section-heading compact price-history-title">
        <div>
          <span className="eyebrow">MARKET ACTIVITY</span>
          <h3>Sale price history</h3>
        </div>
        <span className="price-history-symbol">{entity.symbol}</span>
      </div>
      {query.loading ? (
        <div className="price-chart-placeholder" role="status">
          <span className="spinner" />
          Loading sale history...
        </div>
      ) : query.error ? (
        <div className="price-chart-placeholder price-chart-error" role="status">
          <span>{getErrorMessage(query.error)}</span>
          <button className="button button-secondary button-small" onClick={query.reload}>
            Try again
          </button>
        </div>
      ) : query.data.length === 0 ? (
        <div className="price-chart-placeholder">
          No completed sales yet. The chart will appear after this item trades.
        </div>
      ) : (
        <PriceChart points={query.data} entityName={entity.name} />
      )}
    </section>
  );
}
