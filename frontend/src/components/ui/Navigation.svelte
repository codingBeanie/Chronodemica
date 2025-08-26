<script lang="ts">
</script>

<nav class="w-64 h-screen bg-primary-300 border-r border-primary-200 flex flex-col">
	<!-- Logo and Title -->
	<div class="p-6 border-b border-primary-200">
		<a href="/" class="flex items-center space-x-3 hover:opacity-80 transition-opacity duration-200">
			<div class="w-10 h-10 bg-secondary-200 rounded-lg flex items-center justify-center">
				<span class="text-white font-bold text-xl">C</span>
			</div>
			<h1 class="text-xl font-bold text-secondary-100">Chronodemica</h1>
		</a>
	</div>
	
	<!-- Navigation Items -->
	<div class="flex-1 py-6">
		<ul class="space-y-2 px-4">
			<li>
				<a 
					href="/data_entry" 
					class="flex items-center space-x-3 px-3 py-2 rounded-md text-secondary-100 hover:bg-primary-200 hover:text-primary-100 transition-colors duration-200 group"
				>
					<span class="text-lg group-hover:scale-110 transition-transform duration-200">📝</span>
					<span class="font-medium">Data Entry</span>
				</a>
			</li>
		</ul>
	</div>
	
	<!-- Footer -->
	<div class="p-4 border-t border-primary-200">
		<p class="text-xs text-secondary-100 text-center">
			Chronodemica v1.0
		</p>
	</div>
</nav>