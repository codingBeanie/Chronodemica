<script lang="ts">
	interface Props {
		title: string;
		text: string;
		icon: string;
		number: number;
		href?: string;
	}
	
	let { title, text, icon, number, href }: Props = $props();
</script>

{#if href}
	<a {href} class="block p-8 bg-secondary-100 rounded-2xl shadow-sm hover:shadow-xl hover:scale-105 transition-all duration-300 border border-secondary-200 text-center group cursor-pointer">
		<!-- Icon & Number -->
		<div class="flex justify-center mb-6">
			<div class="relative">
				<div class="w-20 h-20 bg-white border-2 border-secondary-200 rounded-2xl flex items-center justify-center shadow-md group-hover:border-accent-200 transition-colors duration-300">
					<span class="text-3xl">{icon}</span>
				</div>
				<div class="absolute -top-2 -right-2 w-8 h-8 bg-primary-300 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
					{number}
				</div>
			</div>
		</div>
		
		<!-- Content -->
		<div>
			<h3 class="text-xl font-bold text-secondary-300 mb-3 group-hover:text-accent-300 transition-colors duration-300">{title}</h3>
			<p class="text-secondary-300 opacity-90">{text}</p>
		</div>
	</a>
{:else}
	<button class="p-8 bg-secondary-100 rounded-2xl shadow-sm hover:shadow-xl hover:scale-105 transition-all duration-300 border border-secondary-200 text-center group cursor-pointer">
		<!-- Icon & Number -->
		<div class="flex justify-center mb-6">
			<div class="relative">
				<div class="w-20 h-20 bg-white border-2 border-secondary-200 rounded-2xl flex items-center justify-center shadow-md group-hover:border-accent-200 transition-colors duration-300">
					<span class="text-3xl">{icon}</span>
				</div>
				<div class="absolute -top-2 -right-2 w-8 h-8 bg-primary-300 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
					{number}
				</div>
			</div>
		</div>
		
		<!-- Content -->
		<div>
			<h3 class="text-xl font-bold text-secondary-300 mb-3 group-hover:text-accent-300 transition-colors duration-300">{title}</h3>
			<p class="text-secondary-300 opacity-90">{text}</p>
		</div>
	</button>
{/if}