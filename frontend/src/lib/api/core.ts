import { translateApiError, translateNetworkError } from './errorTranslator';

// API Response interface
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Database model endpoints mapping
const MODEL_ENDPOINTS = {
  'Period': 'period',
  'Pop': 'pop', 
  'Party': 'party',
  'PopPeriod': 'pop-period',
  'PartyPeriod': 'party-period',
  'PopVote': 'pop-vote',
  'ElectionResult': 'election-result'
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

// Generic HTTP request function with integrated error handling
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorMessage = await response.text();
      return {
        success: false,
        error: translateApiError(errorMessage, response.status)
      };
    }
    
    const contentType = response.headers.get('content-type');
    let data: T;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = {} as T;
    }
    
    return { success: true, data };
    
  } catch (error) {
    return {
      success: false,
      error: translateNetworkError(error)
    };
  }
}

// CRUD API functions 
export const API = {
  async create<T>(model: ModelName, data: Partial<T>): Promise<ApiResponse<T>> {
    // Filter out empty values and id field
    const submitData = Object.fromEntries(
      Object.entries(data).filter(([key, value]) => 
        key !== 'id' && value !== null && value !== undefined && value !== ''
      )
    );
    
    return request<T>(`/${MODEL_ENDPOINTS[model]}/`, {
      method: 'POST',
      body: JSON.stringify(submitData),
    });
  },

  async getAll<T>(
    model: ModelName, 
    skip: number = 0, 
    limit: number = 100, 
    sortBy?: string, 
    sortDirection?: 'ascending' | 'descending',
    filters?: Record<string, any>
  ): Promise<ApiResponse<T[]>> {
    let endpoint = `/${MODEL_ENDPOINTS[model]}?skip=${skip}&limit=${limit}`;
    
    if (sortBy && sortDirection) {
      const direction = sortDirection === 'descending' ? 'desc' : 'asc';
      endpoint += `&sort_by=${sortBy}&sort_direction=${direction}`;
    }
    
    // Add filters as query parameters
    if (filters) {
      for (const [key, value] of Object.entries(filters)) {
        if (value !== null && value !== undefined) {
          endpoint += `&${key}=${encodeURIComponent(value)}`;
        }
      }
    }
    
    const result = await request<T[]>(endpoint);
    
    // Client-side sorting fallback if backend doesn't support sorting
    if (result.success && result.data && sortBy && sortDirection) {
      const sortedData = [...result.data].sort((a: any, b: any) => {
        const aVal = a[sortBy];
        const bVal = b[sortBy];
        
        // Handle null/undefined values
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return 1;
        if (bVal == null) return -1;
        
        // Compare values
        let comparison = 0;
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          comparison = aVal.localeCompare(bVal);
        } else {
          comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        }
        
        return sortDirection === 'descending' ? -comparison : comparison;
      });
      
      return { ...result, data: sortedData };
    }
    
    return result;
  },

  async getById<T>(model: ModelName, id: number): Promise<ApiResponse<T>> {
    return request<T>(`/${MODEL_ENDPOINTS[model]}/${id}`);
  },

  async update<T>(model: ModelName, id: number, data: Partial<T>): Promise<ApiResponse<T>> {
    return request<T>(`/${MODEL_ENDPOINTS[model]}/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete<T>(model: ModelName, id: number): Promise<ApiResponse<T>> {
    return request<T>(`/${MODEL_ENDPOINTS[model]}/${id}`, {
      method: 'DELETE',
    });
  },

  async getDataStructure(model: string): Promise<ApiResponse<any>> {
    return request(`/data-structure/${model.toLowerCase()}`, {
      method: 'GET',
    });
  },

  // Raw endpoint calls for statistics and simulation
  async getStatistics(endpoint: string): Promise<ApiResponse<any>> {
    return request(`/statistics/${endpoint}`);
  },

  async getSimulation(endpoint: string): Promise<ApiResponse<any>> {
    return request(`/simulation/${endpoint}`);
  },

  async postSimulation(endpoint: string, data?: any): Promise<ApiResponse<any>> {
    return request(`/simulation/${endpoint}`, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }
};

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
  pop_size?: number;
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

// Voting behavior interface (filtered - without ID columns and votes)
export interface VotingBehavior {
  pop_name: string;
  party_name: string;
  party_full_name: string;
  distance: number;
  raw_score: number;
  strength: number;
  adjusted_score: number;
  percentage: number;
}