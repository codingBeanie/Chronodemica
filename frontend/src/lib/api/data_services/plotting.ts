import { API, type PopPeriod, type PartyPeriod, type Pop, type Party } from '../core';
import type { EnrichedElectionResult } from './simulation';
import { getVotingBehavior } from './simulation';

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
  fullNames: string[];
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
    fullNames: finalResults.map(r => r.party_full_name),
    voterTurnout: voterTurnout
  };
}

export interface LineGraphTrace {
  name: string;
  full_name: string;
  x: string[];
  y: (number | null)[];
  color: string;
  party_id: number;
}

export interface LineGraphData {
  traces: LineGraphTrace[];
  periods: string[];
}

interface Period {
  id: number;
  year: number;
}

interface PartyInfo {
  id: number;
  name: string;
  full_name?: string;
  color?: string;
  valid_from?: number;
  valid_until?: number;
}

// Helper function to fetch and sort periods
async function fetchSortedPeriods(): Promise<Period[]> {
  const periodsResponse = await API.getAll('Period');
  if (!periodsResponse.success || !periodsResponse.data) {
    throw new Error('Failed to fetch periods');
  }
  
  const periods = periodsResponse.data as Period[];
  return periods.sort((a, b) => a.year - b.year);
}

// Helper function to fetch parties
async function fetchParties(): Promise<PartyInfo[]> {
  const partiesResponse = await API.getAll('Party');
  if (!partiesResponse.success || !partiesResponse.data) {
    throw new Error('Failed to fetch parties');
  }
  
  return partiesResponse.data as PartyInfo[];
}

// Helper function to check if party was valid in a given period
function isPartyValidInPeriod(party: PartyInfo, period: Period): boolean {
  return (!party.valid_from || period.year >= party.valid_from) && 
         (!party.valid_until || period.year <= party.valid_until);
}

// Helper function to create party map for quick lookups
function createPartyMap(parties: PartyInfo[]): Map<string, PartyInfo> {
  const partyMap = new Map<string, PartyInfo>();
  parties.forEach(party => {
    partyMap.set(party.name, party);
  });
  return partyMap;
}

// Helper function to build trace for a party
function buildPartyTrace(party: PartyInfo, periods: Period[], getData: (period: Period, party: PartyInfo) => number | null): LineGraphTrace {
  const trace: LineGraphTrace = {
    name: party.name,
    full_name: party.full_name || party.name,
    x: [],
    y: [],
    color: party.color || '#525252',
    party_id: party.id
  };
  
  for (const period of periods) {
    if (!isPartyValidInPeriod(party, period)) {
      console.log(`buildPartyTrace - ${party.name} not valid in ${period.year}, skipping`);
      continue;
    }
    
    trace.x.push(period.year.toString());
    const value = getData(period, party);
    trace.y.push(value);
    
    console.log(`buildPartyTrace - ${party.name} in ${period.year}: ${value !== null ? value + '%' : 'null (gap)'}`);
  }
  
  return trace;
}

