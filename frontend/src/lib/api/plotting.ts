import { API, type PopPeriod, type PartyPeriod, type Pop, type Party } from './api';

// Configuration - easily editable scalers
const SIZE_SCALERS = {
  PARTY_STRENGTH_SCALER: 1,
  POP_SIZE_SCALER: 1
};

/**
 * Simple orientation data format
 */
export interface OrientationData {
  x: number[];
  y: number[];
  text: string[];
  size: number[];
}

/**
 * Generic function to fetch entity data and resolve names
 * @param entityType - 'Pop' or 'Party' 
 * @param periodData - Array of period data with entity_id references
 * @returns Array of resolved entities with names
 */
async function resolveEntityNames<T extends { pop_id?: number; party_id?: number }>(
  entityType: 'Pop' | 'Party',
  periodData: T[]
): Promise<Array<T & { name: string }>> {
  const entityIds = periodData.map(item => 
    entityType === 'Pop' ? (item as any).pop_id : (item as any).party_id
  );
  
  const uniqueIds = [...new Set(entityIds)];
  
  const entityPromises = uniqueIds.map(id => API.getById<Pop | Party>(entityType, id));
  const entityResults = await Promise.all(entityPromises);
  
  const entityMap = new Map<number, string>();
  entityResults.forEach((result, index) => {
    if (result.success && result.data) {
      entityMap.set(uniqueIds[index], result.data.name);
    }
  });
  
  return periodData.map(item => ({
    ...item,
    name: entityMap.get(entityType === 'Pop' ? (item as any).pop_id : (item as any).party_id) || 'Unknown'
  }));
}

/**
 * Generic function to convert orientation data to simple format
 * @param data - Array of data with social/economic orientations and names
 * @param sizeField - Field to use for size calculation
 * @param scaler - Multiplier for size values
 * @returns Simple data format
 */
function formatOrientationData<T extends { 
  social_orientation?: number; 
  economic_orientation?: number; 
  name: string; 
}>(data: T[], sizeField: keyof T, scaler: number): OrientationData {
  console.log(`Formatting orientation data with ${data.length} items, sizeField: ${String(sizeField)}, scaler: ${scaler}`);
  
  if (data.length === 0) {
    console.log('No data to format');
    return {
      x: [],
      y: [],
      text: [],
      size: []
    };
  }
  
  console.log('Sample data item:', data[0]);
  
  return {
    x: data.map(item => {
      const val = item.economic_orientation ?? 0;
      console.log(`Economic orientation: ${val}`);
      return val;
    }),
    y: data.map(item => {
      const val = item.social_orientation ?? 0;
      console.log(`Social orientation: ${val}`);
      return val;
    }),
    text: data.map(item => {
      console.log(`Name: ${item.name}`);
      return item.name;
    }),
    size: data.map(item => {
      const value = item[sizeField];
      const result = typeof value === 'number' ? value * scaler : 8;
      console.log(`Size field ${String(sizeField)}: ${value} -> ${result}`);
      return result;
    })
  };
}

/**
 * Get party orientations data
 * @param periodId - The period ID to fetch data for
 * @returns Simple party orientation data
 */
export async function getPartyOrientations(periodId: number): Promise<OrientationData> {
  try {
    console.log('Getting party orientations for period:', periodId);
    const partyPeriodsResult = await API.getAll<PartyPeriod>(
      'PartyPeriod', 
      0, 
      100, 
      undefined, 
      undefined, 
      { period_id: periodId }
    );
    
    console.log('Party periods result:', partyPeriodsResult);
    
    const partyPeriods = partyPeriodsResult.success && partyPeriodsResult.data 
      ? partyPeriodsResult.data 
      : [];
    
    console.log('Party periods data:', partyPeriods);
    
    const resolvedParties = await resolveEntityNames('Party', partyPeriods);
    
    console.log('Resolved parties:', resolvedParties);
    
    const result = formatOrientationData(resolvedParties, 'political_strength', SIZE_SCALERS.PARTY_STRENGTH_SCALER);
    
    console.log('Formatted party data:', result);
    
    return result;
    
  } catch (error) {
    console.error('Error fetching party orientations:', error);
    return {
      x: [],
      y: [],
      text: [],
      size: []
    };
  }
}

/**
 * Get population orientations data
 * @param periodId - The period ID to fetch data for
 * @returns Simple population orientation data
 */
export async function getPopOrientations(periodId: number): Promise<OrientationData> {
  try {
    console.log('Getting pop orientations for period:', periodId);
    const popPeriodsResult = await API.getAll<PopPeriod>(
      'PopPeriod', 
      0, 
      100, 
      undefined, 
      undefined, 
      { period_id: periodId }
    );
    
    console.log('Pop periods result:', popPeriodsResult);
    
    const popPeriods = popPeriodsResult.success && popPeriodsResult.data 
      ? popPeriodsResult.data 
      : [];
    
    console.log('Pop periods data:', popPeriods);
    
    const resolvedPops = await resolveEntityNames('Pop', popPeriods);
    
    console.log('Resolved pops:', resolvedPops);
    
    const result = formatOrientationData(resolvedPops, 'pop_size', SIZE_SCALERS.POP_SIZE_SCALER);
    
    console.log('Formatted pop data:', result);
    
    return result;
    
  } catch (error) {
    console.error('Error fetching population orientations:', error);
    return {
      x: [],
      y: [],
      text: [],
      size: []
    };
  }
}