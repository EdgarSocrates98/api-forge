export type Order = { order_id: string };

export async function listOrders(baseUrl: string): Promise<Order[]> {
  const response = await fetch(`${baseUrl}/orders`);
  return response.json() as Promise<Order[]>;
}