export async function getPartyResultsOverTime(partyId?: number): Promise<LineGraphData> {
  try {
    console.log('getPartyResultsOverTime - Starting fetch for partyId:', partyId);
    
    // Fetch periods and parties
    const [sortedPeriods, allParties] = await Promise.all([
      fetchSortedPeriods(),
      fetchParties()
    ]);
    
    console.log('getPartyResultsOverTime - Sorted periods:', sortedPeriods);
    
    const parties = partyId ? allParties.filter(p => p.id === partyId) : allParties;
    console.log('getPartyResultsOverTime - Parties to process:', parties.map(p => `${p.name} (id: ${p.id})`));
    
    // Fetch election results for all periods
    const periodElectionData: { [periodId: number]: any[] } = {};
    
    for (const period of sortedPeriods) {
      console.log(`getPartyResultsOverTime - Fetching results for period ${period.id} (${period.year})`);
      const resultsResponse = await API.getAll('ElectionResult', 0, 100, undefined, undefined, { period_id: period.id });
      
      periodElectionData[period.id] = resultsResponse.success && resultsResponse.data ? resultsResponse.data : [];
      console.log(`getPartyResultsOverTime - Period ${period.year}: ${periodElectionData[period.id].length} results`);
    }
    
    // Build traces
    const traces: LineGraphTrace[] = [];
    
    for (const party of parties) {
      console.log(`getPartyResultsOverTime - Processing party: ${party.name} (id: ${party.id})`);
      
      const trace = buildPartyTrace(party, sortedPeriods, (period, party) => {
        const periodResults = periodElectionData[period.id] || [];
        const partyResult = periodResults.find((result: any) => result.party_id === party.id);
        return partyResult ? (partyResult.percentage || 0) : null;
      });
      
      if (trace.x.length > 0) {
        traces.push(trace);
        console.log(`getPartyResultsOverTime - Added trace for ${party.name} with ${trace.x.length} data points:`, trace.y);
      }
    }
    
    console.log('getPartyResultsOverTime - Final traces summary:', traces.map(t => `${t.name}: [${t.y.join(', ')}]`));
    
    return {
      traces: traces,
      periods: sortedPeriods.map(p => p.year.toString())
    };
  } catch (error) {
    console.error('Error fetching party results over time:', error);
    return { traces: [], periods: [] };
  }
}

export async function getPopulationVotingBehavior(popId: number): Promise<LineGraphData> {
  try {
    console.log('getPopulationVotingBehavior - Starting fetch for popId:', popId);
    
    // Fetch periods and parties
    const [sortedPeriods, allParties] = await Promise.all([
      fetchSortedPeriods(),
      fetchParties()
    ]);
    
    console.log('getPopulationVotingBehavior - Sorted periods:', sortedPeriods);
    
    // Create party map for quick lookups
    const partyMap = createPartyMap(allParties);
    console.log('getPopulationVotingBehavior - Party mapping created:', Array.from(partyMap.keys()));
    
    // Fetch voting behavior data for all periods
    const periodVotingBehaviorData: { [periodId: number]: any[] } = {};
    
    for (const period of sortedPeriods) {
      console.log(`getPopulationVotingBehavior - Fetching voting behavior for period ${period.id} (${period.year})`);
      const behaviorResponse = await getVotingBehavior(period.id, popId);
      
      periodVotingBehaviorData[period.id] = behaviorResponse.success && behaviorResponse.data ? behaviorResponse.data : [];
      console.log(`getPopulationVotingBehavior - Period ${period.year}: ${periodVotingBehaviorData[period.id].length} voting behavior entries`);
    }
    
    // Extract unique parties from voting behavior data
    const allPartyNames = new Set<string>();
    Object.values(periodVotingBehaviorData).forEach(periodData => {
      periodData.forEach((entry: any) => {
        if (entry.party_name) {
          allPartyNames.add(entry.party_name);
        }
      });
    });
    
    console.log('getPopulationVotingBehavior - Unique parties found:', Array.from(allPartyNames));
    
    // Build traces
    const traces: LineGraphTrace[] = [];
    
    for (const partyName of allPartyNames) {
      console.log(`getPopulationVotingBehavior - Processing party: ${partyName}`);
      
      const partyInfo = partyMap.get(partyName);
      const fakeParty: PartyInfo = {
        id: partyInfo?.id || 0,
        name: partyName,
        full_name: partyInfo?.full_name || partyName,
        color: partyInfo?.color,
        valid_from: partyInfo?.valid_from,
        valid_until: partyInfo?.valid_until
      };
      
      const trace = buildPartyTrace(fakeParty, sortedPeriods, (period, party) => {
        const periodData = periodVotingBehaviorData[period.id] || [];
        const partyBehavior = periodData.find((entry: any) => entry.party_name === party.name);
        return (partyBehavior && partyBehavior.percentage !== undefined) ? (partyBehavior.percentage || 0) : null;
      });
      
      if (trace.x.length > 0) {
        traces.push(trace);
        console.log(`getPopulationVotingBehavior - Added trace for ${partyName} with ${trace.x.length} data points:`, trace.y);
      }
    }
    
    console.log('getPopulationVotingBehavior - Final traces summary:', traces.map(t => `${t.name}: [${t.y.join(', ')}]`));
    
    return {
      traces: traces,
      periods: sortedPeriods.map(p => p.year.toString())
    };
  } catch (error) {
    console.error('Error fetching population voting behavior:', error);
    return { traces: [], periods: [] };
  }
}

