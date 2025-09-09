<script lang="ts">
	import { onMount } from 'svelte';
	import { API, type Period, type ElectionResult, type Party } from '../../lib/api/core';
	import Grid from '../ui/Grid.svelte';

	// Types
	interface EnrichedElectionResult extends ElectionResult {
		party_name: string;
		party_color: string;
	}

	interface PeriodData {
		period: Period;
		electionResults: EnrichedElectionResult[];
	}

	// Component state
	let data = $state<PeriodData[]>([]);
	let loading = $state(false);
	let error = $state('');

	// Constants
	const DEFAULT_PARTY_COLOR = '#525252';
	const MESSAGES = {
		LOADING: 'Loading government data...',
		ERROR: 'Failed to load government composition data',
		NO_GOVERNMENT: 'No government formed',
		NO_OPPOSITION: 'No opposition parties'
	} as const;

	// Data fetching functions
	async function fetchPeriods(): Promise<Period[]> {
		const response = await API.getAll<Period>('Period');
		if (!response.success || !response.data) {
			throw new Error(response.error || 'Failed to load periods');
		}
		return response.data.sort((a, b) => (b.year || 0) - (a.year || 0));
	}

	async function fetchParties(): Promise<Party[]> {
		const response = await API.getAll<Party>('Party');
		if (!response.success || !response.data) {
			throw new Error(response.error || 'Failed to load parties');
		}
		return response.data;
	}

	async function fetchElectionResults(periodId: number): Promise<ElectionResult[]> {
		const response = await API.getAll<ElectionResult>('ElectionResult', 0, 100, undefined, undefined, { period_id: periodId });
		return response.success && response.data ? response.data : [];
	}

	// Data processing functions
	function enrichElectionResults(results: ElectionResult[], parties: Party[]): EnrichedElectionResult[] {
		return results.map(result => {
			const party = parties.find(p => p.id === result.party_id);
			return {
				...result,
				party_name: party?.name || `Party ${result.party_id}`,
				party_color: party?.color || DEFAULT_PARTY_COLOR
			};
		});
	}

	function getGovernmentParties(results: EnrichedElectionResult[]): EnrichedElectionResult[] {
		return results
			.filter(result => result.in_government === true)
			.sort((a, b) => (b.seats || 0) - (a.seats || 0));
	}

	function getOppositionParties(results: EnrichedElectionResult[]): EnrichedElectionResult[] {
		return results
			.filter(result => result.in_parliament === true && result.in_government === false)
			.sort((a, b) => (b.seats || 0) - (a.seats || 0));
	}

	function getPartyTooltip(party: EnrichedElectionResult): string {
		const baseInfo = `${party.party_name}: ${party.seats} seats (${party.percentage?.toFixed(1)}%)`;
		const govInfo = party.head_of_government ? ' • Head of Government' : '';
		return baseInfo + govInfo;
	}

	// Main data fetching function
	async function fetchAllData(): Promise<PeriodData[]> {
		const [periods, parties] = await Promise.all([fetchPeriods(), fetchParties()]);
		
		const periodDataPromises = periods.map(async (period): Promise<PeriodData> => {
			const electionResults = await fetchElectionResults(period.id!);
			const enrichedResults = enrichElectionResults(electionResults, parties);
			
			return {
				period,
				electionResults: enrichedResults
			};
		});

		return Promise.all(periodDataPromises);
	}

	// Load data with error handling
	async function loadData(): Promise<void> {
		loading = true;
		error = '';

		try {
			data = await fetchAllData();
		} catch (err) {
			error = err instanceof Error ? err.message : MESSAGES.ERROR;
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<!-- Loading State -->
{#if loading}
	<div class="flex items-center justify-center p-8">
		<div class="text-light-alt">{MESSAGES.LOADING}</div>
	</div>

<!-- Error State -->
{:else if error}
	<div class="flex items-center justify-center p-8">
		<div class="text-failure">Error: {error}</div>
	</div>

<!-- Main Content -->
{:else}
	<div class="space-y-6">
		{#each data as periodData (periodData.period.id)}
			{@const governmentParties = getGovernmentParties(periodData.electionResults)}
			{@const oppositionParties = getOppositionParties(periodData.electionResults)}
			
			<!-- Period Card -->
			<div class="p-4 border rounded-lg shadow-sm bg-light border-light-alt">
				<Grid cols="1fr 4fr 4fr">
					
					<!-- Period Year Column -->
					<div class="flex items-center justify-center">
						<div class="p-4 text-center text-dark-alt">
							<div class="text-2xl font-bold">{periodData.period.year}</div>
						</div>
					</div>

					<!-- Government Parties Column -->
					<div class="px-4">
						<h3 class="pb-2 mb-3 font-semibold text-center border-b text-dark border-light-alt">
							Government
						</h3>
						
						{#if governmentParties.length > 0}
							<div class="flex w-full h-16 overflow-hidden border rounded border-light-alt">
								{#each governmentParties as party (party.id)}
									<div 
										class="relative flex flex-col items-center justify-center px-2 font-medium transition-all cursor-pointer text-md hover:brightness-110 min-w-12"
										style="flex: {party.seats || 1}; background-color: {party.party_color}"
										title={getPartyTooltip(party)}
									>
										<div class="px-2 py-1 font-semibold text-center truncate rounded text-md bg-light text-dark">
											{party.party_name} ({party.seats})
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="py-4 text-center text-light-alt">{MESSAGES.NO_GOVERNMENT}</div>
						{/if}
					</div>

					<!-- Opposition Parties Column -->
					<div class="px-4">
						<h3 class="pb-2 mb-3 font-semibold text-center border-b text-dark border-light-alt">
							Parliament (Opposition)
						</h3>
						
						{#if oppositionParties.length > 0}
							<div class="flex w-full h-16 overflow-hidden border rounded border-light-alt">
								{#each oppositionParties as party (party.id)}
									<div 
										class="relative flex flex-col items-center justify-center px-2 text-sm font-medium transition-all cursor-pointer hover:brightness-110 min-w-12"
										style="flex: {party.seats || 1}; background-color: {party.party_color}"
										title={getPartyTooltip(party)}
									>
										<div class="px-2 py-1 font-semibold text-center truncate rounded text-md bg-light text-dark">
											{party.party_name} ({party.seats})
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="py-4 text-center text-light-alt">{MESSAGES.NO_OPPOSITION}</div>
						{/if}
					</div>
					
				</Grid>
			</div>
		{/each}
	</div>
{/if}