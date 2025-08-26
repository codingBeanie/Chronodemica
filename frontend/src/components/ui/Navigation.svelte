<script lang="ts">
	const navigationItems = [
		{ label: 'Dashboard', href: '/', icon: '📊' },
		{ label: 'Perioden', href: '/periods', icon: '📅' },
		{ label: 'Bevölkerung', href: '/populations', icon: '👥' },
		{ label: 'Parteien', href: '/parties', icon: '🏛️' },
		{ label: 'Politischer Kompass', href: '/compass', icon: '🧭' },
		{ label: 'Simulation', href: '/simulation', icon: '⚡' },
		{ label: 'Wahlergebnisse', href: '/results', icon: '🗳️' },
		{ label: 'Regierungsbildung', href: '/government', icon: '🏛️' },
		{ label: 'Visualisierungen', href: '/charts', icon: '📈' }
	];
</script>

<nav class="w-64 h-screen bg-primary-300 border-r border-primary-200 flex flex-col">
	<!-- Logo and Title -->
	<div class="p-6 border-b border-primary-200">
		<div class="flex items-center space-x-3">
			<div class="w-10 h-10 bg-secondary-200 rounded-lg flex items-center justify-center">
				<span class="text-white font-bold text-xl">C</span>
			</div>
			<h1 class="text-xl font-bold text-secondary-100">Chronodemica</h1>
		</div>
	</div>
	
	<!-- Navigation Items -->
	<div class="flex-1 py-6">
		<ul class="space-y-2 px-4">
			{#each navigationItems as item}
				<li>
					<a 
						href={item.href} 
						class="flex items-center space-x-3 px-3 py-2 rounded-md text-secondary-100 hover:bg-primary-200 hover:text-primary-100 transition-colors duration-200 group"
					>
						<span class="text-lg group-hover:scale-110 transition-transform duration-200">{item.icon}</span>
						<span class="font-medium">{item.label}</span>
					</a>
				</li>
			{/each}
		</ul>
	</div>
	
	<!-- Footer -->
	<div class="p-4 border-t border-primary-200">
		<p class="text-xs text-secondary-100 text-center">
			Chronodemica v1.0
		</p>
	</div>
</nav>