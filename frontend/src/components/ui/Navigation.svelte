<script lang="ts">
	import NavLink from './NavLink.svelte';
	import Grid from './Grid.svelte';
</script>

<nav class="px-8 py-4 bg-dark text-light">
	<Grid cols="1fr 6fr 1fr" gap="gap-0">
		<!-- Logo and Title -->
		<div class="flex items-center border-r border-light-alt">
			<a href="/" class="flex items-center transition-opacity duration-200 hover:opacity-75">
				<h1 class="text-2xl font-semibold">Chronodemica</h1>
			</a>
		</div>
		
		<!-- Navigation Items -->
		<div class="flex items-center justify-start gap-4 pl-4 border-r border-light">
			<NavLink 
				href="/data_entry" 
				icon="database"
				text="Data Entry"
			/>
			<NavLink 
				href="/period_data" 
				icon="table"
				text="Period Data"
			/>
			<NavLink 
				href="/election" 
				icon="bar-chart-fill"
				text="Election"
			/>
			<NavLink 
				href="/statistics" 
				icon="graph-up"
				text="Statistics"
			/>
		</div>
		
		<!-- Version Info -->
		<div class="flex items-center justify-between ml-4">
			<p class="text-xs text-light-alt">
				Made by CodingBeanie with 🤍
			</p>
			<p class="text-sm text-light-alt">
				v1.0
			</p>
		</div>
	</Grid>
</nav>