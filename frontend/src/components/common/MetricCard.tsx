import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  subtext?: string;
  icon: LucideIcon;
  accentColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  isPositive = true,
  subtext,
  icon: Icon,
  accentColor = "text-[#7C3AED]"
}) => {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 hover:scale-[1.02] transition-all duration-300 transform cursor-default">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl bg-[#EEF4FF] sm:bg-[#F8FAFC]`}>
          <Icon className={`w-5 h-5 ${accentColor}`} />
        </div>
      </div>
      
      <div className="mt-4">
        <h3 className="text-3xl font-bold tracking-tight text-[#0F172A] font-heading">
          {value}
        </h3>
        
        {(change || subtext) && (
          <div className="mt-2 flex items-center gap-1.5 text-xs">
            {change && (
              <span className={`font-semibold ${isPositive ? "text-emerald-600" : "text-rose-600"}`}>
                {change}
              </span>
            )}
            {subtext && (
              <span className="text-[#64748B]">
                {subtext}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
