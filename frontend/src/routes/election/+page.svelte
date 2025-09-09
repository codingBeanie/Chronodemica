<script lang="ts">
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import Button from '../../components/ui/Button.svelte';
	import Input from '../../components/inputs/Input.svelte';
	import BarGraph from '../../components/plots/BarGraph.svelte';
	import Table from '../../components/ui/Table.svelte';
	import Column from '../../components/ui/Column.svelte';
	import CoalitionsChoice from '../../components/builder/CoalitionsChoice.svelte';
	import { API, type Period } from '../../lib/api/core';
	import { ELECTION_FIELD_META } from '../../lib/fieldMeta';
	import { runElectionSimulation, getEnrichedElectionResults, type SimulationResult, type EnrichedElectionResult } from '../../lib/api/data_services/simulation';
	import { onMount } from 'svelte';

	// State
	let periods = $state<Period[]>([]);
	let selectedPeriod = $state('');
	let seats = $state<number>(getInitialSeats());
	let threshold = $state<number>(ELECTION_FIELD_META.threshold.defaultValue!);
	let simulationResult = $state<SimulationResult | null>(null);
	let electionResults = $state<EnrichedElectionResult[]>([]);
	let previousElectionResults = $state<EnrichedElectionResult[] | null>(null);
	let loading = $state(false);
	let loadingResults = $state(false);
	let error = $state<string | null>(null);
	let coalitionsTrigger = $state(0);

	// Helper functions for seat memory
	function getInitialSeats(): number {
		if (typeof window !== 'undefined') {
			const savedSeats = localStorage.getItem('chronodemica_last_seats');
			if (savedSeats) {
				const parsedSeats = parseInt(savedSeats);
				if (!isNaN(parsedSeats) && parsedSeats >= ELECTION_FIELD_META.seats.min && parsedSeats <= ELECTION_FIELD_META.seats.max) {
					return parsedSeats;
				}
			}
		}
		return ELECTION_FIELD_META.seats.defaultValue!;
	}

	function saveSeatsToStorage(seatsValue: number): void {
		if (typeof window !== 'undefined') {
			localStorage.setItem('chronodemica_last_seats', seatsValue.toString());
		}
	}

	// Derived values
	const periodOptionsArray = $derived(periods.map(p => ({ 
		title: p.year.toString(), 
		value: p.id?.toString() || '' 
	})));

	const selectedPeriodYear = $derived(() => {
		if (!selectedPeriod || !periods.length) return '';
		const period = periods.find(p => p.id?.toString() === selectedPeriod);
		return period ? period.year.toString() : '';
	});

	// Prepare seat distribution data for Table component
	const seatDistributionData = $derived(() => {
		if (!electionResults.length) return [];
		
		return electionResults
			.filter(result => result.seats && result.seats > 0 && result.party_id !== -1)
			.map(result => ({
				party_name: result.party_name,
				seats: result.seats,
				in_government: result.in_government,
				head_of_government: result.head_of_government,
				party_color: result.party_color
			}))
			.sort((a, b) => (b.seats || 0) - (a.seats || 0));
	});

	const seatDistributionHeaders = $derived(['party_name', 'seats']);


	// Helper functions
	async function loadExistingResults(periodId: number) {
		loadingResults = true;
		// Clear previous simulation state when loading new period
		error = null;
		simulationResult = null;
		
		try {
			const response = await getEnrichedElectionResults(periodId);
			if (response.success && response.data && response.data.length > 0) {
				electionResults = response.data;
			} else {
				electionResults = [];
			}
			
			// Load previous period results for comparison
			await loadPreviousPeriodResults(periodId);
		} catch (err) {
			electionResults = [];
			previousElectionResults = null;
		} finally {
			loadingResults = false;
		}
	}

	async function loadPreviousPeriodResults(currentPeriodId: number) {
		try {
			// Find the previous period (next higher year)
			const currentPeriod = periods.find(p => p.id === currentPeriodId);
			if (!currentPeriod) {
				previousElectionResults = null;
				return;
			}

			// Sort periods by year and find the previous one
			const sortedPeriods = [...periods].sort((a, b) => a.year - b.year);
			const currentIndex = sortedPeriods.findIndex(p => p.id === currentPeriodId);
			
			if (currentIndex > 0) {
				const previousPeriod = sortedPeriods[currentIndex - 1];
				const response = await getEnrichedElectionResults(previousPeriod.id!);
				
				if (response.success && response.data && response.data.length > 0) {
					previousElectionResults = response.data;
				} else {
					previousElectionResults = null;
				}
			} else {
				previousElectionResults = null;
			}
		} catch (err) {
			previousElectionResults = null;
		}
	}

	async function handleStartVoting() {
		if (!selectedPeriod) return;
		
		loading = true;
		error = null;
		simulationResult = null;
		electionResults = [];
		
		try {
			const periodId = parseInt(selectedPeriod);
			
			// Save seats value to storage
			saveSeatsToStorage(seats);
			
			// Run simulation
			const simResult = await runElectionSimulation(periodId, seats, threshold);
			if (!simResult.success) {
				throw new Error(simResult.error || 'Simulation failed');
			}
			simulationResult = simResult.data!;
			
			// Get updated election results
			await loadExistingResults(periodId);
			
			// Trigger coalitions update
			coalitionsTrigger++;
			
		} catch (err) {
			error = err instanceof Error ? err.message : 'An unexpected error occurred';
		} finally {
			loading = false;
		}
	}

	// Load initial data
	onMount(async () => {
		try {
			const periodResult = await API.getAll<Period>('Period', 0, 100, 'year', 'descending');

			if (periodResult.success && periodResult.data) {
				periods = periodResult.data;
				if (periods.length > 0) {
					selectedPeriod = periods[0].id?.toString() || '';
					// Load existing results for the initial period
					handlePeriodChange();
				}
			}
		} catch (err) {
			error = 'Failed to load periods';
		}
	});

	// Handle period changes explicitly without reactive effects to avoid loops
	function handlePeriodChange() {
		if (selectedPeriod && !loading) {
			const periodId = parseInt(selectedPeriod);
			if (!isNaN(periodId)) {
				loadExistingResults(periodId);
			}
		}
	}

	// Save seats value whenever it changes
	$effect(() => {
		saveSeatsToStorage(seats);
	});
