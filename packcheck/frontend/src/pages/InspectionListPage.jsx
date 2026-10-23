import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { inspectionsAPI, reportsAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import {
  History,
  Search,
  Filter,
  PlusCircle,
  Download,
  ArrowRight,
  RefreshCw,
  FileCheck2,
  Calendar,
} from 'lucide-react';

export const InspectionListPage = () => {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchInspections = async () => {
    try {
      setRefreshing(true);
      const params = {};
      if (search.trim()) params.search = search.trim();
      if (statusFilter) params.status = statusFilter;
      const res = await inspectionsAPI.list(params);
      setInspections(res.data);
    } catch (err) {
      console.error('Failed to load inspections:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchInspections();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchInspections();
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Inspection History Repository
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Complete database of statutory packaged commodity screening records.
          </p>
        </div>

        <Link
          to="/inspections/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-md shadow-blue-500/20 transition self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Inspection</span>
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID, Product, Brand, Inspector..."
            className="w-full pl-10 pr-3.5 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </form>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Status filter buttons */}
          <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl text-xs">
            <button
              onClick={() => setStatusFilter('')}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                statusFilter === '' ? 'bg-white text-blue-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All ({inspections.length})
            </button>
            <button
              onClick={() => setStatusFilter('COMPLIANT')}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                statusFilter === 'COMPLIANT' ? 'bg-white text-emerald-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Compliant
            </button>
            <button
              onClick={() => setStatusFilter('POTENTIAL_NON_COMPLIANCE')}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                statusFilter === 'POTENTIAL_NON_COMPLIANCE' ? 'bg-white text-rose-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Non-Compliant
            </button>
            <button
              onClick={() => setStatusFilter('MANUAL_REVIEW_REQUIRED')}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                statusFilter === 'MANUAL_REVIEW_REQUIRED' ? 'bg-white text-amber-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Review
            </button>
          </div>

          <button
            onClick={fetchInspections}
            disabled={refreshing}
            className="p-2 border border-slate-300 hover:bg-slate-50 rounded-xl text-slate-600 transition"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Inspections Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs">Loading inspection records...</div>
        ) : inspections.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileCheck2 className="w-10 h-10 text-slate-300 mx-auto" />
            <div className="text-sm font-semibold text-slate-700">No inspections match current criteria</div>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try adjusting your search terms or status filter, or start a new inspection.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 font-semibold">Inspection ID</th>
                  <th className="py-3 px-4 font-semibold">Commodity & Brand</th>
                  <th className="py-3 px-4 font-semibold">Category</th>
                  <th className="py-3 px-4 font-semibold">Date & Location</th>
                  <th className="py-3 px-4 font-semibold">Inspector</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">Score</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-blue-600">
                      <Link to={`/inspections/${insp.id}`} className="hover:underline">
                        {insp.inspection_number}
                      </Link>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{insp.product.name}</div>
                      <div className="text-[11px] text-slate-500">{insp.product.brand || 'Unbranded'}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-medium">
                      {insp.product.category}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-slate-800 font-mono text-[11px]">
                        {new Date(insp.inspection_date).toLocaleDateString()}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate max-w-xs">{insp.location}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">
                      {insp.inspector_name}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={insp.overall_status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold">
                      <span className={insp.compliance_score >= 80 ? 'text-emerald-600' : 'text-amber-600'}>
                        {insp.compliance_score}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <a
                          href={`/api/reports/inspection/${insp.id}/pdf`}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
                          title="Download PDF Certificate"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <Link
                          to={`/inspections/${insp.id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg font-semibold transition"
                        >
                          <span>Review</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
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

export default InspectionListPage;
