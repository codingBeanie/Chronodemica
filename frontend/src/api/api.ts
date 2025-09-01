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

  async getAll<T>(model: ModelName, skip: number = 0, limit: number = 100): Promise<ApiResponse<T[]>> {
    return request<T[]>(`/${MODEL_ENDPOINTS[model]}?skip=${skip}&limit=${limit}`);
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