<script lang="ts">
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import Button from '../../components/ui/Button.svelte';
	import ParameterEdit from '../../components/builder/ParameterEdit.svelte';
	import { API, type Period, type Pop, type Party, type PopPeriod, type PartyPeriod } from '../../api/api';
	import { onMount } from 'svelte';

	type DataModel = 'Population' | 'Party';
	type PeriodData = PopPeriod | PartyPeriod;

	// State
	let periods = $state<Period[]>([]);
	let pops = $state<Pop[]>([]);
	let parties = $state<Party[]>([]);
	let selectedPeriod = $state('');
	let selectedDataModel = $state<DataModel>('Population');
	let selectedObject = $state('');
	let periodData = $state<PeriodData | null>(null);
	let previousPeriod = $state<Period | null>(null);
	let previousData = $state<PeriodData | null>(null);
	let unsavedChanges = $state(false);
	let selectedPeriodYear = $state<string>(''); 
	let selectedObjectName = $state<string>('');  

	// Derived values
	let periodOptionsArray = $derived(periods.map(p => ({ 
		title: p.year.toString(), 
		value: p.id?.toString() || '' 
	})));

	let currentObjects = $derived(selectedDataModel === 'Population' ? pops : parties);
	let objectOptionsArray = $derived(currentObjects.map(obj => ({ 
		title: obj.name, 
		value: obj.id?.toString() || '' 
	})));

	// Constants
	const dataModelOptions = { 'Population': 'Population', 'Party': 'Party' };

	// Utility functions
	function getFirstObjectId(objects: (Pop | Party)[]): string {
		return objects.length > 0 ? objects[0].id?.toString() || '' : '';
	}

	function findPreviousPeriod(currentPeriodId: string, allPeriods: Period[]): Period | null {
		const sortedPeriods = [...allPeriods].sort((a, b) => b.year - a.year);
		const currentIndex = sortedPeriods.findIndex(p => p.id?.toString() === currentPeriodId);
		return currentIndex !== -1 && currentIndex < sortedPeriods.length - 1 
			? sortedPeriods[currentIndex + 1] 
			: null;
	}

	async function fetchPeriodData(
		dataModel: DataModel, 
		periodId: number, 
		objectId: number
	): Promise<PeriodData | null> {
		const modelName = dataModel === 'Population' ? 'PopPeriod' : 'PartyPeriod';
		const filterKey = dataModel === 'Population' ? 'pop_id' : 'party_id';
		
		const result = await API.getAll(
			modelName as any, 
			0, 1, undefined, undefined, 
			{ period_id: periodId, [filterKey]: objectId }
		);
		
		return result.success && result.data && result.data.length > 0 ? result.data[0] as PeriodData : null;
	}

	async function createPeriodData(
		dataModel: DataModel,
		objectId: number,
		periodId: number,
		sourceData?: PeriodData | null
	): Promise<PeriodData | null> {
		try {
			const modelName = dataModel === 'Population' ? 'PopPeriod' : 'PartyPeriod';
			const objectIdKey = dataModel === 'Population' ? 'pop_id' : 'party_id';
			
			let baseData: any = {
				[objectIdKey]: objectId,
				period_id: periodId
			};

			if (sourceData) {
				const { id, period_id: _, ...previousValues } = sourceData;
				baseData = { ...previousValues, ...baseData };
			}

			const result = await API.create(modelName as any, baseData);
			return result.success && result.data ? result.data as PeriodData : null;
		} catch (error) {
			console.error('Error creating period data:', error);
			return null;
		}
	}

	async function handleCreatePeriodData(withPreviousData = false) {
		if (!selectedPeriod || !selectedObject) return;
		
		const periodId = parseInt(selectedPeriod);
		const objectId = parseInt(selectedObject);
		const sourceData = withPreviousData ? previousData : null;
		
		const newData = await createPeriodData(selectedDataModel, objectId, periodId, sourceData);
		if (newData) {
			periodData = newData;
		}
	}

	// Load initial data
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
		if (popResult.success && popResult.data) pops = popResult.data;
		if (partyResult.success && partyResult.data) parties = partyResult.data;
		
		selectedObject = getFirstObjectId(currentObjects);
	});

	// Reset object selection when data model changes
	$effect(() => {
		selectedObject = getFirstObjectId(currentObjects);
	});

	// Combined: Previous period calculation + previous data fetch
	$effect(() => {
		const prevPeriod = selectedPeriod && periods.length > 0 
			? findPreviousPeriod(selectedPeriod, periods) 
			: null;
		
		previousPeriod = prevPeriod;
		
		if (prevPeriod && selectedObject) {
			fetchPeriodData(selectedDataModel, prevPeriod.id!, parseInt(selectedObject))
				.then(data => previousData = data);
		} else {
			previousData = null;
		}
	});

	// Combined: Current data fetch + display values update
	$effect(() => {
		if (selectedPeriod && selectedObject) {
			unsavedChanges = false;
			
			// Fetch current period data
			fetchPeriodData(selectedDataModel, parseInt(selectedPeriod), parseInt(selectedObject))
				.then(data => periodData = data);
			
			// Update display values
			selectedPeriodYear = periods.find(p => p.id?.toString() === selectedPeriod)?.year.toString() || '0';
			selectedObjectName = currentObjects.find(obj => obj.id?.toString() === selectedObject)?.name || 'Unknown';
		}
	});
</script>

	
<Grid cols="1fr 5fr 2fr">
	<!-- filter -->
	<Container title="Filter">
		<Grid cols="1fr">
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

	<!-- parameters -->
	<Container title="({selectedPeriodYear}) {selectedObjectName}">
		{#if periodData}
			<ParameterEdit 
				bind:data={periodData} 
				bind:unsavedChanges={unsavedChanges}
				objectName={selectedObjectName}
				periodYear={parseInt(selectedPeriodYear) || 0}
			/>
		{:else}
			<div class="text-center">
				<p class="text-dark mb-4">No data found for the selected combination. Please select a creation method.</p>
				<div class="flex gap-4 justify-center">
					<Button 
						text="Create Empty" 
						theme="light"
						onclick={() => handleCreatePeriodData(false)}
					/>
					<Button 
						text="Create from Previous" 
						theme="light"
						disabled={previousData === null}
						onclick={() => handleCreatePeriodData(true)}
					/>
				</div>
			</div>
		{/if}
	</Container>
	
	<div class="flex flex-col gap-4">
		<!-- political compass -->
		<Container>
			<p class="text-sm text-lightText">Political compass visualization placeholder</p>
		</Container>
		
		<!-- preview voting -->
		<Container>
			<p class="text-sm text-lightText">Preview voting visualization placeholder</p>
		</Container>
	</div>
</Grid>
