import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { productsAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import {
  Boxes,
  Search,
  History,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Building,
  Barcode,
  Calendar,
  Layers,
} from 'lucide-react';

export const ProductRepositoryPage = () => {
  const { productId } = useParams();
  const [products, setProducts] = useState([]);
  const [selectedProductHistory, setSelectedProductHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchProducts = async () => {
    try {
      const params = {};
      if (search.trim()) params.search = search.trim();
      const res = await productsAPI.list(params);
      setProducts(res.data);

      // If productId is provided in URL or first item exists, fetch its history
      const targetId = productId || (res.data.length > 0 ? res.data[0].id : null);
      if (targetId) {
        fetchProductHistory(targetId);
      }
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProductHistory = async (id) => {
    try {
      const res = await productsAPI.getHistory(id);
      setSelectedProductHistory(res.data);
    } catch (err) {
      console.error('Failed to load product history:', err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Product Commodity Repository
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Track repeat inspections, historical compliance trajectories, and packaging changes over time.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Product List */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchProducts()}
              placeholder="Search products or brands..."
              className="w-full pl-10 pr-3.5 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {products.map((p) => {
              const isSelected = selectedProductHistory?.product?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => fetchProductHistory(p.id)}
                  className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-50/70 border-blue-400 ring-2 ring-blue-500/20 shadow-sm'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="font-bold text-sm text-slate-900">{p.name}</div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Brand: <strong className="text-slate-700">{p.brand || 'Unbranded'}</strong>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 font-mono">
                    <span>{p.category}</span>
                    {p.identifier && <span>EAN: {p.identifier}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Inspection Timeline & Evolution for Selected Product */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
          {selectedProductHistory ? (
            <div className="space-y-6">
              {/* Product Header Card */}
              <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 bg-blue-100/60 px-2.5 py-0.5 rounded-full">
                    {selectedProductHistory.product.category}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">
                    Total Historical Inspections: <strong>{selectedProductHistory.total_inspections}</strong>
                  </span>
                </div>
                <h2 className="text-xl font-extrabold text-slate-900">
                  {selectedProductHistory.product.name}
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs text-slate-600 pt-1">
                  <div>
                    <span className="block text-slate-400 text-[10px] uppercase font-semibold">Brand</span>
                    <span className="font-semibold text-slate-800">{selectedProductHistory.product.brand || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="block text-slate-400 text-[10px] uppercase font-semibold">Barcode / EAN</span>
                    <span className="font-mono text-slate-800">{selectedProductHistory.product.identifier || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="block text-slate-400 text-[10px] uppercase font-semibold">Manufacturer</span>
                    <span className="text-slate-800 truncate block">{selectedProductHistory.product.manufacturer || 'Detected via OCR'}</span>
                  </div>
                </div>
              </div>

              {/* Timeline of Inspections */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-900 pb-2 border-b border-slate-100">
                  <History className="w-4 h-4 text-blue-600" />
                  <span>Historical Inspections & Compliance Evolution</span>
                </div>

                {selectedProductHistory.inspections.map((insp, idx) => (
                  <div
                    key={insp.id}
                    className="p-5 rounded-2xl border border-slate-200 hover:border-blue-300 transition-all bg-white shadow-sm space-y-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <Link
                          to={`/inspections/${insp.id}`}
                          className="font-mono font-bold text-blue-600 hover:underline text-sm"
                        >
                          {insp.inspection_number}
                        </Link>
                        <StatusBadge status={insp.overall_status} size="sm" />
                      </div>

                      <div className="flex items-center gap-4 text-xs font-mono text-slate-500">
                        <span>{new Date(insp.inspection_date).toLocaleDateString()}</span>
                        <span className="font-bold text-slate-800">Score: {insp.compliance_score}%</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Inspector</span>
                        <span>{insp.inspector_name}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Station / Location</span>
                        <span>{insp.location}</span>
                      </div>
                    </div>

                    {/* Flagged issues in this scan */}
                    {insp.violations && insp.violations.length > 0 && (
                      <div className="p-3 bg-rose-50/50 border border-rose-200 rounded-xl space-y-1.5 text-xs">
                        <span className="font-bold text-rose-800 block text-[11px]">
                          Infringements Flagged in this Batch:
                        </span>
                        <ul className="list-disc pl-4 space-y-1 text-slate-700">
                          {insp.violations.map((v) => (
                            <li key={v.id}>
                              <strong>{v.field_name.toUpperCase()}:</strong> {v.description}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center justify-end pt-1">
                      <Link
                        to={`/inspections/${insp.id}`}
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800"
                      >
                        <span>View Complete Inspection Record</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 text-xs">
              Select a product from the list to inspect historical inspections.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductRepositoryPage;
