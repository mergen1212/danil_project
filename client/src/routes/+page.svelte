<script lang="ts">
	import HomeHeader from '$lib/components/HomeHeader.svelte';
	import ListProduct from '$lib/components/ListProduct.svelte';
	import type { Product } from '$lib/types/types';

	// Состояние темной темы
	let darkMode = $state(
		typeof localStorage !== 'undefined' && localStorage.getItem('darkMode') === 'true'
	);
	let total = $derived(darkMode ? 'dark' : 'light');
	$effect(() => {
		localStorage.setItem('darkMode', darkMode.toString());
	});

	// Пример данных для товаров
	const products: Product[] = [
		{
			id: 1,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg',
			description: 'Легкий и мощный ноутбук для работы и творчества.'
		},
		{
			id: 2,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg',
			description: 'Легкий и мощный ноутбук для работы и творчества.'
		},
		{
			id: 3,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg',
			description: 'Легкий и мощный ноутбук для работы и творчества.'
		},
		{
			id: 4,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg',
			description: 'Легкий и мощный ноутбук для работы и творчества.'
		}
		// ... остальные товары
	];
</script>

<div class="min-h-screen transition-colors duration-300 dark:bg-gray-800" data-theme={total}>
	<!-- Шапка -->
	<HomeHeader bind:darkMode {total} />

	<!-- Основной контент -->
	<main class="container mx-auto px-6 py-8 dark:text-white" data-theme={total}>
		<h2 class="mb-6 text-3xl font-bold text-gray-800 dark:text-white" data-theme={total}>
			Популярные товары
		</h2>

		<!-- Список товаров -->
		<ListProduct {products} {total} />

		<!-- Подвал -->
		<footer class="mt-8 shadow" data-theme={total}>
			<div class="container mx-auto px-6 py-4">
				<p class="text-center text-gray-600 dark:text-gray-400">
					© 2025 E-Shop. Все права защищены.
				</p>
			</div>
		</footer>
	</main>
</div>
