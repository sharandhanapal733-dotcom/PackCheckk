import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  ScanText,
  FileCheck2,
  FileSpreadsheet,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Cpu,
  Database,
  Building,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  const workflowSteps = [
    {
      num: '01',
      title: 'Package Upload',
      desc: 'High-res image capture of principal display panels, wrappers, or cartons.',
      icon: ScanText,
    },
    {
      num: '02',
      title: 'Image Preprocessing',
      desc: 'CLAHE contrast enhancement, deskewing, and unsharp masking for clarity.',
      icon: Cpu,
    },
    {
      num: '03',
      title: 'PaddleOCR Engine',
      desc: 'Deep DBNet detection and CRNN character recognition with polygon coordinates.',
      icon: Sparkles,
    },
    {
      num: '04',
      title: 'LMPC Field Extraction',
      desc: 'Entity extraction for MRP, Net Qty, Dates, Manufacturer address, and Care details.',
      icon: FileSpreadsheet,
    },
    {
      num: '05',
      title: 'Rule Engine Verification',
      desc: 'Configurable validation against Legal Metrology Rules 2011 statutory provisions.',
      icon: ShieldCheck,
    },
    {
      num: '06',
      title: 'Evidence-Backed Report',
      desc: 'Generate official PDF inspection certificate with bounding-box proof.',
      icon: FileCheck2,
    },
  ];

  return (
    <div className="space-y-16 py-6 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center max-w-4xl mx-auto space-y-6 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 border border-blue-200 text-blue-800 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <span>SIH Problem Statement SIH26034 • Ministry of Consumer Affairs</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-950 tracking-tight leading-tight">
          PackCheck
          <span className="block text-2xl sm:text-3xl lg:text-4xl font-bold text-blue-600 mt-2">
            AI-Assisted Packaged Commodity Compliance Inspection
          </span>
        </h1>

        <p className="text-lg sm:text-xl font-medium text-slate-600 italic">
          "Scan. Analyze. Verify. Report."
        </p>

        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
          An automated preliminary screening and inspection-assistance platform enforcing the{' '}
          <strong className="text-slate-800">Legal Metrology (Packaged Commodities) Rules, 2011</strong>.
          Scan package labels, extract mandatory declarations, detect statutory violations, and generate
          evidence-backed inspection reports.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            to={isAuthenticated ? "/inspections/new" : "/login"}
            className="inline-flex items-center gap-2.5 px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all text-sm group"
          >
            <span>Start New Inspection</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to={isAuthenticated ? "/dashboard" : "/login"}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 font-semibold rounded-xl shadow-sm transition text-sm"
          >
            {isAuthenticated ? "Open Dashboard" : "Officer Login"}
          </Link>
        </div>
      </div>

      {/* Visual Workflow Steps (Section 25) */}
      <div className="bg-white rounded-3xl p-8 sm:p-10 border border-slate-200 shadow-xl shadow-slate-200/50">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl font-bold text-slate-900">Automated Inspection Pipeline</h2>
          <p className="text-sm text-slate-500 mt-1">
            End-to-end evidence processing from uploaded package photographs to legally-verifiable findings.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflowSteps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="relative p-6 rounded-2xl bg-slate-50 border border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors shadow-sm">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-400">
                    STEP {step.num}
                  </span>
                </div>
                <h3 className="font-bold text-base text-slate-900 group-hover:text-blue-900 transition-colors">
                  {step.title}
                </h3>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Mandatory Declarations Checked */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-slate-900 text-white rounded-3xl p-8 border border-slate-800 shadow-xl space-y-5">
          <div className="flex items-center gap-2.5 text-blue-400 text-sm font-semibold">
            <Building className="w-5 h-5" />
            <span>Rule 6, LMPC Rules 2011 Standards</span>
          </div>
          <h3 className="text-xl font-bold text-white">
            Mandatory Package Declarations Checked
          </h3>
          <ul className="space-y-3 text-xs text-slate-300">
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(a):</strong> Manufacturer, Packer, or Importer name and complete address with pin code.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(b):</strong> Generic or common name of the commodity.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(c):</strong> Net quantity in standard metric units (Second Schedule).</span>
            </li>
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(d):</strong> Month and year of manufacture or pre-packing.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(da):</strong> Maximum Retail Price (MRP) in INR inclusive of all taxes.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Rule 6(1)(f):</strong> Consumer care contact details (person name, phone/email, address).</span>
            </li>
          </ul>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-xl flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-amber-700 text-sm font-semibold">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <span>Legal Safety & Scientific Integrity</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900">
              Responsible Enforcement Screening
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              PackCheck is engineered with strict legal safety boundaries:
            </p>
            <ul className="space-y-2 text-xs text-slate-600">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span>Distinguishes <strong>Pass, Potential Non-Compliance, and Manual Review</strong>.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span>OCR failures or low confidence are never treated as proof of legal illegality.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span>Does not fabricate physical font millimeter measurements without calibrated scale.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span>Allows officers to audit and manually correct OCR misreadings while preserving original evidence.</span>
              </li>
            </ul>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between">
            <div className="text-xs text-slate-600">
              <span className="font-semibold text-slate-900 block">Ready to inspect a packaged commodity?</span>
              Launch the scanning tool with image upload.
            </div>
            <Link
              to={isAuthenticated ? "/inspections/new" : "/login"}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow transition shrink-0"
            >
              Start Inspection
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
