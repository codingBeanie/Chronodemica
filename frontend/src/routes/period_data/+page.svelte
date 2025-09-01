<script lang="ts">
	import ContentHeader from '../../components/ui/ContentHeader.svelte';
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import Button from '../../components/ui/Button.svelte';
	import { API, type Period, type Pop, type Party, type PopPeriod, type PartyPeriod } from '../../api/api';
	import { onMount } from 'svelte';

	let periods = $state<Period[]>([]);
	let selectedPeriod = $state('');
	let selectedDataModel = $state('Population');
	let pops = $state<Pop[]>([]);
	let parties = $state<Party[]>([]);
	let selectedObject = $state('');
	let periodData = $state<PopPeriod | PartyPeriod | null>(null);
	let previousPeriod = $state<Period | null>(null);
	let previousData = $state<PopPeriod | PartyPeriod | null>(null);
	
	onMount(async () => {
		const [periodResult, popResult, partyResult] = await Promise.all([
			API.getAll<Period>('Period', 0, 100, 'year', 'descending'),
			API.getAll<Pop>('Pop', 0, 100, 'name', 'ascending'),
			API.getAll<Party>('Party', 0, 100, 'name', 'ascending')
		]);
		
		if (periodResult.success && periodResult.data) {
			periods = periodResult.data;
			if (periods.length > 0) {
				selectedPeriod = periods[0].id?.toString() || '';
			}
		}
		
		if (popResult.success && popResult.data) {
			pops = popResult.data;
		}
		
		if (partyResult.success && partyResult.data) {
			parties = partyResult.data;
		}
		
		// Set initial selected object based on default data model
		if (selectedDataModel === 'Population' && pops.length > 0) {
			selectedObject = pops[0].id?.toString() || '';
		} else if (selectedDataModel === 'Party' && parties.length > 0) {
			selectedObject = parties[0].id?.toString() || '';
		}
	});

	let periodOptionsArray = $derived(periods.map(period => ({
		title: period.year.toString(),
		value: period.id?.toString() || ''
	})));

	const dataModelOptions = {
		'Population': 'Population',
		'Party': 'Party'
	};

	let objectOptionsArray = $derived((() => {
		const objects = selectedDataModel === 'Population' ? pops : parties;
		return objects.map(obj => ({
			title: obj.name,
			value: obj.id?.toString() || ''
		}));
	})());

	$effect(() => {
		// Reset selected object when data model changes
		const objects = selectedDataModel === 'Population' ? pops : parties;
		if (objects.length > 0) {
			selectedObject = objects[0].id?.toString() || '';
		}
	});

	$effect(() => {
		// Update previous period when selected period changes
		if (selectedPeriod && periods.length > 0) {
			const currentPeriod = periods.find(p => p.id?.toString() === selectedPeriod);
			if (currentPeriod) {
				// Find period with year immediately before current period's year
				const sortedPeriods = periods.sort((a, b) => b.year - a.year); // descending by year
				const currentIndex = sortedPeriods.findIndex(p => p.id?.toString() === selectedPeriod);
				
				// Previous period is the next one in the descending list (lower year)
				if (currentIndex !== -1 && currentIndex < sortedPeriods.length - 1) {
					previousPeriod = sortedPeriods[currentIndex + 1];
				} else {
					previousPeriod = null;
				}
			}
		} else {
			previousPeriod = null;
		}
	});

	$effect(() => {
		// Update period data when period, data model, or object changes
		if (selectedPeriod && selectedObject) {
			const periodId = parseInt(selectedPeriod);
			const objectId = parseInt(selectedObject);
			
			const fetchData = async () => {
				if (selectedDataModel === 'Population') {
					const result = await API.getAll<PopPeriod>('PopPeriod', 0, 1, undefined, undefined, {
						period_id: periodId,
						pop_id: objectId
					});
					periodData = result.success && result.data && result.data.length > 0 ? result.data[0] : null;
				} else {
					const result = await API.getAll<PartyPeriod>('PartyPeriod', 0, 1, undefined, undefined, {
						period_id: periodId,
						party_id: objectId
					});
					periodData = result.success && result.data && result.data.length > 0 ? result.data[0] : null;
				}
			};
			
			fetchData();
		}
	});

	$effect(() => {
		// Update previous data when previous period, data model, or object changes
		if (previousPeriod && selectedObject) {
			const previousPeriodId = previousPeriod.id;
			const objectId = parseInt(selectedObject);
			
			const fetchPreviousData = async () => {
				if (selectedDataModel === 'Population') {
					const result = await API.getAll<PopPeriod>('PopPeriod', 0, 1, undefined, undefined, {
						period_id: previousPeriodId,
						pop_id: objectId
					});
					previousData = result.success && result.data && result.data.length > 0 ? result.data[0] : null;
				} else {
					const result = await API.getAll<PartyPeriod>('PartyPeriod', 0, 1, undefined, undefined, {
						period_id: previousPeriodId,
						party_id: objectId
					});
					previousData = result.success && result.data && result.data.length > 0 ? result.data[0] : null;
				}
			};
			
			fetchPreviousData();
		} else {
			// No previous period or no selected object
			previousData = null;
		}
	});

	/**
	 * Creates a new period data entry with backend default values
	 * @param dataModel - 'Population' or 'Party' 
	 * @param objectId - The ID of the Pop or Party
	 * @param periodId - The ID of the Period
	 * @returns Promise with the created entry or null if failed
	 */
	async function createEmptyPeriodData(dataModel: string, objectId: number, periodId: number): Promise<PopPeriod | PartyPeriod | null> {
		try {
			if (dataModel === 'Population') {
				const result = await API.create<PopPeriod>('PopPeriod', {
					pop_id: objectId,
					period_id: periodId
				});
				return result.success && result.data ? result.data : null;
			} else {
				const result = await API.create<PartyPeriod>('PartyPeriod', {
					party_id: objectId,
					period_id: periodId
				});
				return result.success && result.data ? result.data : null;
			}
		} catch (error) {
			console.error('Error creating period data:', error);
			return null;
		}
	}
