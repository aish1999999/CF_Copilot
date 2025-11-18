export interface Company {
  id: number;
  name: string;
  booth_number: string;
  ballroom: string;
  is_platinum_sponsor: boolean;
  position_types: string[];
  majors: string[];
  website?: string;
  careers_url?: string;
  description?: string;
  sector?: string;
  score?: number;
}

export interface Booth {
  id: number;
  booth_number: string;
  ballroom: string;
  coordinates: {
    x: number;
    y: number;
  };
  queue_length: number;
  service_time_estimate: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  session_id: string;
  profile?: UserProfile;
}

export interface UserProfile {
  major?: string;
  skills?: string;
  experience_level?: string;
  time_budget_minutes: number;
}

export interface RouteItem {
  company_id: number;
  company_name?: string;
  booth_number: string;
  ballroom?: string;
  travel_time: number;
  service_time: number;
  arrival_time: number;
  score: number;
}

export interface OptimizedRoute {
  route: RouteItem[];
  total_time: number;
  total_score: number;
  companies_visited: number;
  time_remaining: number;
}

export interface FilterOptions {
  major?: string;
  position_type?: string;
  ballroom?: string;
  search?: string;
  platinum_only?: boolean;
}

export interface CompanyWithScore extends Company {
  score: number;
}
