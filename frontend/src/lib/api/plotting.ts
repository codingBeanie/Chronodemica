import { API, type PopPeriod, type PartyPeriod, type Pop, type Party } from './api';

// ============================================
// SCALING CONFIGURATION - EDIT THESE VALUES
// ============================================
const SCALING_CONFIG = {
  // Party marker size scaling
  PARTY_BASE_SIZE: 8,           // Minimum party marker size
  PARTY_SCALE_FACTOR: 1,        // Multiplier for party strength values
  PARTY_MAX_SIZE: 50,           // Maximum party marker size
  
  // Pop marker size scaling  
  POP_BASE_SIZE: 8,             // Minimum pop marker size
  POP_SCALE_FACTOR: 1,        // Multiplier for pop size values (usually smaller since pop sizes are larger numbers)
  POP_MAX_SIZE: 50,             // Maximum pop marker size
};

/**
 * Simple orientation data format
 */
export interface OrientationData {
  x: number[];
  y: number[];
  text: string[];
  size: number[];
  colors?: string[];
}

/**
 * Generic function to fetch entity data and resolve names and colors
 * @param entityType - 'Pop' or 'Party' 
 * @param periodData - Array of period data with entity_id references
 * @returns Array of resolved entities with names and colors
 */
async function resolveEntityData<T extends { pop_id?: number; party_id?: number }>(
  entityType: 'Pop' | 'Party',
  periodData: T[]
): Promise<Array<T & { name: string; color?: string }>> {
  const entityIds = periodData.map(item => 
    entityType === 'Pop' ? (item as any).pop_id : (item as any).party_id
  );
  
  const uniqueIds = [...new Set(entityIds)];
  
  const entityPromises = uniqueIds.map(id => API.getById<Pop | Party>(entityType, id));
  const entityResults = await Promise.all(entityPromises);
  
  const entityMap = new Map<number, { name: string; color?: string }>();
  entityResults.forEach((result, index) => {
    if (result.success && result.data) {
      entityMap.set(uniqueIds[index], {
        name: result.data.name,
        color: (result.data as any).color || undefined
      });
    }
  });
  
  return periodData.map(item => {
    const entityData = entityMap.get(entityType === 'Pop' ? (item as any).pop_id : (item as any).party_id);
    return {
      ...item,
      name: entityData?.name || 'Unknown',
      color: entityData?.color
    };
  });
}

/**
 * Generic function to convert orientation data to simple format
 * @param data - Array of data with social/economic orientations, names, and colors
 * @param sizeField - Field to use for size calculation
 * @param sizeConfig - Size configuration object with baseSize, scaleFactor, and maxSize
 * @returns Simple data format
 */
function formatOrientationData<T extends { 
  social_orientation?: number; 
  economic_orientation?: number; 
  name: string;
  color?: string;
  [key: string]: any;
}>(data: T[], sizeField: keyof T, sizeConfig: { baseSize: number; scaleFactor: number; maxSize: number }): OrientationData {
  console.log(`Formatting orientation data with ${data.length} items, sizeField: ${String(sizeField)}, sizeConfig:`, sizeConfig);
  
  if (data.length === 0) {
    console.log('No data to format');
    return {
      x: [],
      y: [],
      text: [],
      size: [],
      colors: []
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
      const scaledValue = typeof value === 'number' ? value * sizeConfig.scaleFactor : 0;
      const result = Math.min(Math.max(scaledValue + sizeConfig.baseSize, sizeConfig.baseSize), sizeConfig.maxSize);
      console.log(`Size field ${String(sizeField)}: ${value} -> scaled: ${scaledValue} -> final: ${result}`);
      return result;
    }),
    colors: data.map(item => {
      console.log(`Color: ${item.color || 'none'}`);
      return item.color || '';
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
    
    const resolvedParties = await resolveEntityData('Party', partyPeriods);
    
    console.log('Resolved parties:', resolvedParties);
    
    const result = formatOrientationData(resolvedParties, 'political_strength', {
      baseSize: SCALING_CONFIG.PARTY_BASE_SIZE,
      scaleFactor: SCALING_CONFIG.PARTY_SCALE_FACTOR,
      maxSize: SCALING_CONFIG.PARTY_MAX_SIZE
    });
    
    console.log('Formatted party data:', result);
    
    return result;
    
  } catch (error) {
    console.error('Error fetching party orientations:', error);
    return {
      x: [],
      y: [],
      text: [],
      size: [],
      colors: []
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
    
    const resolvedPops = await resolveEntityData('Pop', popPeriods);
    
    console.log('Resolved pops:', resolvedPops);
    
    const result = formatOrientationData(resolvedPops, 'pop_size', {
      baseSize: SCALING_CONFIG.POP_BASE_SIZE,
      scaleFactor: SCALING_CONFIG.POP_SCALE_FACTOR,
      maxSize: SCALING_CONFIG.POP_MAX_SIZE
    });
    
    console.log('Formatted pop data:', result);
    
    return result;
    
  } catch (error) {
    console.error('Error fetching population orientations:', error);
    return {
      x: [],
      y: [],
      text: [],
      size: [],
      colors: []
    };
  }
}