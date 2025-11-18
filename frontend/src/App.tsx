import React, { useState, useEffect } from 'react';
import { Company, FilterOptions, UserProfile } from './types';
import { getCompanies } from './services/api';
import { FilterPanel } from './components/FilterPanel';
import { CompanyList } from './components/CompanyList';
import { RoutePlanner } from './components/RoutePlanner';
import { FloorMap } from './components/FloorMap';
import { UserProfileModal } from './components/UserProfileModal';
import { Compass, User, Github } from 'lucide-react';

function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<Company[]>([]);
  const [filters, setFilters] = useState<FilterOptions>({});
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [activeView, setActiveView] = useState<'list' | 'map'>('list');

  useEffect(() => {
    loadCompanies();
  }, [filters]);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const data = await getCompanies(filters);
      setCompanies(data.companies);
    } catch (error) {
      console.error('Failed to load companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCompany = (company: Company) => {
    setSelectedCompanies((prev) => {
      const isSelected = prev.some((c) => c.id === company.id);
      if (isSelected) {
        return prev.filter((c) => c.id !== company.id);
      } else {
        return [...prev, company];
      }
    });
  };

  const handleClearSelection = () => {
    setSelectedCompanies([]);
  };

  const handleSaveProfile = (profile: Partial<UserProfile>) => {
    setUserProfile(profile as UserProfile);
    // In production, this would save to the backend
    console.log('Profile saved:', profile);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Compass className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  CF Copilot
                </h1>
                <p className="text-xs text-gray-500">
                  UH Engineering Career Fair Navigator
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowProfileModal(true)}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <User className="w-5 h-5" />
                <span className="hidden sm:inline">
                  {userProfile?.major || 'Set Profile'}
                </span>
              </button>
              <a
                href="https://github.com/aish1999999/CF_Copilot"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900"
              >
                <Github className="w-6 h-6" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1">
            <FilterPanel
              onFilterChange={setFilters}
              activeFilters={filters}
            />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* View Switcher */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveView('list')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeView === 'list'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Company List
                </button>
                <button
                  onClick={() => setActiveView('map')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeView === 'map'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Floor Map
                </button>
              </div>
            </div>

            {/* Content */}
            {activeView === 'list' ? (
              <CompanyList
                companies={companies}
                onSelectCompany={handleSelectCompany}
                selectedCompanies={selectedCompanies.map((c) => c.id)}
                loading={loading}
              />
            ) : (
              <FloorMap
                selectedCompanies={selectedCompanies}
                onBoothClick={(boothNumber) => {
                  // Find and select company by booth number
                  const company = companies.find(
                    (c) => c.booth_number === boothNumber
                  );
                  if (company) handleSelectCompany(company);
                }}
              />
            )}
          </div>

          {/* Right Sidebar - Route Planner */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <RoutePlanner
                selectedCompanies={selectedCompanies}
                onClearSelection={handleClearSelection}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Built with ❤️ for UH Engineering students | Powered by FastAPI &
            React
          </p>
        </div>
      </footer>

      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
        onSave={handleSaveProfile}
        initialProfile={userProfile || undefined}
      />
    </div>
  );
}

export default App;
