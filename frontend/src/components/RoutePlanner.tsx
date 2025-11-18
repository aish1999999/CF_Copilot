import React, { useState } from 'react';
import { Company, OptimizedRoute } from '../types';
import { optimizeRoute } from '../services/api';
import { Route, Clock, TrendingUp, MapPin, ArrowRight } from 'lucide-react';

interface RoutePlannerProps {
  selectedCompanies: Company[];
  onClearSelection: () => void;
}

export const RoutePlanner: React.FC<RoutePlannerProps> = ({
  selectedCompanies,
  onClearSelection,
}) => {
  const [timeBudget, setTimeBudget] = useState(180); // 3 hours
  const [optimizedRoute, setOptimizedRoute] = useState<OptimizedRoute | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    if (selectedCompanies.length === 0) {
      setError('Please select at least one company');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const companyIds = selectedCompanies.map(c => c.id);
      const route = await optimizeRoute(companyIds, timeBudget);
      setOptimizedRoute(route);
    } catch (err) {
      setError('Failed to optimize route. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Route className="w-6 h-6 text-primary-600" />
        Route Planner
      </h2>

      {/* Time Budget */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Time Budget (minutes)
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="30"
            max="300"
            step="15"
            value={timeBudget}
            onChange={(e) => setTimeBudget(parseInt(e.target.value))}
            className="flex-1"
          />
          <span className="text-lg font-semibold text-gray-900 w-20 text-right">
            {timeBudget} min
          </span>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {Math.floor(timeBudget / 60)}h {timeBudget % 60}m
        </p>
      </div>

      {/* Selected Companies */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-gray-700">
            Selected Companies ({selectedCompanies.length})
          </h3>
          {selectedCompanies.length > 0 && (
            <button
              onClick={onClearSelection}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Clear all
            </button>
          )}
        </div>
        <div className="max-h-40 overflow-y-auto space-y-2">
          {selectedCompanies.length === 0 ? (
            <p className="text-sm text-gray-500 italic">
              No companies selected. Click on companies to add them to your route.
            </p>
          ) : (
            selectedCompanies.map((company) => (
              <div
                key={company.id}
                className="flex items-center justify-between bg-gray-50 p-2 rounded"
              >
                <span className="text-sm text-gray-900">{company.name}</span>
                <span className="text-xs text-gray-500">Booth {company.booth_number}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Optimize Button */}
      <button
        onClick={handleOptimize}
        disabled={loading || selectedCompanies.length === 0}
        className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            Optimizing...
          </>
        ) : (
          <>
            <TrendingUp className="w-5 h-5" />
            Optimize Route
          </>
        )}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Optimized Route Display */}
      {optimizedRoute && (
        <div className="mt-6 border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimized Route</h3>

          {/* Summary */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-xs text-blue-600 font-medium mb-1">Companies</div>
              <div className="text-2xl font-bold text-blue-700">
                {optimizedRoute.companies_visited}
              </div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-xs text-green-600 font-medium mb-1">Total Time</div>
              <div className="text-2xl font-bold text-green-700">
                {Math.round(optimizedRoute.total_time)} min
              </div>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="text-xs text-purple-600 font-medium mb-1">Time Left</div>
              <div className="text-2xl font-bold text-purple-700">
                {Math.round(optimizedRoute.time_remaining)} min
              </div>
            </div>
          </div>

          {/* Route Steps */}
          <div className="space-y-3">
            {optimizedRoute.route.map((item, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{item.company_name}</div>
                  <div className="text-sm text-gray-600 flex items-center gap-3 mt-1">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      Booth {item.booth_number}
                    </span>
                    {item.ballroom && (
                      <span>{item.ballroom}</span>
                    )}
                  </div>
                  <div className="flex gap-3 mt-2 text-xs text-gray-500">
                    <span>
                      <Clock className="w-3 h-3 inline mr-1" />
                      Arrive: {Math.round(item.arrival_time)} min
                    </span>
                    <span>Travel: {Math.round(item.travel_time)} min</span>
                    <span>Visit: {Math.round(item.service_time)} min</span>
                  </div>
                </div>
                {index < optimizedRoute.route.length - 1 && (
                  <ArrowRight className="w-5 h-5 text-gray-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
