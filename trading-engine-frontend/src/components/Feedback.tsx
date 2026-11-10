import Icon from "./Icon";
import type { IconName } from "./Icon";

export function ErrorNotice({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="error-notice" role="alert">
      <Icon name="info" />
      <span>{message}</span>
      {onRetry && (
        <button className="text-button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
export function EmptyState({
  title,
  text,
  icon = "inventory",
  action,
  onAction,
}: {
  title: string;
  text: string;
  icon?: IconName;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Icon name={icon} size={30} />
      </div>
      <h3>{title}</h3>
      <p>{text}</p>
      {action && (
        <button className="button button-primary" onClick={onAction}>
          {action}
          <Icon name="arrow" size={16} />
        </button>
      )}
    </div>
  );
}
export function SkeletonCards() {
  return (
    <div className="item-grid" aria-label="Loading items" aria-busy="true">
      {Array.from({ length: 6 }, (_, i) => (
        <div className="skeleton-card" key={i}>
          <div />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}
