import React from 'react';
import { Company } from '../types';
import { CompanyCard } from './CompanyCard';
import { Building2 } from 'lucide-react';

interface CompanyListProps {
  companies: Company[];
  onSelectCompany: (company: Company) => void;
  selectedCompanies: number[];
  loading?: boolean;
}

export const CompanyList: React.FC<CompanyListProps> = ({
  companies,
  onSelectCompany,
  selectedCompanies,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="text-center py-12">
        <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No companies found</h3>
        <p className="text-gray-600">
          Try adjusting your filters to see more results
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          {companies.length} {companies.length === 1 ? 'Company' : 'Companies'}
        </h2>
        {selectedCompanies.length > 0 && (
          <span className="text-sm text-gray-600">
            {selectedCompanies.length} selected
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {companies.map((company) => (
          <CompanyCard
            key={company.id}
            company={company}
            onSelect={onSelectCompany}
            isSelected={selectedCompanies.includes(company.id)}
            showScore={company.score !== undefined}
          />
        ))}
      </div>
    </div>
  );
};
