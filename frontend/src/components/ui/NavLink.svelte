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
	class="flex items-center hover:opacity-80 transition-opacity duration-200 py-2 px-3 rounded-lg {isActive ? 'bg-dark text-light opacity-70' : ''}"
>
	<i class="bi bi-{icon} mr-3 text-xl"></i>
	<span class="font-light">{text}</span>
</a>