</script>

<ContentHeader title="Periodic Detail Data" />

<Grid cols="1fr">
	<!-- filter -->
	<Container>
		<Grid cols="2fr 1fr 2fr">
			<!--Period Selection-->
			<div>
				<SegmentedControl 
					label="Period Selection"
					optionsArray={periodOptionsArray}
					bind:selectedValue={selectedPeriod}
				/>
			</div>
			<!--Data Model Selection-->
			<div>
				<SegmentedControl 
					label="Data Model Selection"
					options={dataModelOptions}
					bind:selectedValue={selectedDataModel}
				/>
			</div>
			<!--Object Selection-->
			<div>
				<SegmentedControl 
					label="{selectedDataModel} Selection"
					optionsArray={objectOptionsArray}
					bind:selectedValue={selectedObject}
				/>
			</div>
		</Grid>
	</Container>
</Grid>
	
<Grid cols="3fr 1fr">
	<!-- parameters -->
	<Container>
		{#if periodData}
			<h3 class="text-lg font-semibold mb-4">Parameters</h3>
			<pre class="bg-light-alt p-4 rounded-lg overflow-auto text-sm">
{JSON.stringify(periodData, null, 2)}
			</pre>
		{:else}
			<div class="text-center">
				<p class="text-dark mb-4">No data found for the selected combination. Please select a creation method.</p>
				<div class="flex gap-4 justify-center">
					<Button 
						text="Create Empty" 
						theme="light"
						onclick={async () => {
							if (selectedPeriod && selectedObject) {
								const periodId = parseInt(selectedPeriod);
								const objectId = parseInt(selectedObject);
								
								const newData = await createEmptyPeriodData(selectedDataModel, objectId, periodId);
								if (newData) {
									// Update the current period data to show the newly created entry
									periodData = newData;
								}
							}
						}}
					/>
					<Button 
						text="Create from Previous" 
						theme="light"
						disabled={previousData === null}
						onclick={() => {}}
					/>
				</div>
			</div>
		{/if}
	</Container>
	
	<div class="flex flex-col gap-4">
		<!-- political compass -->
		<Container></Container>
		
		<!-- preview voting -->
		<Container></Container>
	</div>
</Grid>
