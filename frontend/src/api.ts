export async function api<T>(url:string, options?:RequestInit):Promise<T> {
  const response = await fetch('/api' + url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Confira os dados enviados.');
  return data;
}
export function json(body:unknown):RequestInit {return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}}