</script>

<!-- Top row -->
<Grid cols="1fr 6fr 1fr">
	<!-- Selection -->
	<Container title="Selection">
		<div class="flex flex-col gap-4">
			<SegmentedControl 
				label="Period Selection"
				optionsArray={periodOptionsArray}
				bind:selectedValue={selectedPeriod}
				onchange={handlePeriodChange}
			/>
			<Input 
				id="seats"
				type="number"
				label="Seats"
				bind:value={seats}
				hint={ELECTION_FIELD_META.seats.hint}
			/>
			<Input 
				id="threshold"
				type="number"
				label="Threshold (%)"
				bind:value={threshold}
				hint={ELECTION_FIELD_META.threshold.hint}
			/>
			
			<Button 
				text={loading ? "Running..." : "Start Voting"}
				theme="accent"
				onclick={handleStartVoting}
			/>
		</div>
	</Container>

	<!-- Results -->
	 <Column>
	<Container title="Election {selectedPeriodYear()}">
		{#if loading}
			<div class="flex items-center justify-center p-8">
				<p class="text-dark">Running simulation...</p>
			</div>
		{:else if loadingResults}
			<div class="flex items-center justify-center p-8">
				<p class="text-dark">Loading results...</p>
			</div>
		{:else if error}
			<div class="bg-failure bg-opacity-10 border border-failure rounded-lg p-4">
				<p class="text-failure font-medium">Error:</p>
				<p class="text-failure text-sm">{error}</p>
			</div>
		{:else if simulationResult || electionResults.length > 0}
			<div class="space-y-6">
				<!-- Election Results -->
				{#if electionResults.length > 0}
					<div>
						<BarGraph {electionResults} {threshold} {previousElectionResults} />
					</div>
				{/if}
			</div>
		{:else}
			<div class="text-center p-8">
				<p class="text-lightText">
					{selectedPeriod ? 'No election results found for this period' : 'Select a period to view results'}
				</p>
			</div>
		{/if}
	</Container>
	<!-- Bottom row with coalitions -->

	<Container title="Government Formation">
		<CoalitionsChoice 
			periodId={selectedPeriod ? parseInt(selectedPeriod) : null}
			trigger={coalitionsTrigger}
			onGovernmentChange={() => selectedPeriod && loadExistingResults(parseInt(selectedPeriod))}
		/>
	</Container>
	</Column>
	
	<Container title="Seats">
		{#if loadingResults}
			<div class="flex items-center justify-center p-8">
				<p class="text-dark">Loading...</p>
			</div>
		{:else if seatDistributionData().length > 0}
			<Table 
				mode="simple"
				externalData={seatDistributionData()}
				externalHeaders={seatDistributionHeaders}
			/>
		{:else}
			<div class="text-center p-8">
				<p class="text-lightText">No seat distribution data available</p>
			</div>
		{/if}
	</Container>
</Grid>

