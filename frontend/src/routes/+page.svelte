<script lang="ts">
	const startSteps = [
		{
			number: 1,
			title: 'Erstelle Akteure und Perioden',
			description: 'Definieren Sie Bevölkerungsgruppen, Parteien und zeitliche Rahmen für Ihre Simulation',
			icon: '👥',
			color: 'accent'
		},
		{
			number: 2,
			title: 'Lege die Parameter fest',
			description: 'Bestimmen Sie politische Orientierungen und Eigenschaften Ihrer Akteure',
			icon: '⚙️',
			color: 'accent'
		},
		{
			number: 3,
			title: 'Simuliere eine Wahl',
			description: 'Starten Sie die Wahlsimulation und analysieren Sie die berechneten Ergebnisse',
			icon: '🗳️',
			color: 'success'
		}
	];
</script>

<div class="max-w-7xl mx-auto">
	<!-- Header -->
	<div class="text-center mb-16">
		<h1 class="text-5xl font-bold text-secondary-300 mb-6">
			Welcome to Chronodemica
		</h1>
		<p class="text-xl text-secondary-300 max-w-4xl mx-auto mb-8">
			Ein innovatives Webtool zur Simulation und Visualisierung fiktiver Wahlresultate. 
			Erforschen Sie komplexe politische Dynamiken und deren zeitliche Entwicklung.
		</p>
		<div class="w-24 h-1 bg-primary-200 mx-auto rounded-full"></div>
	</div>
	
	<!-- Start Guide -->
	<div class="max-w-6xl mx-auto">
		<h2 class="text-3xl font-bold text-secondary-300 text-center mb-4">So funktioniert's</h2>
		<p class="text-lg text-secondary-300 text-center mb-12 opacity-80">In drei einfachen Schritten zu Ihrer ersten Wahlsimulation</p>
		
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			{#each startSteps as step}
				<button class="p-8 bg-white rounded-2xl shadow-sm hover:shadow-xl hover:scale-105 transition-all duration-300 border border-secondary-200 text-center group cursor-pointer">
					<!-- Icon & Number -->
					<div class="flex justify-center mb-6">
						<div class="relative">
							<div class="w-20 h-20 bg-white border-2 border-secondary-200 rounded-2xl flex items-center justify-center shadow-md group-hover:border-{step.color}-200 transition-colors duration-300">
								<span class="text-3xl">{step.icon}</span>
							</div>
							<div class="absolute -top-2 -right-2 w-8 h-8 bg-primary-300 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
								{step.number}
							</div>
						</div>
					</div>
					
					<!-- Content -->
					<div>
						<h3 class="text-xl font-bold text-secondary-300 mb-3 group-hover:text-{step.color}-300 transition-colors duration-300">{step.title}</h3>
						<p class="text-secondary-300 opacity-90">{step.description}</p>
					</div>
				</button>
			{/each}
		</div>
	</div>
</div>
