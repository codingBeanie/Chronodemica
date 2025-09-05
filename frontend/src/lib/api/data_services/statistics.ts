import { API } from '../core';

// Population ratio calculation with auto-save
export async function calculatePopulationRatio(popSize: number, periodId: number, popPeriodId: number): Promise<string> {
  try {
    // Handle edge case where popSize is 0
    if (popSize === 0) {
      return 'Ratio: 0%';
    }

    // First: Auto-save the pop_size value to database
    const updateResult = await API.update('PopPeriod', popPeriodId, { pop_size: popSize });
    
    if (!updateResult.success) {
      console.warn('Failed to auto-save pop_size:', updateResult.error);
      return '';
    }

    // Then: Query the statistics API for updated total pop_size
    const statsResult = await API.getStatistics(`period/${periodId}/pop-size`);
    
    if (!statsResult.success || !statsResult.data) {
      console.warn('Failed to fetch population statistics:', statsResult.error);
      return '';
    }

    const totalPopSize = statsResult.data.total_pop_size;
    
    // Handle division by zero
    if (totalPopSize === 0) {
      return 'Ratio: 0%';
    }

    // Calculate ratio as percentage
    const ratio = (popSize / totalPopSize) * 100;
    const roundedRatio = Math.round(ratio * 10) / 10; // Round to 1 decimal place
    
    return `Ratio: ${roundedRatio}%`;
    
  } catch (error) {
    console.warn('Error calculating population ratio:', error);
    return '';
  }
}