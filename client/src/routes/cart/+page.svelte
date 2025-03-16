<script lang="ts">
	import type { ProductC } from '$lib/types/types';

	let darkMode = $state(
		typeof localStorage !== 'undefined' && localStorage.getItem('darkMode') === 'true'
	);
	let total = $derived(darkMode ? 'dark' : 'light');
	$effect(() => {
		localStorage.setItem('darkMode', darkMode.toString());
	});
	// Пример данных для товаров в корзине
	let cartItems = $state<ProductC[]>([
		{
			id: 1,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			quantity: 1,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg'
		},
		{
			id: 2,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			quantity: 2,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg'
		},
		{
			id: 3,
			name: 'Ноутбук Apple MacBook Air',
			price: 999.99,
			quantity: 1,
			image:
				'https://main-cdn.sbermegamarket.ru/big1/hlr-system/-17/173/130/037/519/48/100055644608b0.jpg'
		}
	]);

	// Функция для изменения количества товара
	const updateQuantity = (id: number, newQuantity: number) => {
		if (newQuantity <= 0) removeItem(id);
		cartItems = cartItems.map((item) =>
			item.id === id ? { ...item, quantity: newQuantity } : item
		);
	};

	// Функция для удаления товара из корзины
	const removeItem = (id: number) => {
		cartItems = cartItems.filter((item) => item.id !== id);
	};

	// Вычисление общей суммы
	const totalAmount = $derived.by(() => {
		let total = 0;
		for (const n of cartItems) {
			total += n.price * n.quantity;
		}
		return total;
	});
</script>

<div class="min-h-screen bg-gray-100 py-8 dark:bg-gray-900" data-theme={total}>
	<div class="container mx-auto px-4">
		<h1 class="mb-8 text-3xl font-bold text-gray-800 dark:text-white" data-theme={total}>
			Корзина
		</h1>

		<!-- Список товаров -->
		<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800" data-theme={total}>
			{#if cartItems.length > 0}
				{#each cartItems as item (item.id)}
					<div
						class="flex items-center justify-between border-b border-gray-200 py-4 dark:border-gray-700"
						data-theme={total}
					>
						<div class="flex items-center">
							<img
								src={item.image}
								alt={item.name}
								class="h-16 w-16 rounded-lg object-cover dark:text-white"
								data-theme={total}
							/>
							<div class="ml-4">
								<h3 class="text-lg font-semibold text-gray-800 dark:text-white" data-theme={total}>
									{item.name}
								</h3>
								<p class="text-gray-600 dark:text-gray-400" data-theme={total}>
									${item.price.toFixed(2)}
								</p>
							</div>
						</div>

						<!-- Управление количеством -->
						<div class="flex items-center">
							<button
								onclick={() => updateQuantity(item.id, item.quantity - 1)}
								class="rounded-lg bg-gray-200 px-3 py-1 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
								data-theme={total}
							>
								-
							</button>
							<span class="mx-3 text-gray-800 dark:text-white" data-theme={total}
								>{item.quantity}</span
							>
							<button
								onclick={() => updateQuantity(item.id, item.quantity + 1)}
								class="rounded-lg bg-gray-200 px-3 py-1 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
								data-theme={total}
							>
								+
							</button>
						</div>

						<!-- Удаление товара -->
						<button
							onclick={() => removeItem(item.id)}
							class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-600"
							data-theme={total}
						>
							Удалить
						</button>
					</div>
				{/each}
			{:else}
				<p class="text-center text-gray-600 dark:text-gray-400" data-theme={total}>
					Ваша корзина пуста.
				</p>
			{/if}
		</div>

		<!-- Итоговая сумма -->
		{#if cartItems.length > 0}
			<div class="mt-8 rounded-lg bg-white p-6 shadow-md dark:bg-gray-800" data-theme={total}>
				<h2 class="mb-4 text-xl font-bold text-gray-800 dark:text-white" data-theme={total}>
					Итого
				</h2>
				<div class="flex items-center justify-between">
					<span class="text-gray-600 dark:text-gray-400" data-theme={total}>Общая сумма:</span>
					<span class="text-2xl font-bold text-gray-800 dark:text-white" data-theme={total}
						>${totalAmount.toFixed(2)}</span
					>
				</div>
				<button
					class="mt-6 w-full rounded-lg bg-indigo-600 py-3 text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none dark:bg-indigo-500 dark:hover:bg-indigo-600"
					data-theme={total}
				>
					Оформить заказ
				</button>
			</div>
		{/if}
	</div>
</div>
