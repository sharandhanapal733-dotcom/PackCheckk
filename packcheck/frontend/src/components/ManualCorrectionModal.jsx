import React, { useState } from 'react';
import { X, CheckCircle, AlertTriangle, Edit3 } from 'lucide-react';

export const ManualCorrectionModal = ({
  isOpen,
  onClose,
  field,
  onSave,
}) => {
  if (!isOpen || !field) return null;

  const [value, setValue] = useState(field.corrected_value || field.field_value || '');
  const [notes, setNotes] = useState(field.correction_notes || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!value.trim()) {
      setError('Value cannot be empty');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await onSave(field.id, { corrected_value: value.trim(), notes: notes.trim() });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save correction. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white">
          <div className="flex items-center gap-2.5">
            <Edit3 className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-base">
              Correct Declaration: {field.field_name?.replace('_', ' ').toUpperCase()}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm">
              {error}
            </div>
          )}

          {/* Original Evidence Callout */}
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Original OCR Text Evidence (Unchanged)
            </div>
            <div className="text-sm font-mono text-slate-800 bg-white p-2.5 rounded border border-slate-200 break-words">
              {field.original_ocr_text || field.field_value || 'No text detected in OCR'}
            </div>
            <div className="text-[11px] text-slate-500">
              Confidence Score: {Math.round((field.confidence || 0) * 100)}%
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Corrected Value <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="e.g. ₹50.00 or 500 g"
              className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-medium"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              This corrected value will be re-validated by the Legal Metrology rule engine.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Officer Audit Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              placeholder="Reason for correction e.g. OCR misread digit 5 as letter S..."
              className="w-full px-3.5 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm transition disabled:opacity-50 flex items-center gap-2"
            >
              {saving ? 'Updating Score...' : 'Save & Re-evaluate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ManualCorrectionModal;
