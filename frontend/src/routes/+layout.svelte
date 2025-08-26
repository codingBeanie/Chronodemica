<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navigation from '../components/ui/Navigation.svelte';
	
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="flex min-h-screen bg-secondary-100">
	<Navigation />
	<main class="flex-1 p-8">
		{@render children?.()}
	</main>
</div>
