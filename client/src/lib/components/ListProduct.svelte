<script lang="ts">
	import type { Product } from '$lib/types/types';

	let { products, total }: { products: Product[]; total: string } = $props();
</script>

<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
	{#each products as product (product.id)}
		<div
			class="overflow-hidden rounded-lg bg-white shadow-md transition-all hover:shadow-lg dark:bg-gray-800"
			data-theme={total}
		>
			<img
				src={product.image}
				alt={product.name}
				class="h-65 w-full object-cover dark:brightness-90"
			/>
			<div class="p-4">
				<h3 class="text-xl font-semibold text-gray-800 dark:text-white" data-theme={total}>
					{product.name}
				</h3>
				<p class="mt-2 text-gray-600 dark:text-gray-400">{product.description}</p>
				<div class="mt-4 flex items-center justify-between">
					<span class="text-lg font-bold text-gray-800 dark:text-white" data-theme={total}
						>${product.price.toFixed(2)}</span
					>
					<button
						class="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600"
						data-theme={total}
					>
						В корзину
					</button>
				</div>
			</div>
		</div>
	{/each}
</div>
