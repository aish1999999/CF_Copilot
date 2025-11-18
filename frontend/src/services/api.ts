import axios from 'axios';
import type { Company, Booth, User, UserProfile, OptimizedRoute, FilterOptions } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Companies
export const getCompanies = async (filters?: FilterOptions): Promise<{ companies: Company[], total: number }> => {
  const params = new URLSearchParams();
  if (filters?.major) params.append('major', filters.major);
  if (filters?.position_type) params.append('position_type', filters.position_type);
  if (filters?.ballroom) params.append('ballroom', filters.ballroom);
  if (filters?.search) params.append('search', filters.search);
  if (filters?.platinum_only) params.append('platinum_only', 'true');

  const response = await api.get(`/companies/?${params.toString()}`);
  return response.data;
};

export const getCompanyById = async (id: number): Promise<Company> => {
  const response = await api.get(`/companies/${id}`);
  return response.data;
};

export const getCompanyByBooth = async (boothNumber: string): Promise<Company> => {
  const response = await api.get(`/companies/booth/${boothNumber}`);
  return response.data;
};

export const getMajors = async (): Promise<string[]> => {
  const response = await api.get('/companies/filters/majors');
  return response.data.majors;
};

export const getBallrooms = async (): Promise<string[]> => {
  const response = await api.get('/companies/filters/ballrooms');
  return response.data.ballrooms;
};

export const getPositionTypes = async (): Promise<string[]> => {
  const response = await api.get('/companies/filters/position-types');
  return response.data.position_types;
};

// Booths
export const getBooths = async (ballroom?: string): Promise<{ booths: Booth[], total: number }> => {
  const params = ballroom ? `?ballroom=${ballroom}` : '';
  const response = await api.get(`/booths/${params}`);
  return response.data;
};

export const getBooth = async (boothNumber: string): Promise<Booth> => {
  const response = await api.get(`/booths/${boothNumber}`);
  return response.data;
};

export const updateQueueLength = async (boothNumber: string, queueLength: number): Promise<void> => {
  await api.patch(`/booths/${boothNumber}/queue`, { queue_length: queueLength });
};

// Routing
export const optimizeRoute = async (
  companyIds: number[],
  timeBudget: number = 180,
  userId?: number
): Promise<OptimizedRoute> => {
  const response = await api.post('/routing/optimize/', {
    company_ids: companyIds,
    time_budget_minutes: timeBudget,
    user_id: userId,
  });
  return response.data;
};

export const calculateRouteTime = async (
  boothSequence: string[],
  avgInteractionTime: number = 5.0
): Promise<{ booth_sequence: string[], total_time_minutes: number, num_booths: number }> => {
  const response = await api.post('/routing/calculate-time/', {
    booth_sequence: boothSequence,
    avg_interaction_time: avgInteractionTime,
  });
  return response.data;
};

export const getShortestPath = async (
  start: string,
  end: string
): Promise<{ start: string, end: string, path: string[], travel_time_minutes: number, num_hops: number }> => {
  const response = await api.get(`/routing/shortest-path?start=${start}&end=${end}`);
  return response.data;
};

// Users
export const createUser = async (
  username: string,
  email: string,
  major?: string,
  timeBudget: number = 180
): Promise<User> => {
  const response = await api.post('/users/', {
    username,
    email,
    major,
    time_budget_minutes: timeBudget,
  });
  return response.data;
};

export const getUser = async (userId: number): Promise<User> => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export const updateUserProfile = async (
  userId: number,
  profile: Partial<UserProfile>
): Promise<{ message: string, profile: UserProfile }> => {
  const response = await api.patch(`/users/${userId}/profile`, profile);
  return response.data;
};
