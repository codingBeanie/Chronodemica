<script lang="ts">
	import { page } from '$app/stores';
	
	interface Props {
		href: string;
		icon: string;
		text: string;
	}
	
	let { href, icon, text }: Props = $props();
	
	// Check if current page matches this link
	const isActive = $derived($page.url.pathname === href);
</script>

<a 
	{href}
	class="flex items-center py-2 px-3 rounded-lg {isActive ? 'text-light' : 'text-light-alt opacity-80'}"
>
	<i class="bi bi-{icon} mr-3 text-2xl"></i>
	<span class="text-lg">{text}</span>
</a>