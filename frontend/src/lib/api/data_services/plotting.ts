import { API, type PopPeriod, type PartyPeriod, type Pop, type Party } from '../core';
import type { EnrichedElectionResult } from './simulation';

const SCALING_CONFIG = {
  PARTY_BASE_SIZE: 5,
  PARTY_SCALE_FACTOR: 1,
  PARTY_MAX_SIZE: 100,
  POP_BASE_SIZE: 5,
  POP_SCALE_FACTOR: 1,
  POP_MAX_SIZE: 100,
};

const EMPTY_ORIENTATION_DATA: OrientationData = {
  x: [],
  y: [],
  text: [],
  size: [],
  colors: []
};

export interface OrientationData {
  x: number[];
  y: number[];
  text: string[];
  size: number[];
  colors?: string[];
}

export interface ElectionBarData {
  x: string[];
  y: number[];
  text: string[];
  colors: string[];
  voterTurnout: number;
}

async function resolveEntityData<T extends { pop_id?: number; party_id?: number }>(
  entityType: 'Pop' | 'Party',
  periodData: T[]
): Promise<Array<T & { name: string; color?: string }>> {
  const getEntityId = (item: T) => entityType === 'Pop' ? item.pop_id : item.party_id;
  const entityIds = periodData.map(getEntityId);
  const uniqueIds = [...new Set(entityIds.filter(id => id !== undefined))] as number[];
  
  const entityResults = await Promise.all(
    uniqueIds.map(id => API.getById<Pop | Party>(entityType, id))
  );
  
  const entityMap = new Map<number, { name: string; color?: string }>();
  entityResults.forEach((result, index) => {
    if (result.success && result.data) {
      entityMap.set(uniqueIds[index], {
        name: result.data.name,
        color: (result.data as Pop & Party).color
      });
    }
  });
  
  return periodData.map(item => {
    const entityId = getEntityId(item);
    const entityData = entityId ? entityMap.get(entityId) : undefined;
    return {
      ...item,
      name: entityData?.name || 'Unknown',
      color: entityData?.color
    };
  });
}

function formatOrientationData<T extends { 
  social_orientation?: number; 
  economic_orientation?: number; 
  name: string;
  color?: string;
  [key: string]: any;
}>(data: T[], sizeField: keyof T, sizeConfig: { baseSize: number; scaleFactor: number; maxSize: number }): OrientationData {
  if (data.length === 0) {
    return { ...EMPTY_ORIENTATION_DATA };
  }
  
  return {
    x: data.map(item => item.economic_orientation ?? 0),
    y: data.map(item => item.social_orientation ?? 0),
    text: data.map(item => item.name),
    size: data.map(item => {
      const value = item[sizeField];
      const scaledValue = typeof value === 'number' ? value * sizeConfig.scaleFactor : 0;
      return Math.min(Math.max(scaledValue + sizeConfig.baseSize, sizeConfig.baseSize), sizeConfig.maxSize);
    }),
    colors: data.map(item => item.color || '')
  };
}

async function fetchOrientationData<T extends { pop_id?: number; party_id?: number }>(
  entityType: 'Pop' | 'Party',
  periodId: number,
  sizeField: string,
  sizeConfig: { baseSize: number; scaleFactor: number; maxSize: number }
): Promise<OrientationData> {
  try {
    const entityTypeEndpoint = `${entityType}Period` as const;
    const result = await API.getAll<T>(
      entityTypeEndpoint as any,
      0,
      100,
      undefined,
      undefined,
      { period_id: periodId }
    );
    
    const periodData = result.success && result.data ? result.data : [];
    const resolvedData = await resolveEntityData(entityType, periodData);
    
    return formatOrientationData(resolvedData, sizeField as keyof typeof resolvedData[0], sizeConfig);
  } catch (error) {
    console.error(`Error fetching ${entityType.toLowerCase()} orientations:`, error);
    return { ...EMPTY_ORIENTATION_DATA };
  }
}

export async function getPartyOrientations(periodId: number): Promise<OrientationData> {
  return fetchOrientationData<PartyPeriod>('Party', periodId, 'political_strength', {
    baseSize: SCALING_CONFIG.PARTY_BASE_SIZE,
    scaleFactor: SCALING_CONFIG.PARTY_SCALE_FACTOR,
    maxSize: SCALING_CONFIG.PARTY_MAX_SIZE
  });
}

export async function getPopOrientations(periodId: number): Promise<OrientationData> {
  return fetchOrientationData<PopPeriod>('Pop', periodId, 'pop_size', {
    baseSize: SCALING_CONFIG.POP_BASE_SIZE,
    scaleFactor: SCALING_CONFIG.POP_SCALE_FACTOR,
    maxSize: SCALING_CONFIG.POP_MAX_SIZE
  });
}

const ELECTION_COLORS = [
  '#3182ce', // accent
  '#38a169', // success
  '#1a1a1a', // dark
  '#525252', // dark-alt
  '#8B5CF6', // purple
  '#F59E0B', // orange
  '#DC2626', // red
  '#059669', // emerald
  '#7C3AED', // violet
  '#D97706'  // amber
];

export function processElectionResults(results: EnrichedElectionResult[]): ElectionBarData {
  // Calculate voter turnout (100% - Non-Voters percentage)
  const nonVotersResult = results.find(r => r.party_id === -1);
  const nonVotersPercentage = nonVotersResult?.percentage || 0;
  const voterTurnout = 100 - nonVotersPercentage;
  
  // Filter to include actual parties and Small Parties, exclude Non-Voters (-1)
  const validResults = results.filter(r => r.party_id > 0 || r.party_id === -2);
  
  // Separate regular parties from Misc.Parties
  const regularParties = validResults.filter(r => r.party_id > 0);
  const miscParties = validResults.filter(r => r.party_id === -2);
  
  // Sort regular parties by percentage descending
  const sortedRegularParties = regularParties.sort((a, b) => (b.percentage || 0) - (a.percentage || 0));
  
  // Combine: regular parties first, then Misc.Parties at the end
  const finalResults = [...sortedRegularParties, ...miscParties];

  return {
    x: finalResults.map(r => r.party_name),
    y: finalResults.map(r => r.percentage || 0),
    text: finalResults.map(r => `${(r.percentage || 0).toFixed(1)}%`), // Only show percentage
    colors: finalResults.map(r => r.party_color || "#525252"), // Use actual party colors
    voterTurnout: voterTurnout
  };
}