import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { inspectionsAPI } from '../services/api';
import {
  Upload,
  FileText,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  X,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Building,
  Layers,
  MapPin,
  Cpu,
} from 'lucide-react';

export const NewInspectionPage = () => {
  const navigate = useNavigate();

  // Wizard state: 1 = Product Info, 2 = Image Upload, 3 = Processing
  const [step, setStep] = useState(1);

  // Form State
  const [productData, setProductData] = useState({
    product_name: '',
    brand: '',
    category: 'Packaged Food & Beverages',
    manufacturer: '',
    identifier: '',
    batch_number: '',
    location: 'Central Enforcement Station, New Delhi',
    inspector_remarks: '',
  });

  // Images state
  const [images, setImages] = useState([]); // array of { file, preview, side }
  const [selectedSide, setSelectedSide] = useState('Principal Display Panel (Front)');

  // Inspection & Processing State
  const [createdInspection, setCreatedInspection] = useState(null);
  const [processingStage, setProcessingStage] = useState(0); // 0-5
  const [processingStatusText, setProcessingStatusText] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Step 1: Submit Product Information
  const handleProductSubmit = (e) => {
    e.preventDefault();
    if (!productData.product_name.trim()) {
      setError('Product Name is required.');
      return;
    }
    setError('');
    setStep(2);
  };

  // Step 2: Handle Image Selection & Drag-Drop
  const handleFiles = (fileList) => {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const newImgs = [];

    Array.from(fileList).forEach((file) => {
      if (!validTypes.includes(file.type)) {
        setError(`File ${file.name} is not an accepted format (JPG, PNG, WEBP).`);
        return;
      }
      if (file.size > 15 * 1024 * 1024) {
        setError(`File ${file.name} exceeds 15MB limit.`);
        return;
      }
      newImgs.push({
        file,
        preview: URL.createObjectURL(file),
        side: selectedSide,
      });
    });

    if (newImgs.length > 0) {
      setImages((prev) => [...prev, ...newImgs]);
      setError('');
    }
  };

  const removeImage = (index) => {
    setImages((prev) => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index].preview);
      updated.splice(index, 1);
      return updated;
    });
  };

  // Step 3: Trigger Full Automated Processing Workflow
  const handleStartProcessing = async () => {
    if (images.length === 0) {
      setError('Please upload at least one package photograph before proceeding.');
      return;
    }

    setIsSubmitting(true);
    setError('');
    setStep(3);

    try {
      // 1. Create Inspection Draft in DB
      setProcessingStage(1);
      setProcessingStatusText('Creating inspection record in enforcement database...');
      const createRes = await inspectionsAPI.create(productData);
      const inspection = createRes.data;
      setCreatedInspection(inspection);

      // 2. Upload Images to Backend
      setProcessingStage(2);
      setProcessingStatusText(`Uploading ${images.length} package photograph(s)...`);
      const formData = new FormData();
      images.forEach((imgObj) => {
        formData.append('files', imgObj.file);
      });
      formData.append('image_side', selectedSide);
      await inspectionsAPI.uploadImages(inspection.id, formData);

      // 3. Preprocessing & OCR
      setProcessingStage(3);
      setProcessingStatusText('Executing CLAHE preprocessing & PaddleOCR vision engine...');
      // Brief aesthetic pause so user perceives pipeline stages
      await new Promise((r) => setTimeout(r, 600));

      // 4. Declaration Extraction & Rule Verification
      setProcessingStage(4);
      setProcessingStatusText('Extracting mandatory declarations and checking LMPC 2011 rules...');
      const processRes = await inspectionsAPI.process(inspection.id);

      // 5. Finalizing Report
      setProcessingStage(5);
      setProcessingStatusText('Compliance screening complete! Preparing evidence dossier...');
      await new Promise((r) => setTimeout(r, 800));

      // Navigate to detailed inspection result page!
      navigate(`/inspections/${inspection.id}`);
    } catch (err) {
      console.error('Processing failed:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to process inspection. Please ensure clear photographs and try again.'
      );
      setStep(2); // Go back to upload step on error
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Wizard Header & Stepper */}
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            New Packaged Commodity Inspection
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Automated screening under the Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        {/* Stepper Navigation */}
        <div className="grid grid-cols-3 gap-2 p-1.5 bg-slate-200/70 rounded-2xl">
          <div
            className={`py-2 px-3 rounded-xl flex items-center justify-center gap-2 text-xs font-semibold transition ${
              step === 1
                ? 'bg-white text-blue-600 shadow-sm'
                : step > 1
                ? 'text-slate-600'
                : 'text-slate-400'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
              1
            </span>
            <span className="hidden sm:inline">Product Information</span>
          </div>

          <div
            className={`py-2 px-3 rounded-xl flex items-center justify-center gap-2 text-xs font-semibold transition ${
              step === 2
                ? 'bg-white text-blue-600 shadow-sm'
                : step > 2
                ? 'text-slate-600'
                : 'text-slate-400'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
              2
            </span>
            <span className="hidden sm:inline">Package Photos</span>
          </div>

          <div
            className={`py-2 px-3 rounded-xl flex items-center justify-center gap-2 text-xs font-semibold transition ${
              step === 3
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-slate-400'
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px]">
              3
            </span>
            <span className="hidden sm:inline">OCR & Compliance</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Inspection Notice:</span>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* STEP 1: Product Information */}
      {step === 1 && (
        <form
          onSubmit={handleProductSubmit}
          className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6"
        >
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-100">
            <FileText className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">
              Step 1: Product & Inspection Metadata
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Product Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={productData.product_name}
                onChange={(e) => setProductData({ ...productData, product_name: e.target.value })}
                placeholder="e.g. Parle-G Gold Biscuits or Dettol Antiseptic Liquid"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Brand / Trademark
              </label>
              <input
                type="text"
                value={productData.brand}
                onChange={(e) => setProductData({ ...productData, brand: e.target.value })}
                placeholder="e.g. Parle, Nestle, Britannia"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Commodity Category
              </label>
              <select
                value={productData.category}
                onChange={(e) => setProductData({ ...productData, category: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Packaged Food & Beverages">Packaged Food & Beverages</option>
                <option value="Personal Care & Cosmetics">Personal Care & Cosmetics</option>
                <option value="Household Cleaners & Chemicals">Household Cleaners & Chemicals</option>
                <option value="Dairy & Perishables">Dairy & Perishables</option>
                <option value="Electronics & Accessories">Electronics & Accessories</option>
                <option value="Pharmaceutical & Healthcare">Pharmaceutical & Healthcare</option>
                <option value="Other Packaged Commodity">Other Packaged Commodity</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Manufacturer / Packer (Optional Pre-fill)
              </label>
              <input
                type="text"
                value={productData.manufacturer}
                onChange={(e) => setProductData({ ...productData, manufacturer: e.target.value })}
                placeholder="Leave blank for automatic OCR detection"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Barcode / EAN / Batch Identifier
              </label>
              <input
                type="text"
                value={productData.identifier}
                onChange={(e) => setProductData({ ...productData, identifier: e.target.value })}
                placeholder="e.g. 8901234567890"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Inspection Location
              </label>
              <input
                type="text"
                value={productData.location}
                onChange={(e) => setProductData({ ...productData, location: e.target.value })}
                placeholder="e.g. Retail Store, Warehouse, Port"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Batch Number (If stamped on outer seal)
              </label>
              <input
                type="text"
                value={productData.batch_number}
                onChange={(e) => setProductData({ ...productData, batch_number: e.target.value })}
                placeholder="e.g. B-2026/09"
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
                Officer Remarks & Notes
              </label>
              <textarea
                value={productData.inspector_remarks}
                onChange={(e) => setProductData({ ...productData, inspector_remarks: e.target.value })}
                rows={2}
                placeholder="Notes on packaging condition, shelf location, or physical seals..."
                className="w-full px-3.5 py-2 bg-white border border-slate-300 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="pt-4 flex items-center justify-end border-t border-slate-100">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md shadow-blue-500/20 transition text-sm"
            >
              <span>Continue to Package Photos</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      )}

      {/* STEP 2: Image Upload */}
      {step === 2 && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <ImageIcon className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">
                Step 2: Upload Package Photographs
              </h2>
            </div>
            <button
              onClick={() => setStep(1)}
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Edit Details</span>
            </button>
          </div>

          {/* Package Side Tag Selector */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-slate-600 mr-1">Package Face:</span>
            {[
              'Principal Display Panel (Front)',
              'Back Panel / Declarations',
              'Side Panel / Nutritional Info',
              'Bottom / Stamp Seal',
            ].map((side) => (
              <button
                key={side}
                type="button"
                onClick={() => setSelectedSide(side)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                  selectedSide === side
                    ? 'bg-blue-50 border-blue-400 text-blue-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {side}
              </button>
            ))}
          </div>

          {/* Drag & Drop Upload Dropzone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              handleFiles(e.dataTransfer.files);
            }}
            className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-3xl p-8 sm:p-12 text-center bg-slate-50/50 hover:bg-blue-50/20 transition-all cursor-pointer group"
            onClick={() => document.getElementById('file-upload-input').click()}
          >
            <input
              id="file-upload-input"
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
            <div className="w-16 h-16 rounded-2xl bg-white border border-slate-200 flex items-center justify-center mx-auto text-blue-600 shadow-sm group-hover:scale-105 transition-transform mb-3">
              <Upload className="w-8 h-8" />
            </div>
            <div className="text-sm font-semibold text-slate-800">
              Drag and drop product images here, or <span className="text-blue-600">browse files</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Supports high-resolution JPG, JPEG, PNG, WEBP (up to 15MB each). Multiple package sides accepted.
            </p>
          </div>

          {/* Image Previews Grid */}
          {images.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-700 uppercase tracking-wider">
                <span>Selected Photographs ({images.length})</span>
                <span className="text-slate-400 lowercase font-normal">Click × to remove</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {images.map((img, idx) => (
                  <div
                    key={idx}
                    className="relative rounded-2xl border border-slate-200 overflow-hidden bg-slate-900 group aspect-square shadow-sm"
                  >
                    <img
                      src={img.preview}
                      alt={`Package side ${idx + 1}`}
                      className="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
                    />
                    <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-slate-950/90 to-transparent text-[10px] text-white">
                      <div className="font-semibold truncate">{img.file.name}</div>
                      <div className="text-blue-300 text-[9px] truncate">{img.side}</div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeImage(idx);
                      }}
                      className="absolute top-2 right-2 p-1.5 bg-slate-900/80 hover:bg-rose-600 text-white rounded-full transition shadow"
                      title="Remove image"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Row */}
          <div className="pt-4 flex items-center justify-between border-t border-slate-100">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="px-5 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition"
            >
              Back to Details
            </button>

            <button
              type="button"
              onClick={handleStartProcessing}
              disabled={images.length === 0 || isSubmitting}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md shadow-blue-500/20 transition text-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch Automated OCR & Compliance Check</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Automated Processing Interface (Section 29) */}
      {step === 3 && (
        <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-xl space-y-8 text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto text-blue-600 animate-pulse">
            <Cpu className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-slate-900">
              Analyzing Packaged Commodity...
            </h2>
            <p className="text-sm text-slate-600 max-w-md mx-auto">
              {processingStatusText}
            </p>
          </div>

          {/* Pipeline Progress Stages */}
          <div className="max-w-md mx-auto space-y-3 text-left">
            {[
              { id: 1, label: 'Upload received & registered in database' },
              { id: 2, label: 'CLAHE image preprocessing & contrast enhancement' },
              { id: 3, label: 'PaddleOCR deep vision & bounding box coordinates' },
              { id: 4, label: 'LMPC mandatory declaration & entity extraction' },
              { id: 5, label: 'Legal Metrology rule validation & score calculation' },
            ].map((stg) => {
              const isCompleted = processingStage > stg.id;
              const isCurrent = processingStage === stg.id;

              return (
                <div
                  key={stg.id}
                  className={`p-3.5 rounded-xl border flex items-center gap-3 transition-all ${
                    isCompleted
                      ? 'bg-emerald-50/60 border-emerald-200 text-emerald-800'
                      : isCurrent
                      ? 'bg-blue-50 border-blue-300 text-blue-900 font-semibold ring-2 ring-blue-500/20'
                      : 'bg-slate-50 border-slate-200 text-slate-400'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : isCurrent ? (
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                  )}
                  <span className="text-xs">{stg.label}</span>
                </div>
              );
            })}
          </div>

          <div className="pt-2 text-xs text-slate-400 font-mono">
            Do not refresh browser. Analysis running on server...
          </div>
        </div>
      )}
    </div>
  );
};

export default NewInspectionPage;
