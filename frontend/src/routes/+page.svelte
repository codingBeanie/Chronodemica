<script lang="ts">
	import ClickableCard from '../components/ui/ClickableCard.svelte';
	import ContentHeader from '../components/ui/ContentHeader.svelte';
	import Container from '../components/ui/Container.svelte';
	import Grid from '../components/ui/Grid.svelte';
	import Column from '../components/ui/Column.svelte';
	
	const startSteps = [
		{
			number: 1,
			title: 'Create Actors and Periods',
			description: 'Define population groups, parties, and time frames for your simulation',
			icon: '👥',
			href: '/data_entry'
		},
		{
			number: 2,
			title: 'Set Parameters',
			description: 'Determine political orientations and characteristics of your actors',
			icon: '⚙️'
		},
		{
			number: 3,
			title: 'Simulate Election',
			description: 'Start the election simulation and analyze the calculated results',
			icon: '🗳️'
		}
	];
</script>


<!-- Start Guide -->
<Grid cols="1fr">
	<Column>
		<Container>
			<h2 class="text-3xl font-bold text-dark-alt text-center mb-4">How it works</h2>
			<p class="text-lg text-dark-alt text-center mb-12 opacity-80">Your first election simulation in three simple steps</p>
			
			<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
				{#each startSteps as step}
					<ClickableCard 
						title={step.title}
						text={step.description}
						icon={step.icon}
						number={step.number}
						href={step.href}
					/>
				{/each}
			</div>
		</Container>
	</Column>
</Grid>
