import React from 'react';
import { Company } from '../types';
import { MapPin, Briefcase, GraduationCap, Star } from 'lucide-react';

interface CompanyCardProps {
  company: Company;
  onSelect?: (company: Company) => void;
  isSelected?: boolean;
  showScore?: boolean;
}

export const CompanyCard: React.FC<CompanyCardProps> = ({
  company,
  onSelect,
  isSelected = false,
  showScore = false,
}) => {
  return (
    <div
      className={`bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer border-2 ${
        isSelected ? 'border-primary-500' : 'border-transparent'
      } ${company.is_platinum_sponsor ? 'ring-2 ring-yellow-400' : ''}`}
      onClick={() => onSelect?.(company)}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            {company.name}
            {company.is_platinum_sponsor && (
              <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            )}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
            <MapPin className="w-4 h-4" />
            <span>Booth {company.booth_number}</span>
            <span className="text-gray-400">•</span>
            <span>{company.ballroom}</span>
          </div>
        </div>
        {showScore && company.score !== undefined && (
          <div className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
            {(company.score * 100).toFixed(0)}% Match
          </div>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-start gap-2">
          <Briefcase className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
          <div className="flex flex-wrap gap-1">
            {company.position_types.map((type, idx) => (
              <span
                key={idx}
                className="inline-block bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded"
              >
                {type.replace('Entry-Level/Full-Time', 'Full-Time')
                     .replace('Internships', 'Internship')
                     .replace('Co-Op', 'Co-Op')}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-start gap-2">
          <GraduationCap className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-gray-600 line-clamp-2">
            {company.majors.length > 3
              ? `${company.majors.slice(0, 3).join(', ')} +${company.majors.length - 3} more`
              : company.majors.join(', ')}
          </div>
        </div>
      </div>

      {isSelected && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <span className="text-sm text-primary-600 font-medium">
            ✓ Added to route
          </span>
        </div>
      )}
    </div>
  );
};
