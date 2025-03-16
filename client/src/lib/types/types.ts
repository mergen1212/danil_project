export interface Product {
	id: number;
	name: string;
	price: number;
	image: string;
	description: string;
}
export interface ProductC {
	id: number;
	name: string;
	price: number;
	quantity: number;
	image: string;
}
export interface UserAuth {
	email: string;
	password: string;
	confirmPassword: string;
}
