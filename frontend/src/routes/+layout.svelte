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

<div class="min-h-screen bg-light-alt text-dark-alt">
	<Navigation />
	<main class="px-6 py-4">
		{@render children?.()}
	</main>
</div>
