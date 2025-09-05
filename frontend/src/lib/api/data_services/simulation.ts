import { API, type ApiResponse, type VotingBehavior } from '../core';

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