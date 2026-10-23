import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  Boxes,
  Sliders,
  FileCheck2,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = () => {
  const { isAdmin } = useAuth();

  const navItems = [
    { to: '/dashboard', label: 'Enforcement Dashboard', icon: LayoutDashboard },
    { to: '/inspections/new', label: 'Start New Inspection', icon: PlusCircle },
    { to: '/inspections', label: 'Inspection History', icon: History },
    { to: '/products', label: 'Product Repository', icon: Boxes },
    { to: '/rules', label: 'Compliance Rules Engine', icon: Sliders },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-1">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-2">
          Enforcement Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Legal Reference & System Info Card */}
      <div className="p-4 border-t border-slate-800">
        <div className="p-3 bg-slate-800/60 border border-slate-700/60 rounded-xl space-y-1.5">
          <div className="flex items-center gap-1.5 text-blue-400 text-xs font-semibold">
            <FileCheck2 className="w-3.5 h-3.5" />
            <span>Statutory Standard</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-tight">
            Legal Metrology (Packaged Commodities) Rules, 2011 & Amendments
          </p>
          <div className="pt-1 flex items-center justify-between text-[10px] text-slate-400">
            <span>Govt. of India</span>
            <span className="font-mono text-emerald-400">OCR v4 Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
