<script lang="ts">
	import Grid from '../../components/ui/Grid.svelte';
	import Container from '../../components/ui/Container.svelte';
	import Column from '../../components/ui/Column.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import Button from '../../components/ui/Button.svelte';
	import ParameterEdit from '../../components/builder/ParameterEdit.svelte';
	import Table from '../../components/ui/Table.svelte';
	import PoliticalCompass from '../../components/plots/PoliticalCompass.svelte';
	import ScoringCurve from '../../components/plots/ScoringCurve.svelte';
	import { API, type Period, type Pop, type Party, type PopPeriod, type PartyPeriod, type VotingBehavior } from '../../lib/api/core';
	import { getVotingBehavior } from '../../lib/api/data_services/simulation';
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
	let votingBehavior = $state<VotingBehavior[]>([]);
	let previousVotingBehavior = $state<VotingBehavior[]>([]);
	let refreshTrigger = $state<number>(0);
	let popSizeRatios = $state<any[]>([]);
	let previousPopSizeRatios = $state<any[]>([]);
	
	// Define headers for voting behavior table (filtered data - no IDs and votes)
	let votingBehaviorHeaders = $state<string[]>([
		'party_name', 
		'party_full_name',
		'distance', 
		'raw_score', 
		'strength', 
		'adjusted_score', 
		'percentage',
		'% change'
	]);  

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

	// Derived values for enhanced voting behavior with % change
	let enhancedVotingBehavior = $derived(
		previousVotingBehavior.length > 0 && votingBehavior.length > 0
			? calculatePercentageChanges(votingBehavior, previousVotingBehavior)
			: votingBehavior.map(vb => ({ ...vb, '% change': 'N/A' }))
	);

	// Derived values for enhanced pop size ratios with % change
	let enhancedPopSizeRatios = $derived(
		previousPopSizeRatios.length > 0 && popSizeRatios.length > 0
			? calculatePopSizeRatioChanges(popSizeRatios, previousPopSizeRatios)
			: popSizeRatios.map(psr => ({ ...psr, '% change': 'N/A' }))
	);

	// Utility functions
	function getFirstObjectId(objects: (Pop | Party)[]): string {
		return objects.length > 0 ? objects[0].id?.toString() || '' : '';
	}

	function calculatePercentageChanges(current: VotingBehavior[], previous: VotingBehavior[]): any[] {
		// Create a map of previous percentages by party name for quick lookup
		const previousMap = new Map<string, number>();
		previous.forEach(prev => {
			previousMap.set(prev.party_name, prev.percentage);
		});

		// Add % change to current voting behavior data
		return current.map(curr => {
			const prevPercentage = previousMap.get(curr.party_name);
			const percentageChange = prevPercentage !== undefined 
				? (curr.percentage - prevPercentage)
				: null;

			return {
				...curr,
				'% change': percentageChange !== null 
					? `${percentageChange >= 0 ? '+' : ''}${percentageChange.toFixed(1)}%`
					: 'N/A'
			};
		});
	}

	function calculatePopSizeRatioChanges(current: any[], previous: any[]): any[] {
		// Create a map of previous ratios by pop name for quick lookup
		const previousMap = new Map<string, number>();
		previous.forEach(prev => {
			// Try different possible field names for the ratio value
			const ratioValue = prev.ratio || prev.percentage || prev.size_ratio || prev.pop_ratio;
			const nameValue = prev.name || prev.pop_name || prev.population_name;
			
			if (nameValue && ratioValue !== undefined) {
				const parsedRatio = typeof ratioValue === 'string' ? parseFloat(ratioValue) : ratioValue;
				previousMap.set(nameValue, parsedRatio);
			}
		});

		// Add % change to current pop size ratio data
		return current.map(curr => {
			// Try different possible field names for current data
			const currentRatioValue = curr.ratio || curr.percentage || curr.size_ratio || curr.pop_ratio;
			const currentNameValue = curr.name || curr.pop_name || curr.population_name;
			
			const prevRatio = previousMap.get(currentNameValue);
			const currentRatio = typeof currentRatioValue === 'string' ? parseFloat(currentRatioValue) : currentRatioValue;
			
			const percentageChange = prevRatio !== undefined && !isNaN(currentRatio) && !isNaN(prevRatio)
				? (currentRatio - prevRatio)
				: null;

			return {
				...curr,
				'% change': percentageChange !== null 
					? `${percentageChange >= 0 ? '+' : ''}${percentageChange.toFixed(1)}%`
					: 'N/A'
			};
		});
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
			// Trigger refresh of political compass and other components
			refreshTrigger++;
		}
	}

	// Handle save action from ParameterEdit component
	function handleParameterSave(action: string, success: boolean) {
		if (action === 'save' && success) {
			// Trigger voting behavior refresh by incrementing counter
			refreshTrigger++;
		}
	}

	// Load initial data
	onMount(async () => {
		const [periodResult, popResult] = await Promise.all([
			API.getAll<Period>('Period', 0, 100, 'year', 'descending'),
			API.getAll<Pop>('Pop', 0, 100, 'name', 'ascending')
		]);

		if (periodResult.success && periodResult.data) {
			periods = periodResult.data;
			if (periods.length > 0) {
				selectedPeriod = periods[0].id?.toString() || '';
			}
		}
		if (popResult.success && popResult.data) pops = popResult.data;
		
		selectedObject = getFirstObjectId(currentObjects);
	});

	// Load pops and parties when selectedPeriod changes
	$effect(() => {
		if (selectedPeriod) {
			console.log('Loading data for period:', selectedPeriod);
			Promise.all([
				API.getAll<Pop>('Pop', 0, 100, 'name', 'ascending', undefined, parseInt(selectedPeriod)),
				API.getAll<Party>('Party', 0, 100, 'name', 'ascending', undefined, parseInt(selectedPeriod))
			]).then(([popResult, partyResult]) => {
				if (popResult.success && popResult.data) {
					console.log('Loaded pops:', popResult.data.map(p => p.name));
					pops = popResult.data;
				}
				if (partyResult.success && partyResult.data) {
					console.log('Loaded parties:', partyResult.data.map(p => p.name));
					parties = partyResult.data;
				}
			});
		}
	});

	// Load pop size ratios when selectedPeriod changes or data is refreshed
	$effect(() => {
		if (selectedPeriod) {
			// Trigger refresh when refreshTrigger changes (after data save)
			refreshTrigger; 
			
			API.getPopSizeRatios(parseInt(selectedPeriod))
				.then(result => {
					if (result.success && result.data) {
						popSizeRatios = result.data;
					}
				});
		}
	});

	// Load previous period pop size ratios for % change calculation
	$effect(() => {
		if (previousPeriod) {
			// Trigger refresh when refreshTrigger changes (after data save)
			refreshTrigger;
			
			console.log('Fetching previous pop size ratios for period:', previousPeriod.id);
			
			API.getPopSizeRatios(previousPeriod.id!)
				.then(result => {
					if (result.success && result.data) {
						previousPopSizeRatios = result.data;
					} else {
						console.warn('No previous pop size ratios data:', result.error);
						previousPopSizeRatios = [];
					}
				})
				.catch(error => {
					console.error('Error fetching previous pop size ratios:', error);
					previousPopSizeRatios = [];
				});
		} else {
			previousPopSizeRatios = [];
		}
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

	// Fetch voting behavior data for Population model - reactive to refresh trigger
	$effect(() => {
		if (selectedPeriod && selectedObject && selectedDataModel === 'Population' && periodData) {
			const periodId = parseInt(selectedPeriod);
			const objectId = parseInt(selectedObject);
			
			// Only fetch voting behavior if PopPeriod data exists and IDs are valid
			if (!isNaN(periodId) && !isNaN(objectId) && periodId > 0 && objectId > 0) {
				// Depend on refreshTrigger to force re-execution after saves
				refreshTrigger; // This makes the effect reactive to refreshTrigger changes
				
				console.log('Fetching voting behavior for period:', periodId, 'pop:', objectId);
				
				getVotingBehavior(periodId, objectId)
					.then(result => {
						if (result.success && result.data) {
							votingBehavior = result.data;
						} else {
							console.warn('No voting behavior data:', result.error);
							votingBehavior = [];
						}
					})
					.catch(error => {
						console.error('Error fetching voting behavior:', error);
						votingBehavior = [];
					});
			} else {
				votingBehavior = [];
			}
		} else {
			votingBehavior = [];
		}
	});

	// Fetch previous period voting behavior for % change calculation
	$effect(() => {
		if (selectedObject && selectedDataModel === 'Population' && previousPeriod && previousData) {
			const prevPeriodId = previousPeriod.id!;
			const objectId = parseInt(selectedObject);
			
			if (!isNaN(objectId) && objectId > 0) {
				// Depend on refreshTrigger to force re-execution after saves
				refreshTrigger;
				
				console.log('Fetching previous voting behavior for period:', prevPeriodId, 'pop:', objectId);
				
				getVotingBehavior(prevPeriodId, objectId)
					.then(result => {
						if (result.success && result.data) {
							previousVotingBehavior = result.data;
						} else {
							console.warn('No previous voting behavior data:', result.error);
							previousVotingBehavior = [];
						}
					})
					.catch(error => {
						console.error('Error fetching previous voting behavior:', error);
						previousVotingBehavior = [];
					});
			} else {
				previousVotingBehavior = [];
			}
		} else {
			previousVotingBehavior = [];
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
	<Column>
		<Container title="({selectedPeriodYear}) {selectedObjectName}">
			{#if periodData}
				<ParameterEdit 
					bind:data={periodData} 
					bind:unsavedChanges={unsavedChanges}
					objectName={selectedObjectName}
					periodYear={parseInt(selectedPeriodYear) || 0}
					onAction={handleParameterSave}
					previousData={previousData}
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
		
		<!-- preview voting -->
		{#if selectedDataModel === 'Population'}
		<Container title="Preview Voting Behavior">
			{#if enhancedVotingBehavior.length > 0}
				<Table 
					model=""
					mode="simple"
					externalData={enhancedVotingBehavior}
					externalHeaders={votingBehaviorHeaders}
				/>
			{:else}
				<p class="text-sm text-lightText">No voting behavior data available</p>
			{/if}
		</Container>
		{/if}
	</Column>

	
	{#if selectedDataModel === 'Population'}
	<div class="flex flex-col gap-4">
		<!-- political compass -->
		<Container title="Political Compass">
			{#if selectedPeriod}
				<PoliticalCompass period={parseInt(selectedPeriod)} refreshTrigger={refreshTrigger} />
			{:else}
				<p class="text-sm text-dark-alt">Please select a period to view the political compass</p>
			{/if}
		</Container>
		
		<!-- scoring curve -->
		<Container title="Scoring Curve">
			{#if periodData && selectedDataModel === 'Population'}
				<ScoringCurve popPeriod={periodData as PopPeriod} refreshTrigger={refreshTrigger} />
			{:else}
				<p class="text-sm text-dark-alt">Please create or select PopPeriod data to view the scoring curve</p>
			{/if}
		</Container>

		<!-- pop size ratios -->
		<Container title="Population Size Ratios">
			{#if enhancedPopSizeRatios.length > 0}
				<Table mode="simple" externalData={enhancedPopSizeRatios} />
			{:else}
				<p class="text-sm text-dark-alt">No population data available for this period</p>
			{/if}
		</Container>
	</div>
	{/if}

	{#if selectedDataModel === 'Party'}
	<div class="flex flex-col gap-4">
		<!-- political compass -->
		<Container title="Political Compass">
			{#if selectedPeriod}
				<PoliticalCompass period={parseInt(selectedPeriod)} refreshTrigger={refreshTrigger} />
			{:else}
				<p class="text-sm text-dark-alt">Please select a period to view the political compass</p>
			{/if}
		</Container>
	</div>
	{/if}
</Grid>
