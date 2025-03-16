<script lang="ts">
	let { darkMode = $bindable(), total }: { darkMode: boolean; total: string } = $props();
</script>

<header class="bg-white shadow dark:bg-gray-800" data-theme={total}>
	<div class="container mx-auto px-6 py-4">
		<div class="flex items-center justify-between">
			<h1 class="text-2xl font-bold text-gray-800 dark:text-white" data-theme={total}>E-Shop</h1>
			<nav class="flex items-center space-x-6">
				<button
					onclick={() => (darkMode = !darkMode)}
					class="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
				>
					{#if darkMode}
						<span class="text-white">🌞</span>
					{:else}
						<span>🌙</span>
					{/if}
				</button>
				<a
					href="/"
					class="text-gray-800 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400"
					data-theme={total}>Главная</a
				>
				<a
					href="/products"
					class="text-gray-800 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400"
					data-theme={total}>Товары</a
				>
				<a
					href="/cart"
					class="text-gray-800 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400"
					data-theme={total}>Корзина</a
				>
			</nav>
		</div>
	</div>
</header>
