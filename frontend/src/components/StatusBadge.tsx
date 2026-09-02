import React from 'react';

interface StatusBadgeProps {
  status?: string | null;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const label = (status ?? 'Unknown').toString();
  const normalized = label.toUpperCase();
  let badgeClass = 'badge-closed';

  if (normalized === 'HIGH' || normalized === 'DECLINED') {
    badgeClass = 'badge-high';
  } else if (normalized === 'MEDIUM' || normalized === 'PENDING' || normalized === 'ESCALATED') {
    badgeClass = 'badge-medium';
  } else if (normalized === 'LOW' || normalized === 'APPROVED' || normalized === 'CLOSED') {
    badgeClass = 'badge-low';
  }

  return (
    <span className={`badge ${badgeClass}`} title={label} aria-label={`status-${normalized.toLowerCase()}`}>
      {label}
    </span>
  );
};
