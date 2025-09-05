import { API, type ApiResponse, type VotingBehavior, type PopPeriod, type ElectionResult, type Party } from '../core';

// Distance scoring interface for the curve data
export interface DistanceScoring {
  distance: number;
  score: number;
}

// Get distance scoring curve (0-100) for a PopPeriod
export async function getDistanceScoring(popPeriod: PopPeriod): Promise<ApiResponse<DistanceScoring[]>> {
  const result = await API.getSimulation(`pop-period/${popPeriod.id}/distance-scoring`);
  
  if (result.success && result.data) {
    return {
      success: true,
      data: result.data as DistanceScoring[]
    };
  }
  
  return result as ApiResponse<DistanceScoring[]>;
}

// Get voting behavior for a specific population in a period with processed data
export async function getVotingBehavior(periodId: number, popId: number): Promise<ApiResponse<VotingBehavior[]>> {
  const result = await API.getSimulation(`period/${periodId}/pop/${popId}/voting-behavior`);
  
  if (result.success && result.data) {
    // Filter out ID columns and votes column from each entry
    const filteredData = result.data.map((entry: any) => {
      const { pop_id, period_id, party_id, votes, ...filteredEntry } = entry;
      return filteredEntry;
    });
    
    // Sort by percentage in descending order (highest first)
    const sortedData = filteredData.sort((a: any, b: any) => {
      return (b.percentage || 0) - (a.percentage || 0);
    });
    
    return {
      success: true,
      data: sortedData as VotingBehavior[]
    };
  }
  
  return result as ApiResponse<VotingBehavior[]>;
}

// Interface for simulation results
export interface SimulationResult {
  success: boolean;
  message: string;
  period_id: number;
  parameters: {
    seats: number;
    threshold: number;
  };
  statistics: {
    total_votes: number;
    total_parties: number;
    parties_in_parliament: number;
    parliament_threshold_met: boolean;
  };
}

// Run complete election simulation
export async function runElectionSimulation(
  periodId: number, 
  seats: number, 
  threshold: number
): Promise<ApiResponse<SimulationResult>> {
  const result = await API.postSimulation(`period/${periodId}/full-simulation?seats=${seats}&threshold=${threshold}`);
  return result as ApiResponse<SimulationResult>;
}

// Enhanced election result interface with party names
export interface EnrichedElectionResult extends Omit<ElectionResult, 'party_id'> {
  party_id: number;
  party_name: string;
  party_full_name: string;
}

// Get election results for a period (raw, without party names)
export async function getElectionResults(periodId: number): Promise<ApiResponse<ElectionResult[]>> {
  const result = await API.getSimulation(`period/${periodId}/results`);
  return result as ApiResponse<ElectionResult[]>;
}

// Get election results enriched with party names
export async function getEnrichedElectionResults(periodId: number): Promise<ApiResponse<EnrichedElectionResult[]>> {
  try {
    // Get election results and all parties in parallel
    const [resultsResponse, partiesResponse] = await Promise.all([
      API.getSimulation(`period/${periodId}/results`),
      API.getAll<Party>('Party', 0, 1000) // Get all parties
    ]);

    if (!resultsResponse.success) {
      return resultsResponse as ApiResponse<EnrichedElectionResult[]>;
    }

    if (!partiesResponse.success) {
      return {
        success: false,
        error: partiesResponse.error || 'Failed to load parties'
      };
    }

    const results = resultsResponse.data || [];
    const parties = partiesResponse.data || [];

    // Create party lookup map
    const partyMap = new Map<number, Party>();
    parties.forEach(party => {
      if (party.id) {
        partyMap.set(party.id, party);
      }
    });

    // Enrich results with party names
    const enrichedResults: EnrichedElectionResult[] = results.map((result: ElectionResult) => {
      // Handle special party IDs for non-voters and small parties
      if (result.party_id === -1) {
        return {
          ...result,
          party_name: "Non-Voters",
          party_full_name: "Non-Voters"
        };
      }
      
      if (result.party_id === -2) {
        return {
          ...result,
          party_name: "Small Parties", 
          party_full_name: "Small Parties"
        };
      }
      
      // Handle regular parties
      const party = partyMap.get(result.party_id);
      return {
        ...result,
        party_name: party?.name || `Unknown Party (ID: ${result.party_id})`,
        party_full_name: party?.full_name || party?.name || `Unknown Party (ID: ${result.party_id})`
      };
    });

    return {
      success: true,
      data: enrichedResults
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to enrich election results'
    };
  }
}