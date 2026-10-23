import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI, reportsAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import {
  ShieldCheck,
  AlertTriangle,
  XCircle,
  FileCheck2,
  TrendingUp,
  BarChart3,
  PieChart as PieIcon,
  PlusCircle,
  ArrowRight,
  Download,
  Clock,
  Search,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  AreaChart,
  Area,
} from 'recharts';

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboard = async () => {
    try {
      setRefreshing(true);
      const res = await dashboardAPI.get();
      setData(res.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load live dashboard statistics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-500 text-sm font-medium">Loading live enforcement analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 space-y-3">
        <div className="flex items-center gap-2 font-bold text-base">
          <XCircle className="w-5 h-5 text-rose-600" />
          <span>Analytics Query Error</span>
        </div>
        <p className="text-sm">{error}</p>
        <button
          onClick={fetchDashboard}
          className="px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  const { stats, status_distribution, violations_by_category, trend_data, common_violations, recent_inspections } = data;

  const STATUS_COLORS = {
    COMPLIANT: '#10b981',
    POTENTIAL_NON_COMPLIANCE: '#ef4444',
    MANUAL_REVIEW_REQUIRED: '#f59e0b',
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Enforcement Analytics Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Real-time compliance monitoring under Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboard}
            disabled={refreshing}
            className="p-2.5 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl text-slate-600 hover:text-slate-900 transition shadow-sm"
            title="Refresh Live Data"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>

          <Link
            to="/inspections/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-md shadow-blue-500/20 transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Inspection</span>
          </Link>
        </div>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Inspections */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Total Inspections
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-slate-900 font-mono">
              {stats.total_inspections}
            </span>
            <FileCheck2 className="w-5 h-5 text-blue-500 opacity-80" />
          </div>
          <span className="text-[10px] text-slate-400 mt-2">Recorded in DB</span>
        </div>

        {/* Compliant */}
        <div className="bg-white p-5 rounded-2xl border border-emerald-200/80 bg-emerald-50/20 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider">
            Compliant
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-emerald-700 font-mono">
              {stats.compliant_count}
            </span>
            <ShieldCheck className="w-5 h-5 text-emerald-600 opacity-80" />
          </div>
          <span className="text-[10px] text-emerald-600 font-medium mt-2">
            {stats.total_inspections > 0 ? Math.round((stats.compliant_count / stats.total_inspections) * 100) : 0}% compliance rate
          </span>
        </div>

        {/* Non-Compliant */}
        <div className="bg-white p-5 rounded-2xl border border-rose-200/80 bg-rose-50/20 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider">
            Non-Compliant
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-rose-700 font-mono">
              {stats.non_compliant_count}
            </span>
            <XCircle className="w-5 h-5 text-rose-600 opacity-80" />
          </div>
          <span className="text-[10px] text-rose-600 font-medium mt-2">Potential violations</span>
        </div>

        {/* Manual Review */}
        <div className="bg-white p-5 rounded-2xl border border-amber-200/80 bg-amber-50/20 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider">
            Manual Review
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-amber-700 font-mono">
              {stats.manual_review_count}
            </span>
            <AlertTriangle className="w-5 h-5 text-amber-600 opacity-80" />
          </div>
          <span className="text-[10px] text-amber-600 font-medium mt-2">Low OCR / ambiguous</span>
        </div>

        {/* Total Violations */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Flagged Issues
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-slate-900 font-mono">
              {stats.total_violations}
            </span>
            <BarChart3 className="w-5 h-5 text-indigo-500 opacity-80" />
          </div>
          <span className="text-[10px] text-slate-400 mt-2">Rule infringements</span>
        </div>

        {/* Avg Compliance Score */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Avg Score
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-bold text-blue-600 font-mono">
              {stats.average_compliance_score}%
            </span>
            <TrendingUp className="w-5 h-5 text-blue-500 opacity-80" />
          </div>
          <span className="text-[10px] text-slate-400 mt-2">Mean index across inspections</span>
        </div>
      </div>

      {/* Visual Analytics Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Status Distribution Donut Chart */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Compliance Status Distribution</h3>
              <p className="text-xs text-slate-500">Breakdown of inspected packages</p>
            </div>
            <PieIcon className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={status_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {status_distribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={STATUS_COLORS[entry.status] || '#94a3b8'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name, props) => [`${value} package(s)`, props.payload.label]}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Legend
                  formatter={(value, entry) => (
                    <span className="text-xs text-slate-700 font-medium">{entry.payload.label}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Violations by Category Bar Chart */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Violations by Statutory Category</h3>
              <p className="text-xs text-slate-500">Distribution of detected non-compliances</p>
            </div>
            <BarChart3 className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-64">
            {violations_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={violations_by_category} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis
                    dataKey="category"
                    tick={{ fontSize: 11, fill: '#64748b' }}
                    interval={0}
                    angle={-15}
                    textAnchor="end"
                  />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={36} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No active violations recorded in database
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Inspections Trend Area Chart */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-slate-900">Inspection Activity & Trend</h3>
            <p className="text-xs text-slate-500">7-day volume of statutory screenings</p>
          </div>
          <TrendingUp className="w-4 h-4 text-slate-400" />
        </div>

        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trend_data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="total" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#totalGrad)" name="Total Screenings" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Section: Common Violations & Recent Inspections Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Most Common Violations */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-slate-900 mb-1">Common Infringements</h3>
            <p className="text-xs text-slate-500 mb-4">Frequent statutory non-compliances</p>

            <div className="space-y-3">
              {common_violations.length > 0 ? (
                common_violations.map((item, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-800">{item.field_name}</span>
                      <span className="px-2 py-0.5 bg-rose-100 text-rose-800 rounded font-mono font-bold text-[10px]">
                        {item.count} flagged
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-600">{item.violation_type}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{item.legal_reference}</div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 py-6 text-center">
                  No violations logged yet
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 mt-4">
            <Link
              to="/rules"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center justify-between"
            >
              <span>View Legal Metrology Rules</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Recent Inspections Table */}
        <div className="lg:col-span-2 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Recent Enforcement Inspections</h3>
              <p className="text-xs text-slate-500">Latest screened packaged commodities</p>
            </div>
            <Link
              to="/inspections"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-y border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-semibold">Inspection ID</th>
                  <th className="py-2.5 px-3 font-semibold">Product Name</th>
                  <th className="py-2.5 px-3 font-semibold">Date</th>
                  <th className="py-2.5 px-3 font-semibold">Status</th>
                  <th className="py-2.5 px-3 font-semibold">Score</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recent_inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 font-mono font-medium text-blue-600">
                      <Link to={`/inspections/${insp.id}`} className="hover:underline">
                        {insp.inspection_number}
                      </Link>
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-semibold text-slate-900">{insp.product.name}</div>
                      <div className="text-[11px] text-slate-500">{insp.product.brand || 'Unbranded'}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-500 font-mono">
                      {new Date(insp.inspection_date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-3">
                      <StatusBadge status={insp.overall_status} size="sm" />
                    </td>
                    <td className="py-3 px-3 font-mono font-semibold">
                      <span className={insp.compliance_score >= 80 ? 'text-emerald-600' : 'text-amber-600'}>
                        {insp.compliance_score}%
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/inspections/${insp.id}`}
                        className="inline-flex items-center gap-1 text-slate-600 hover:text-blue-600 font-semibold"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
