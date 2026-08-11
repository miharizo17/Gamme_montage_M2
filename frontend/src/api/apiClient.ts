const API_BASE = '/api/gamme-montage'
const CLE_TOKEN = 'gamme-montage:token'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export function lireToken(): string | null {
  try {
    return localStorage.getItem(CLE_TOKEN)
  } catch {
    return null
  }
}

export function stockerToken(token: string) {
  try {
    localStorage.setItem(CLE_TOKEN, token)
  } catch {
    // Stockage indisponible (navigation privee, etc.) : le token ne survit pas au rechargement.
  }
}

export function supprimerToken() {
  try {
    localStorage.removeItem(CLE_TOKEN)
  } catch {
    // ignore
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      supprimerToken()
      window.dispatchEvent(new Event('gamme-montage:non-authentifie'))
    }
    const payload = await response.json().catch(() => null)
    const message = typeof payload?.detail === 'string' ? payload.detail : `Erreur ${response.status}`
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

function headersAvecAuth(base: Record<string, string> = {}): Record<string, string> {
  const token = lireToken()
  return token ? { ...base, Authorization: `Bearer ${token}` } : base
}

export async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: headersAvecAuth() })
  return handleResponse<T>(response)
}

export async function getBlob(path: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}${path}`, { headers: headersAvecAuth() })
  if (!response.ok) {
    if (response.status === 401) {
      supprimerToken()
      window.dispatchEvent(new Event('gamme-montage:non-authentifie'))
    }
    throw new ApiError(`Erreur ${response.status}`, response.status)
  }
  return response.blob()
}

export async function post<T>(path: string, body: unknown, sansAuth = false): Promise<T> {
  const headers = { 'Content-Type': 'application/json' }
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: sansAuth ? headers : headersAvecAuth(headers),
    body: JSON.stringify(body),
  })
  return handleResponse<T>(response)
}

export async function put<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: headersAvecAuth({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  })
  return handleResponse<T>(response)
}
