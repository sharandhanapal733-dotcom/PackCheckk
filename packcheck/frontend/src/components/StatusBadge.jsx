import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, AlertCircle } from 'lucide-react';

export const StatusBadge = ({ status, size = 'md' }) => {
  const s = String(status || '').toUpperCase();

  let config = {
    bg: 'bg-slate-100',
    text: 'text-slate-700',
    border: 'border-slate-300',
    label: status || 'Unknown',
    icon: HelpCircle,
  };

  if (s === 'COMPLIANT' || s === 'PASS') {
    config = {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      label: s === 'COMPLIANT' ? 'Compliant' : 'Pass',
      icon: CheckCircle2,
    };
  } else if (s === 'POTENTIAL_NON_COMPLIANCE' || s === 'FAIL') {
    config = {
      bg: 'bg-rose-50',
      text: 'text-rose-700',
      border: 'border-rose-200',
      label: s === 'POTENTIAL_NON_COMPLIANCE' ? 'Potential Non-Compliance' : 'Fail',
      icon: XCircle,
    };
  } else if (s === 'MANUAL_REVIEW_REQUIRED' || s === 'MANUAL_REVIEW' || s === 'REVIEW') {
    config = {
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200',
      label: s === 'MANUAL_REVIEW_REQUIRED' ? 'Manual Review Required' : 'Review Required',
      icon: AlertTriangle,
    };
  } else if (s === 'WARNING') {
    config = {
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      label: 'Warning',
      icon: AlertCircle,
    };
  } else if (s === 'NOT_DETECTED') {
    config = {
      bg: 'bg-slate-100',
      text: 'text-slate-600',
      border: 'border-slate-200',
      label: 'Not Detected',
      icon: HelpCircle,
    };
  } else if (s === 'MANUAL_CORRECTED') {
    config = {
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      border: 'border-blue-200',
      label: 'Corrected by Officer',
      icon: CheckCircle2,
    };
  }

  const Icon = config.icon;
  const sizeClasses =
    size === 'sm'
      ? 'px-2 py-0.5 text-xs gap-1'
      : size === 'lg'
      ? 'px-3.5 py-1.5 text-sm gap-2 font-medium'
      : 'px-2.5 py-1 text-xs gap-1.5 font-medium';

  return (
    <span
      className={`inline-flex items-center rounded-full border ${config.bg} ${config.text} ${config.border} ${sizeClasses}`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </span>
  );
};

export default StatusBadge;
