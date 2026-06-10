import type {
  Country,
  Department,
  Distribution,
  Employee,
  EmployeeCreate,
  EmployeeFilters,
  EmployeeUpdate,
  Grouped,
  Page,
  Summary,
} from './types'

// In dev, leave empty so Vite proxies /api -> backend. In prod, set VITE_API_URL.
const BASE_URL = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })

  if (!response.ok) {
    let detail: string = response.statusText
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') detail = body.detail
      else if (body.detail) detail = JSON.stringify(body.detail)
    } catch {
      // response had no JSON body; keep statusText
    }
    throw new Error(detail)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

function buildQuery(filters: EmployeeFilters): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value))
    }
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}

export const api = {
  listEmployees: (filters: EmployeeFilters = {}) =>
    request<Page<Employee>>(`/api/employees${buildQuery(filters)}`),
  getEmployee: (id: number) => request<Employee>(`/api/employees/${id}`),
  createEmployee: (payload: EmployeeCreate) =>
    request<Employee>('/api/employees', { method: 'POST', body: JSON.stringify(payload) }),
  updateEmployee: (id: number, payload: EmployeeUpdate) =>
    request<Employee>(`/api/employees/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deactivateEmployee: (id: number) =>
    request<void>(`/api/employees/${id}`, { method: 'DELETE' }),

  getCountries: () => request<Country[]>('/api/meta/countries'),
  getDepartments: () => request<Department[]>('/api/meta/departments'),

  getSummary: () => request<Summary>('/api/analytics/summary'),
  getByCountry: () => request<Grouped>('/api/analytics/by-country'),
  getByDepartment: () => request<Grouped>('/api/analytics/by-department'),
  getDistribution: () => request<Distribution>('/api/analytics/distribution'),
}
