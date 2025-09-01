<script lang="ts">
	import ContentHeader from '../../components/ui/ContentHeader.svelte';
	import SegmentedControl from '../../components/ui/SegmentedControl.svelte';
	import CrudTable from '../../components/ui/CrudTable.svelte';
	import Container from '../../components/ui/Container.svelte';
	import Grid from '../../components/ui/Grid.svelte';
	import Column from '../../components/ui/Column.svelte';

	// Configuration hashmap for the segmented control options
	const dataTypeOptions = {
		'Population': 'Pop',
		'Party': 'Party', 
		'Period': 'Period'
	};
	
	let selectedDataType: 'Pop' | 'Party' | 'Period' = 'Pop';
</script>

<ContentHeader 
	title="Data Entry" 
/>

<Grid cols="1fr">
	<Column>
		<Container>
			<div class="mb-16">
				<SegmentedControl 
					label="Select Data Type"
					options={dataTypeOptions}
					bind:selectedValue={selectedDataType}
				/>
			</div>
			<div>
				<CrudTable model={selectedDataType} />
			</div>
		</Container>
	</Column>
</Grid>