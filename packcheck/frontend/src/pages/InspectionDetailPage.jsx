import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { inspectionsAPI, reportsAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import OCRViewer from '../components/OCRViewer';
import ManualCorrectionModal from '../components/ManualCorrectionModal';
import {
  ShieldCheck,
  AlertTriangle,
  XCircle,
  FileText,
  Download,
  Edit3,
  Eye,
  CheckCircle2,
  Calendar,
  MapPin,
  User,
  Tag,
  ArrowLeft,
  RefreshCw,
  Sparkles,
  ExternalLink,
  History,
  Layers,
} from 'lucide-react';

export const InspectionDetailPage = () => {
  const { id } = useParams();
  const [inspection, setInspection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  // Highlighting & OCR sync
  const [highlightedBbox, setHighlightedBbox] = useState(null);

  // Manual correction modal state
  const [correctionModalField, setCorrectionModalField] = useState(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [pdfMessage, setPdfMessage] = useState('');

  const fetchInspection = async () => {
    try {
      const res = await inspectionsAPI.get(id);
      setInspection(res.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load inspection details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspection();
  }, [id]);

  const handleFieldCorrection = async (fieldId, data) => {
    await inspectionsAPI.correctField(id, fieldId, data);
    await fetchInspection(); // Refresh updated compliance score and status
  };

  const handleDownloadPdf = async () => {
    setIsGeneratingPdf(true);
    setPdfMessage('Generating official compliance certificate PDF...');
    try {
      const genRes = await reportsAPI.generate(id);
      // Trigger download
      window.open(`/api/reports/${genRes.data.report_id}/download`, '_blank');
      setPdfMessage('PDF generated and opened successfully!');
      setTimeout(() => setPdfMessage(''), 4000);
      await fetchInspection();
    } catch (err) {
      alert('Failed to generate PDF: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] space-y-4">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-500 text-sm font-medium">Loading inspection analysis...</p>
      </div>
    );
  }

  if (error || !inspection) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 space-y-3">
        <div className="flex items-center gap-2 font-bold text-base">
          <XCircle className="w-5 h-5 text-rose-600" />
          <span>Inspection Not Found</span>
        </div>
        <p className="text-sm">{error || 'Unable to retrieve inspection record.'}</p>
        <Link
          to="/inspections"
          className="inline-flex items-center gap-2 px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Inspection History</span>
        </Link>
      </div>
    );
  }

  const activeImage = inspection.images?.[activeImageIndex] || null;

  // Aggregate OCR results for the active image
  const activeImageOcr = activeImage?.ocr_results || [];

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
            <Link to="/inspections" className="hover:text-blue-600">
              Inspections
            </Link>
            <span>/</span>
            <span className="font-mono text-slate-700">{inspection.inspection_number}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {inspection.product.name}
            </h1>
            <span className="text-xs px-2.5 py-1 bg-slate-100 border border-slate-200 text-slate-700 rounded-full font-mono">
              {inspection.inspection_number}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Brand: <strong className="text-slate-700">{inspection.product.brand || 'Unbranded'}</strong> • Category: <strong className="text-slate-700">{inspection.product.category}</strong>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <Link
            to={`/products/${inspection.product.id}/history`}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 shadow-sm transition"
            title="Compare with past inspections of this product"
          >
            <History className="w-4 h-4 text-blue-600" />
            <span>Product History</span>
          </Link>

          <button
            onClick={handleDownloadPdf}
            disabled={isGeneratingPdf}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-500/20 transition disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>{isGeneratingPdf ? 'Generating...' : 'Download Official PDF Report'}</span>
          </button>
        </div>
      </div>

      {pdfMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{pdfMessage}</span>
        </div>
      )}

      {/* SECTION 16: Executive Compliance Status Callout */}
      <div
        className={`p-6 sm:p-8 rounded-3xl border shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-6 ${
          inspection.overall_status === 'COMPLIANT'
            ? 'bg-emerald-50/50 border-emerald-200 text-emerald-950'
            : inspection.overall_status === 'POTENTIAL_NON_COMPLIANCE'
            ? 'bg-rose-50/50 border-rose-200 text-rose-950'
            : 'bg-amber-50/50 border-amber-200 text-amber-950'
        }`}
      >
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
            {inspection.overall_status === 'COMPLIANT' ? (
              <span className="text-emerald-700 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Preliminary Screening Status
              </span>
            ) : inspection.overall_status === 'POTENTIAL_NON_COMPLIANCE' ? (
              <span className="text-rose-700 flex items-center gap-1.5">
                <XCircle className="w-4 h-4" /> Preliminary Screening Status
              </span>
            ) : (
              <span className="text-amber-700 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Preliminary Screening Status
              </span>
            )}
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {inspection.overall_status === 'COMPLIANT'
              ? '🟢 COMPLIANT WITH LMPC RULES, 2011'
              : inspection.overall_status === 'POTENTIAL_NON_COMPLIANCE'
              ? '🔴 POTENTIAL NON-COMPLIANCE DETECTED'
              : '🟡 MANUAL REVIEW REQUIRED'}
          </h2>

          <p className="text-xs sm:text-sm text-slate-700 max-w-2xl leading-relaxed">
            {inspection.overall_status === 'COMPLIANT'
              ? 'All mandatory package declarations (Rule 6) were successfully detected and verified against Legal Metrology standards.'
              : inspection.overall_status === 'POTENTIAL_NON_COMPLIANCE'
              ? 'One or more mandatory statutory declarations are missing or violate standard unit / tax formatting rules. Physical verification advised.'
              : 'Declarations could not be confirmed with high optical confidence, or character height requires physical optical calibration.'}
          </p>
        </div>

        {/* Transparent Compliance Score Card (Section 12) */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm min-w-[220px] text-center space-y-1 shrink-0">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Compliance Score
          </span>
          <div className="text-3xl sm:text-4xl font-extrabold font-mono text-slate-900">
            {inspection.compliance_score}%
          </div>
          <p className="text-[10px] text-slate-500">
            Formula: {inspection.passed_checks} passed / {inspection.total_checks} applicable checks × 100
          </p>
          <div className="pt-2 flex items-center justify-center gap-3 text-xs border-t border-slate-100 font-medium">
            <span className="text-rose-600">{inspection.violations_count} flagged</span>
            <span className="text-slate-300">•</span>
            <span className="text-amber-600">{inspection.manual_review_count} review</span>
          </div>
        </div>
      </div>

      {/* Inspection Meta Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5 bg-white rounded-2xl border border-slate-200 text-xs">
        <div>
          <span className="text-slate-400 block text-[10px] uppercase font-semibold">Enforcement Officer</span>
          <span className="font-semibold text-slate-800">{inspection.inspector_name}</span>
        </div>
        <div>
          <span className="text-slate-400 block text-[10px] uppercase font-semibold">Inspection Date</span>
          <span className="font-semibold text-slate-800 font-mono">
            {new Date(inspection.inspection_date).toLocaleString()}
          </span>
        </div>
        <div>
          <span className="text-slate-400 block text-[10px] uppercase font-semibold">Location / Station</span>
          <span className="font-semibold text-slate-800">{inspection.location || 'Field Station'}</span>
        </div>
        <div>
          <span className="text-slate-400 block text-[10px] uppercase font-semibold">Batch / Barcode</span>
          <span className="font-semibold text-slate-800 font-mono">
            {inspection.batch_number || inspection.product.identifier || 'Not Stamped'}
          </span>
        </div>
      </div>

      {/* SECTION 14: Interactive OCR Review Screen & Bounding Boxes */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Eye className="w-5 h-5 text-blue-600" />
              <span>OCR Visual Inspection Screen</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Click any bounding box or declaration below to inspect text and confidence evidence.
            </p>
          </div>

          {/* Multiple Package Side Switcher */}
          {inspection.images && inspection.images.length > 1 && (
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl">
              {inspection.images.map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => {
                    setActiveImageIndex(idx);
                    setHighlightedBbox(null);
                  }}
                  className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                    activeImageIndex === idx
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Side {idx + 1}: {img.image_side || 'Panel'}
                </button>
              ))}
            </div>
          )}
        </div>

        {activeImage ? (
          <OCRViewer
            image={activeImage}
            ocrResults={activeImageOcr}
            highlightedBbox={highlightedBbox}
            onSelectBox={(boxItem) => {
              // Find matching field
              const matchedField = inspection.extracted_fields.find(
                (f) =>
                  f.bbox &&
                  f.bbox[0] === boxItem.box[0] &&
                  f.bbox[1] === boxItem.box[1]
              );
              if (matchedField) {
                // Focus card or highlight
              }
            }}
          />
        ) : (
          <div className="p-8 text-center text-slate-400 text-xs">
            No package images registered for this inspection.
          </div>
        )}
      </div>

      {/* SECTION 16: Mandatory Declarations Summary Table */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <span>Mandatory Package Declarations Assessment</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Rule 6 compliance assessment with original OCR proof and manual correction facility.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-y border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Declaration Field</th>
                <th className="py-3 px-4 font-semibold">Extracted Value</th>
                <th className="py-3 px-4 font-semibold">OCR Evidence Text</th>
                <th className="py-3 px-4 font-semibold">Confidence</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {inspection.extracted_fields.map((field) => {
                const isSelected =
                  highlightedBbox &&
                  field.bbox &&
                  highlightedBbox[0] === field.bbox[0] &&
                  highlightedBbox[1] === field.bbox[1];

                return (
                  <tr
                    key={field.id}
                    className={`transition-colors cursor-pointer ${
                      isSelected ? 'bg-blue-50/60' : 'hover:bg-slate-50/70'
                    }`}
                    onClick={() => {
                      if (field.bbox) {
                        setHighlightedBbox(field.bbox);
                      }
                    }}
                  >
                    <td className="py-3.5 px-4 font-bold text-slate-900 whitespace-nowrap">
                      {field.field_name.replace('_', ' ').toUpperCase()}
                    </td>
                    <td className="py-3.5 px-4">
                      {field.is_manually_corrected ? (
                        <div>
                          <span className="font-semibold text-blue-700 block">
                            {field.corrected_value}
                          </span>
                          <span className="text-[10px] text-blue-500 italic">
                            (Manually Corrected by Officer)
                          </span>
                        </div>
                      ) : (
                        <span className="font-semibold text-slate-900">
                          {field.field_value || <span className="text-slate-400 italic">Not Detected</span>}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 max-w-xs">
                      <span className="font-mono text-slate-600 line-clamp-2 text-[11px]">
                        {field.original_ocr_text || '—'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold">
                      <span
                        className={
                          field.confidence >= 0.75
                            ? 'text-emerald-600'
                            : field.confidence >= 0.5
                            ? 'text-amber-600'
                            : 'text-slate-400'
                        }
                      >
                        {field.status === 'DETECTED' ? `${Math.round(field.confidence * 100)}%` : '—'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={field.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setCorrectionModalField(field);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition"
                        title="Correct OCR recognition mistake"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        <span>Correct</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECTION 16: Flagged Violations & Observations Table */}
      {inspection.violations && inspection.violations.length > 0 && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-rose-200/80 shadow-sm space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-rose-950 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-600" />
                <span>Flagged Observations & Statutory Violations ({inspection.violations.length})</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Specific clauses under Legal Metrology Rules 2011 requiring officer verification or enforcement.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {inspection.violations.map((viol) => (
              <div
                key={viol.id}
                className="p-5 rounded-2xl bg-rose-50/40 border border-rose-200 space-y-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase font-mono ${
                        viol.severity === 'CRITICAL'
                          ? 'bg-rose-600 text-white'
                          : viol.severity === 'HIGH'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {viol.severity}
                    </span>
                    <span className="font-bold text-slate-900 text-sm">
                      {viol.field_name.replace('_', ' ').toUpperCase()} • {viol.violation_type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-xs font-mono font-medium text-slate-600">
                    {viol.legal_reference}
                  </span>
                </div>

                <p className="text-xs text-slate-800 leading-relaxed font-medium">
                  {viol.description}
                </p>

                {viol.evidence_text && (
                  <div className="p-2.5 bg-white rounded-xl border border-slate-200 text-xs font-mono text-slate-700">
                    <strong className="text-slate-500 font-sans block text-[10px] uppercase">
                      OCR Evidence Observed:
                    </strong>
                    {viol.evidence_text}
                  </div>
                )}

                <div className="text-xs text-rose-900 bg-rose-100/60 p-2.5 rounded-xl flex items-start gap-2">
                  <span className="font-bold shrink-0">Recommended Action:</span>
                  <span>{viol.recommended_action}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Correction Modal Component (Section 15) */}
      <ManualCorrectionModal
        isOpen={!!correctionModalField}
        field={correctionModalField}
        onClose={() => setCorrectionModalField(null)}
        onSave={handleFieldCorrection}
      />
    </div>
  );
};

export default InspectionDetailPage;
