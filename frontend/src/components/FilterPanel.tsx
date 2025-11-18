import React, { useState, useEffect } from 'react';
import { FilterOptions } from '../types';
import { getMajors, getBallrooms, getPositionTypes } from '../services/api';
import { Search, Filter, X } from 'lucide-react';

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void;
  activeFilters: FilterOptions;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({ onFilterChange, activeFilters }) => {
  const [majors, setMajors] = useState<string[]>([]);
  const [ballrooms, setBallrooms] = useState<string[]>([]);
  const [positionTypes, setPositionTypes] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const loadFilters = async () => {
      try {
        const [majorsData, ballroomsData, positionTypesData] = await Promise.all([
          getMajors(),
          getBallrooms(),
          getPositionTypes(),
        ]);
        setMajors(majorsData);
        setBallrooms(ballroomsData);
        setPositionTypes(positionTypesData);
      } catch (error) {
        console.error('Failed to load filters:', error);
      }
    };
    loadFilters();
  }, []);

  const handleFilterChange = (key: keyof FilterOptions, value: string | boolean) => {
    onFilterChange({
      ...activeFilters,
      [key]: value || undefined,
    });
  };

  const clearFilters = () => {
    onFilterChange({});
  };

  const activeFilterCount = Object.values(activeFilters).filter(Boolean).length;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Filter className="w-5 h-5" />
          Filters
          {activeFilterCount > 0 && (
            <span className="bg-primary-500 text-white text-xs px-2 py-1 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </h2>
        <div className="flex gap-2">
          {activeFilterCount > 0 && (
            <button
              onClick={clearFilters}
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
            >
              <X className="w-4 h-4" />
              Clear all
            </button>
          )}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="lg:hidden text-sm text-primary-600 hover:text-primary-700"
          >
            {showFilters ? 'Hide' : 'Show'}
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search companies..."
            value={activeFilters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Filter Options */}
      <div className={`space-y-4 ${showFilters ? 'block' : 'hidden lg:block'}`}>
        {/* Major */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Major
          </label>
          <select
            value={activeFilters.major || ''}
            onChange={(e) => handleFilterChange('major', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Majors</option>
            {majors.map((major) => (
              <option key={major} value={major}>
                {major}
              </option>
            ))}
          </select>
        </div>

        {/* Position Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Position Type
          </label>
          <select
            value={activeFilters.position_type || ''}
            onChange={(e) => handleFilterChange('position_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Positions</option>
            {positionTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* Ballroom */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ballroom
          </label>
          <select
            value={activeFilters.ballroom || ''}
            onChange={(e) => handleFilterChange('ballroom', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Ballrooms</option>
            {ballrooms.map((ballroom) => (
              <option key={ballroom} value={ballroom}>
                {ballroom}
              </option>
            ))}
          </select>
        </div>

        {/* Platinum Only */}
        <div className="flex items-center">
          <input
            id="platinum-only"
            type="checkbox"
            checked={activeFilters.platinum_only || false}
            onChange={(e) => handleFilterChange('platinum_only', e.target.checked)}
            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
          />
          <label htmlFor="platinum-only" className="ml-2 text-sm text-gray-700">
            Platinum Sponsors Only
          </label>
        </div>
      </div>
    </div>
  );
};
