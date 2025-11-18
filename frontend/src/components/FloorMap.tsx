import React, { useState, useEffect } from 'react';
import { Booth, Company } from '../types';
import { getBooths } from '../services/api';
import { Map, ZoomIn, ZoomOut } from 'lucide-react';

interface FloorMapProps {
  selectedCompanies: Company[];
  onBoothClick?: (boothNumber: string) => void;
}

export const FloorMap: React.FC<FloorMapProps> = ({
  selectedCompanies,
  onBoothClick,
}) => {
  const [booths, setBooths] = useState<Booth[]>([]);
  const [selectedBallroom, setSelectedBallroom] = useState<string>('Waldorf');
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    loadBooths();
  }, [selectedBallroom]);

  const loadBooths = async () => {
    setLoading(true);
    try {
      const data = await getBooths(selectedBallroom);
      setBooths(data.booths);
    } catch (error) {
      console.error('Failed to load booths:', error);
    } finally {
      setLoading(false);
    }
  };

  const ballrooms = ['Waldorf', 'Conrad', 'Shamrock'];
  const selectedBoothNumbers = selectedCompanies.map(c => c.booth_number);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <Map className="w-6 h-6 text-primary-600" />
          Floor Map
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
            className="p-2 hover:bg-gray-100 rounded"
          >
            <ZoomOut className="w-5 h-5" />
          </button>
          <button
            onClick={() => setZoom(Math.min(2, zoom + 0.1))}
            className="p-2 hover:bg-gray-100 rounded"
          >
            <ZoomIn className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Ballroom Selector */}
      <div className="mb-6">
        <div className="flex gap-2">
          {ballrooms.map((ballroom) => (
            <button
              key={ballroom}
              onClick={() => setSelectedBallroom(ballroom)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedBallroom === ballroom
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {ballroom}
            </button>
          ))}
        </div>
      </div>

      {/* Map Container */}
      <div className="border-2 border-gray-200 rounded-lg overflow-hidden bg-gray-50">
        {loading ? (
          <div className="flex justify-center items-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="relative h-96 overflow-auto">
            <svg
              width={800 * zoom}
              height={600 * zoom}
              className="mx-auto"
              style={{ minWidth: '100%', minHeight: '100%' }}
            >
              {/* Grid */}
              <defs>
                <pattern
                  id="grid"
                  width={40 * zoom}
                  height={40 * zoom}
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d={`M ${40 * zoom} 0 L 0 0 0 ${40 * zoom}`}
                    fill="none"
                    stroke="gray"
                    strokeWidth="0.5"
                    opacity="0.2"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Booths */}
              {booths.map((booth) => {
                const isSelected = selectedBoothNumbers.includes(booth.booth_number);
                const x = (booth.coordinates.x || 0) * zoom;
                const y = (booth.coordinates.y || 0) * zoom;
                const size = 30 * zoom;

                return (
                  <g
                    key={booth.id}
                    onClick={() => onBoothClick?.(booth.booth_number)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={x}
                      cy={y}
                      r={size / 2}
                      fill={isSelected ? '#3b82f6' : '#e5e7eb'}
                      stroke={isSelected ? '#1d4ed8' : '#9ca3af'}
                      strokeWidth={2}
                      className="hover:opacity-80 transition-opacity"
                    />
                    <text
                      x={x}
                      y={y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="text-xs font-bold pointer-events-none"
                      fill={isSelected ? 'white' : '#374151'}
                      fontSize={10 * zoom}
                    >
                      {booth.booth_number.split('/')[0]}
                    </text>
                    {/* Queue indicator */}
                    {booth.queue_length > 0 && (
                      <circle
                        cx={x + size / 2}
                        cy={y - size / 2}
                        r={6 * zoom}
                        fill="#ef4444"
                        stroke="white"
                        strokeWidth={1}
                      >
                        <title>{booth.queue_length} in queue</title>
                      </circle>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-gray-300 border-2 border-gray-500"></div>
          <span>Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-primary-500 border-2 border-primary-700"></div>
          <span>Selected</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span>Has Queue</span>
        </div>
      </div>
    </div>
  );
};
