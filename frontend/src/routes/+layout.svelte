<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navigation from '../components/ui/Navigation.svelte';
	
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" />
</svelte:head>

<div class="flex min-h-screen bg-light-alt text-dark-alt px-8">
	<Navigation />
	<main class="flex-1 h-full flex pt-4 flex-col">
		<div class="flex-1">
			{@render children?.()}
		</div>
	</main>
</div>
