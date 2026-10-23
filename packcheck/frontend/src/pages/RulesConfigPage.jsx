import React, { useState, useEffect } from 'react';
import { rulesAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  Sliders,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Lock,
  RefreshCw,
  Plus,
  Scale,
} from 'lucide-react';

export const RulesConfigPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState('');
  const { isAdmin } = useAuth();

  const fetchRules = async () => {
    try {
      setRefreshing(true);
      const res = await rulesAPI.list();
      setRules(res.data);
    } catch (err) {
      console.error('Failed to load rules:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleToggleRule = async (rule) => {
    if (!isAdmin) {
      alert('Only Enforcement Administrators can toggle statutory compliance rules.');
      return;
    }
    try {
      await rulesAPI.update(rule.id, { enabled: !rule.enabled });
      setMessage(`Rule ${rule.rule_id} status updated.`);
      setTimeout(() => setMessage(''), 3000);
      await fetchRules();
    } catch (err) {
      alert('Failed to update rule: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSeverityChange = async (rule, newSeverity) => {
    if (!isAdmin) {
      alert('Only Enforcement Administrators can modify rule severity.');
      return;
    }
    try {
      await rulesAPI.update(rule.id, { severity: newSeverity });
      setMessage(`Rule ${rule.rule_id} severity updated to ${newSeverity}.`);
      setTimeout(() => setMessage(''), 3000);
      await fetchRules();
    } catch (err) {
      alert('Failed to update rule severity: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
            <Scale className="w-7 h-7 text-blue-600" />
            <span>Legal Metrology Compliance Rule Engine</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Configurable statutory criteria based on Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        <button
          onClick={fetchRules}
          disabled={refreshing}
          className="p-2.5 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl text-slate-600 hover:text-slate-900 transition self-start sm:self-auto shadow-sm"
          title="Refresh Rules"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {message && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Role notice banner */}
      <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-2xl flex items-center justify-between text-xs text-blue-900">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0" />
          <span>
            {isAdmin ? (
              <strong>Administrator Access: You can enable/disable rules and tune statutory severities.</strong>
            ) : (
              <span>Inspector View: Viewing active statutory rules applied to automated package scans.</span>
            )}
          </span>
        </div>
        {!isAdmin && (
          <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
            <Lock className="w-3 h-3" /> Read Only
          </span>
        )}
      </div>

      {/* Rules Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs">Loading rules...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 font-semibold">Rule ID</th>
                  <th className="py-3 px-4 font-semibold">Target Field</th>
                  <th className="py-3 px-4 font-semibold">Validation Type</th>
                  <th className="py-3 px-4 font-semibold">Statutory Reference & Description</th>
                  <th className="py-3 px-4 font-semibold">Severity</th>
                  <th className="py-3 px-4 font-semibold text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-blue-600 whitespace-nowrap">
                      {rule.rule_id}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900 uppercase">
                      {rule.field.replace('_', ' ')}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-semibold">
                        {rule.rule_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-semibold text-slate-900 text-xs mb-0.5">
                        {rule.legal_reference}
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        {rule.description}
                      </p>
                    </td>
                    <td className="py-3.5 px-4">
                      {isAdmin ? (
                        <select
                          value={rule.severity}
                          onChange={(e) => handleSeverityChange(rule, e.target.value)}
                          className="px-2 py-1 bg-white border border-slate-200 rounded-lg text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                        >
                          <option value="CRITICAL">CRITICAL</option>
                          <option value="HIGH">HIGH</option>
                          <option value="MEDIUM">MEDIUM</option>
                          <option value="LOW">LOW</option>
                          <option value="INFO">INFO</option>
                        </select>
                      ) : (
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase font-mono ${
                            rule.severity === 'CRITICAL'
                              ? 'bg-rose-100 text-rose-800'
                              : rule.severity === 'HIGH'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {rule.severity}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {isAdmin ? (
                        <button
                          onClick={() => handleToggleRule(rule)}
                          className={`px-3 py-1 rounded-full text-xs font-bold transition ${
                            rule.enabled
                              ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
                              : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                          }`}
                        >
                          {rule.enabled ? 'ACTIVE' : 'DISABLED'}
                        </button>
                      ) : (
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            rule.enabled
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-slate-100 text-slate-500 border border-slate-200'
                          }`}
                        >
                          {rule.enabled ? 'Active' : 'Disabled'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RulesConfigPage;
