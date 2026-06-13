import React from "react";
import { Download, ExternalLink } from "lucide-react";
import { API_BASE, authHeaders } from "../api/client";

interface InteractiveReportDownloadProps {
  downloadUrl: string | null;
  isEnabled: boolean;
}

export const InteractiveReportDownload: React.FC<InteractiveReportDownloadProps> = ({
  downloadUrl,
  isEnabled
}) => {
  const handleDownload = () => {
    if (!isEnabled || !downloadUrl) return;
    const url = `${API_BASE}${downloadUrl}?download=true`;
    // We can open it in a new window or trigger download via iframe/a tag.
    const link = document.createElement("a");
    link.href = url;
    link.download = "";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePreview = () => {
    if (!isEnabled || !downloadUrl) return;
    const url = `${API_BASE}${downloadUrl}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-md">
      <button
        onClick={handleDownload}
        disabled={!isEnabled || !downloadUrl}
        className="w-full sm:flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 disabled:bg-[#1a2e3b] disabled:text-cyan-800 disabled:border-[#1e2d42] border border-transparent text-white font-semibold rounded-lg shadow transition cursor-pointer"
      >
        <Download size={16} />
        <span>Download Interactive Report</span>
      </button>
      <button
        onClick={handlePreview}
        disabled={!isEnabled || !downloadUrl}
        className="w-full sm:flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-[#0b1724] border border-[#1e2d42] hover:border-cyan-500/50 hover:bg-[#071226] disabled:border-[#1e2d42] disabled:text-gray-600 disabled:bg-[#0b1724] text-cyan-200 font-semibold rounded-lg transition cursor-pointer"
      >
        <ExternalLink size={16} />
        <span>Preview Report</span>
      </button>
    </div>
  );
};

export default InteractiveReportDownload;
