<script lang="ts">
	import NavLink from './NavLink.svelte';
</script>

<nav class="w-48 p-4 h-screen flex flex-col ">
	<!-- Logo and Title -->
	<div class="pt-12 pb-12">
		<a href="/" class="flex hover:opacity-50 transition-opacity duration-200">
			<h1 class="text-xl ">Chronodemica</h1>
		</a>
	</div>
	
	<!-- Navigation Items -->
	<div class="flex-1">
		<ul class="space-y-2">
			<li>
				<NavLink 
					href="/data_entry" 
					icon="database"
					text="Data Entry"
				/>
			</li>
			<li>
				<NavLink 
					href="/period_data" 
					icon="table"
					text="Period Data"
				/>
			</li>
		</ul>
	</div>
	
	<!-- Footer -->
	<div class="p-4">
		<p class="text-xs text-thin-text text-center">
			Chronodemica v1.0
		</p>
	</div>
</nav>