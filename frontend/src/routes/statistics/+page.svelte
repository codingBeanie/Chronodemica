<script lang="ts">
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import LineGraph from '../../components/plots/LineGraph.svelte';
	import GovernmentList from '../../components/builder/GovernmentList.svelte';
	import { API } from '../../lib/api/core';
	import { onMount } from 'svelte';

	// Types
	interface Pop {
		id: number;
		name: string;
	}

	// Configuration hashmap for the main statistics options
	const statisticOptions = {
		'Party Results': 'party_results',
		'Population Votes': 'population_votes',
		'Population Composition': 'population_composition',
		'Governments': 'governments'
	};

	// State
	let selectedStatistic = $state('party_results');
	let pops = $state<Pop[]>([]);
	let selectedPop = $state('');

	// Fetch all populations
	async function fetchPops() {
		const response = await API.getAll('Pop');
		if (response.success && response.data) {
			pops = response.data as Pop[];
		}
	}

	// Create pop options hashmap (no 'All' option for population votes)
	let popOptions = $derived(() => {
		const options: Record<string, string> = {};
		pops.forEach((pop) => {
			options[pop.name] = pop.id.toString();
		});
		return options;
	});

	// Set first pop as default when pops are loaded
	$effect(() => {
		if (pops.length > 0 && !selectedPop) {
			selectedPop = pops[0].id.toString();
		}
	});

	onMount(() => {
		fetchPops();
	});
</script>

<Grid cols="1fr 7fr">
	<!-- Selection Container -->
	<Container title="Selection">
		<SegmentedControl 
			label="Statistic"
			options={statisticOptions}
			bind:selectedValue={selectedStatistic}
		/>


		{#if selectedStatistic === 'population_votes' && pops.length > 0}
			<SegmentedControl 
				label="Population"
				options={popOptions()}
				bind:selectedValue={selectedPop}
			/>
		{/if}
	</Container>

	<!-- Main Content Area -->
	<div>
		{#if selectedStatistic === 'party_results'}
			<Container title="Party Results Over Time">
				<LineGraph />
			</Container>
		{:else if selectedStatistic === 'population_votes'}
			<Container title="[{selectedPop && pops.find(p => p.id.toString() === selectedPop)?.name || ''}] Population Voting Behavior ">
				{#if selectedPop && pops.find(p => p.id.toString() === selectedPop)}
					<LineGraph mode="population" popId={parseInt(selectedPop)} />
				{:else}
					<p class="text-light-alt">Please select a population to view voting behavior.</p>
				{/if}
			</Container>
		{:else if selectedStatistic === 'population_composition'}
			<Container title="Population Composition">
				<LineGraph mode="composition" />
			</Container>
		{:else if selectedStatistic === 'governments'}
			<Container title="Government Composition">
				<GovernmentList />
			</Container>
		{/if}
	</div>
</Grid>
