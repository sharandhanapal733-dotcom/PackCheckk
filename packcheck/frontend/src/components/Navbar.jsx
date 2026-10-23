import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, PlusCircle, LogOut, User, Building2, Bell } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white">PackCheck</span>
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-400/30">
                  SIH26034
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">Legal Metrology Compliance System</p>
            </div>
          </Link>
        </div>

        {/* Action Controls & User Profile */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <Link
                to="/inspections/new"
                className="hidden sm:inline-flex items-center gap-2 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
              >
                <PlusCircle className="w-4 h-4" />
                <span>New Inspection</span>
              </Link>

              <div className="h-6 w-px bg-slate-800 mx-1 hidden sm:block" />

              {/* User details */}
              <div className="flex items-center gap-3 bg-slate-800/60 py-1 px-2.5 rounded-lg border border-slate-700/50">
                <div className="w-7 h-7 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-300 text-xs font-bold">
                  {user?.full_name?.charAt(0) || 'O'}
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-xs font-medium text-slate-200 line-clamp-1">
                    {user?.full_name || 'Enforcement Officer'}
                  </div>
                  <div className="text-[10px] text-blue-400 flex items-center gap-1 font-mono">
                    <span>{user?.role}</span>
                    {user?.badge_number && <span>• {user.badge_number}</span>}
                  </div>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-lg transition"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
            >
              Officer Portal Login
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
