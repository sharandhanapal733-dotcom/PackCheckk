import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Eye, ShieldCheck, Tag } from 'lucide-react';

export const OCRViewer = ({
  image,
  ocrResults = [],
  highlightedBbox = null,
  onSelectBox = null,
}) => {
  const [scale, setScale] = useState(1);
  const [activeBox, setActiveBox] = useState(null);
  const [naturalDimensions, setNaturalDimensions] = useState({ width: 1, height: 1 });
  const imgRef = useRef(null);

  // Sync external highlighted box
  useEffect(() => {
    if (highlightedBbox) {
      setActiveBox(highlightedBbox);
    }
  }, [highlightedBbox]);

  const onImageLoad = (e) => {
    setNaturalDimensions({
      width: e.target.naturalWidth || 800,
      height: e.target.naturalHeight || 600,
    });
  };

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.25, 3));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.25, 0.5));
  const handleResetZoom = () => setScale(1);

  const imgSrc = image?.file_path?.startsWith('http')
    ? image.file_path
    : `/${image?.file_path || ''}`;

  return (
    <div className="flex flex-col bg-slate-900 rounded-xl overflow-hidden shadow-lg border border-slate-800">
      {/* Viewer Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-950/80 border-b border-slate-800 text-slate-300 text-xs">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-blue-400" />
          <span className="font-medium text-white">{image?.original_filename || 'Package Photograph'}</span>
          <span className="text-slate-500">|</span>
          <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-400">
            {ocrResults.length} text blocks detected
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-1.5 hover:bg-slate-800 rounded transition text-slate-400 hover:text-white"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="w-12 text-center font-mono text-slate-400">{Math.round(scale * 100)}%</span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 hover:bg-slate-800 rounded transition text-slate-400 hover:text-white"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1.5 hover:bg-slate-800 rounded transition text-slate-400 hover:text-white ml-1"
            title="Reset Zoom"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Interactive Canvas Area */}
      <div className="relative overflow-auto max-h-[550px] min-h-[400px] flex items-center justify-center p-4 bg-slate-950/50">
        <div
          className="relative inline-block transition-transform duration-150 origin-center"
          style={{ transform: `scale(${scale})` }}
        >
          <img
            ref={imgRef}
            src={imgSrc}
            alt="Product Package"
            onLoad={onImageLoad}
            className="max-w-full max-h-[500px] object-contain rounded select-none block"
          />

          {/* SVG Bounding Boxes Overlay */}
          {naturalDimensions.width > 1 && (
            <svg
              className="absolute inset-0 w-full h-full pointer-events-auto"
              viewBox={`0 0 ${naturalDimensions.width} ${naturalDimensions.height}`}
              preserveAspectRatio="none"
            >
              {ocrResults.map((item, idx) => {
                const box = item.box || [];
                if (box.length < 4) return null;
                const [xmin, ymin, xmax, ymax] = box;
                const width = Math.max(xmax - xmin, 4);
                const height = Math.max(ymax - ymin, 4);

                const isHighlighted =
                  activeBox &&
                  activeBox[0] === xmin &&
                  activeBox[1] === ymin &&
                  activeBox[2] === xmax &&
                  activeBox[3] === ymax;

                return (
                  <g key={idx} className="cursor-pointer group">
                    <rect
                      x={xmin}
                      y={ymin}
                      width={width}
                      height={height}
                      fill={isHighlighted ? 'rgba(59, 130, 246, 0.35)' : 'rgba(16, 185, 129, 0.12)'}
                      stroke={isHighlighted ? '#3b82f6' : '#10b981'}
                      strokeWidth={isHighlighted ? 3 : 1.5}
                      strokeDasharray={isHighlighted ? 'none' : '3 3'}
                      className="transition-all duration-150 hover:fill-blue-500/40 hover:stroke-blue-400"
                      onClick={() => {
                        setActiveBox(box);
                        if (onSelectBox) onSelectBox(item);
                      }}
                    />
                  </g>
                );
              })}
            </svg>
          )}
        </div>
      </div>

      {/* Selected Box Inspector Panel */}
      {activeBox && (
        <div className="px-4 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-900/40 border border-blue-700/50 rounded-lg text-blue-400">
              <Tag className="w-4 h-4" />
            </div>
            <div>
              <div className="text-slate-400 text-[11px]">Selected OCR Region Evidence</div>
              <div className="text-white font-medium text-sm mt-0.5">
                {ocrResults.find(
                  (r) =>
                    r.box &&
                    r.box[0] === activeBox[0] &&
                    r.box[1] === activeBox[1] &&
                    r.box[2] === activeBox[2]
                )?.text || 'Bounding Box Selected'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="text-slate-400 block text-[10px]">Confidence</span>
              <span className="font-mono text-emerald-400 font-semibold">
                {Math.round(
                  (ocrResults.find(
                    (r) =>
                      r.box &&
                      r.box[0] === activeBox[0] &&
                      r.box[1] === activeBox[1]
                  )?.confidence || 0.9) * 100
                )}
                %
              </span>
            </div>
            <button
              onClick={() => setActiveBox(null)}
              className="text-slate-400 hover:text-white px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default OCRViewer;
