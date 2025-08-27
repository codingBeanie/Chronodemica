const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Database model endpoints mapping
const MODEL_ENDPOINTS = {
  'Period': 'periods',
  'Pop': 'pops', 
  'Party': 'parties',
  'PopPeriod': 'pop-periods',
  'PartyPeriod': 'party-periods',
  'PopVote': 'pop-votes',
  'ElectionResult': 'election-results'
} as const;

type ModelName = keyof typeof MODEL_ENDPOINTS;

// Error handling
export class APIError extends Error {
  status: number;
  
  constructor(message: string, status: number) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Generic HTTP request function
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new APIError(
        errorMessage || `HTTP error! status: ${response.status}`,
        response.status
      );
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return {} as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${error}`, 0);
  }
}

// Generic CRUD functions
export async function create<T>(model: ModelName, data: Partial<T>): Promise<T> {
  const endpoint = `/${MODEL_ENDPOINTS[model]}/`;
  return request<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAll<T>(model: ModelName, skip: number = 0, limit: number = 100): Promise<T[]> {
  const endpoint = `/${MODEL_ENDPOINTS[model]}?skip=${skip}&limit=${limit}`;
  return request<T[]>(endpoint);
}

export async function getById<T>(model: ModelName, id: number): Promise<T> {
  const endpoint = `/${MODEL_ENDPOINTS[model]}/${id}`;
  return request<T>(endpoint);
}

export async function update<T>(model: ModelName, id: number, data: Partial<T>): Promise<T> {
  const endpoint = `/${MODEL_ENDPOINTS[model]}/${id}`;
  return request<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function remove<T>(model: ModelName, id: number): Promise<T> {
  const endpoint = `/${MODEL_ENDPOINTS[model]}/${id}`;
  return request<T>(endpoint, {
    method: 'DELETE',
  });
}

// TypeScript interfaces matching the backend models
export interface Period {
  id?: number;
  year: number;
}

export interface Pop {
  id?: number;
  name: string;
}

export interface Party {
  id?: number;
  name: string;
  full_name?: string;
  color?: string;
}

export interface PopPeriod {
  id?: number;
  pop_id: number;
  period_id: number;
  population?: number;
  social_orientation?: number;
  economic_orientation?: number;
  max_political_distance?: number;
  variety_tolerance?: number;
  non_voters_distance?: number;
  small_party_distance?: number;
  ratio_eligible?: number;
}

export interface PartyPeriod {
  id?: number;
  party_id: number;
  period_id: number;
  social_orientation?: number;
  economic_orientation?: number;
  political_strength?: number;
}

export interface PopVote {
  id?: number;
  period_id: number;
  pop_id: number;
  party_id: number;
  votes?: number;
}

export interface ElectionResult {
  id?: number;
  period_id: number;
  party_id: number;
  votes?: number;
  percentage?: number;
  seats?: number;
  in_parliament?: boolean;
  in_government?: boolean;
  head_of_government?: boolean;
}