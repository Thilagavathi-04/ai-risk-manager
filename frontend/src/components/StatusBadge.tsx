import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const normalized = status.toUpperCase();
  let badgeClass = 'badge-closed';

  if (normalized === 'HIGH' || normalized === 'DECLINED') {
    badgeClass = 'badge-high';
  } else if (normalized === 'MEDIUM' || normalized === 'PENDING' || normalized === 'ESCALATED') {
    badgeClass = 'badge-medium';
  } else if (normalized === 'LOW' || normalized === 'APPROVED' || normalized === 'CLOSED') {
    badgeClass = 'badge-low';
  }

  return <span className={`badge ${badgeClass}`}>{status}</span>;
};
