<script lang="ts">
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import Button from '../../components/ui/Button.svelte';
	import Input from '../../components/inputs/Input.svelte';
	import BarGraph from '../../components/plots/BarGraph.svelte';
	import { API, type Period } from '../../lib/api/core';
	import { ELECTION_FIELD_META } from '../../lib/fieldMeta';
	import { runElectionSimulation, getEnrichedElectionResults, type SimulationResult, type EnrichedElectionResult } from '../../lib/api/data_services/simulation';
	import { onMount } from 'svelte';

	// State
	let periods = $state<Period[]>([]);
	let selectedPeriod = $state('');
	let seats = $state<number>(ELECTION_FIELD_META.seats.defaultValue!);
	let threshold = $state<number>(ELECTION_FIELD_META.threshold.defaultValue!);
	let simulationResult = $state<SimulationResult | null>(null);
	let electionResults = $state<EnrichedElectionResult[]>([]);
	let loading = $state(false);
	let loadingResults = $state(false);
	let error = $state<string | null>(null);

	// Derived values
	const periodOptionsArray = $derived(periods.map(p => ({ 
		title: p.year.toString(), 
		value: p.id?.toString() || '' 
	})));


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
		} catch (err) {
			electionResults = [];
		} finally {
			loadingResults = false;
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
			
			// Run simulation
			const simResult = await runElectionSimulation(periodId, seats, threshold);
			if (!simResult.success) {
				throw new Error(simResult.error || 'Simulation failed');
			}
			simulationResult = simResult.data!;
			
			// Get updated election results
			await loadExistingResults(periodId);
			
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
</script>

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
	<Container title="Results">
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
						<BarGraph {electionResults} {threshold} />
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
	<Container title="Seats">
		
	</Container>
</Grid>