<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navigation from '../components/ui/Navigation.svelte';
	
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="flex min-h-screen bg-secondary-500">
	<Navigation />
	<main class="flex-1 h-full flex pt-4 flex-col">
		<div class="flex-1 px-6">
			<div class="max-w-7xl mx-auto">
				{@render children?.()}
			</div>
		</div>
	</main>
</div>