// Generic colors for population composition visualization
const POPULATION_COLORS = [
  '#3182ce', // blue
  '#38a169', // green  
  '#e53e3e', // red
  '#d69e2e', // yellow
  '#8b5cf6', // purple
  '#f56565', // light red
  '#4fd1c7', // teal
  '#f6ad55', // orange
  '#9f7aea', // light purple
  '#68d391', // light green
  '#f687b3', // pink
  '#4299e1', // light blue
] as const;

export async function getPopulationComposition(): Promise<LineGraphData> {
  try {
    console.log('getPopulationComposition - Starting fetch for all population sizes over time');
    
    // Fetch periods and populations
    const [sortedPeriods, allPops] = await Promise.all([
      fetchSortedPeriods(),
      fetchPops()
    ]);
    
    console.log('getPopulationComposition - Sorted periods:', sortedPeriods);
    console.log('getPopulationComposition - Populations available:', allPops.map(p => `${p.name} (id: ${p.id})`));
    
    // Fetch population period data for all periods
    const periodPopData: { [periodId: number]: any[] } = {};
    
    for (const period of sortedPeriods) {
      console.log(`getPopulationComposition - Fetching pop data for period ${period.id} (${period.year})`);
      const popResponse = await API.getAll('PopPeriod', 0, 100, undefined, undefined, { period_id: period.id });
      
      periodPopData[period.id] = popResponse.success && popResponse.data ? popResponse.data : [];
      console.log(`getPopulationComposition - Period ${period.year}: ${periodPopData[period.id].length} pop period entries`);
    }
    
    // Build traces for each population
    const traces: LineGraphTrace[] = [];
    
    allPops.forEach((pop, index) => {
      console.log(`getPopulationComposition - Processing population: ${pop.name} (id: ${pop.id})`);
      
      // Assign color from the palette, cycling through if more pops than colors
      const colorIndex = index % POPULATION_COLORS.length;
      const assignedColor = POPULATION_COLORS[colorIndex];
      
      const fakeParty: PartyInfo = {
        id: pop.id,
        name: pop.name,
        full_name: pop.name, // For populations, name and full_name are the same
        color: assignedColor,
        valid_from: undefined,
        valid_until: undefined
      };
      
      const trace = buildPartyTrace(fakeParty, sortedPeriods, (period, party) => {
        const periodData = periodPopData[period.id] || [];
        const popData = periodData.find((entry: any) => entry.pop_id === party.id);
        return (popData && popData.pop_size !== undefined) ? (popData.pop_size || 0) : null;
      });
      
      if (trace.x.length > 0) {
        traces.push(trace);
        console.log(`getPopulationComposition - Added trace for ${pop.name} with color ${assignedColor} and ${trace.x.length} data points:`, trace.y);
      }
    });
    
    console.log('getPopulationComposition - Final traces summary:', traces.map(t => `${t.name}: [${t.y.join(', ')}]`));
    
    return {
      traces: traces,
      periods: sortedPeriods.map(p => p.year.toString())
    };
  } catch (error) {
    console.error('Error fetching population composition:', error);
    return { traces: [], periods: [] };
  }
}

// Helper function to fetch populations (similar to fetchParties)
async function fetchPops(): Promise<Array<{ id: number; name: string; color?: string }>> {
  const popsResponse = await API.getAll('Pop');
  if (!popsResponse.success || !popsResponse.data) {
    throw new Error('Failed to fetch populations');
  }
  
  return popsResponse.data as Array<{ id: number; name: string; color?: string }>;
}