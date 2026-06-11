import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { EmployeeCreate, EmployeeFilters, EmployeeUpdate } from './types'

const keys = {
  employees: (filters: EmployeeFilters) => ['employees', filters] as const,
  employee: (id: number) => ['employee', id] as const,
  countries: ['countries'] as const,
  departments: ['departments'] as const,
  analytics: ['analytics'] as const,
}

export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: keys.employees(filters),
    queryFn: () => api.listEmployees(filters),
  })
}

export function useCountries() {
  return useQuery({ queryKey: keys.countries, queryFn: api.getCountries, staleTime: Infinity })
}

export function useDepartments() {
  return useQuery({ queryKey: keys.departments, queryFn: api.getDepartments, staleTime: Infinity })
}

function useInvalidateEmployees() {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: ['employees'] })
    queryClient.invalidateQueries({ queryKey: keys.analytics })
  }
}

export function useCreateEmployee() {
  const invalidate = useInvalidateEmployees()
  return useMutation({
    mutationFn: (payload: EmployeeCreate) => api.createEmployee(payload),
    onSuccess: invalidate,
  })
}

export function useUpdateEmployee(id: number) {
  const invalidate = useInvalidateEmployees()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: EmployeeUpdate) => api.updateEmployee(id, payload),
    onSuccess: () => {
      invalidate()
      queryClient.invalidateQueries({ queryKey: keys.employee(id) })
    },
  })
}

export function useDeactivateEmployee() {
  const invalidate = useInvalidateEmployees()
  return useMutation({
    mutationFn: (id: number) => api.deactivateEmployee(id),
    onSuccess: invalidate,
  })
}

export function useSummary() {
  return useQuery({ queryKey: [...keys.analytics, 'summary'], queryFn: api.getSummary })
}

export function useByCountry() {
  return useQuery({ queryKey: [...keys.analytics, 'by-country'], queryFn: api.getByCountry })
}

export function useByDepartment() {
  return useQuery({ queryKey: [...keys.analytics, 'by-department'], queryFn: api.getByDepartment })
}

export function useDistribution() {
  return useQuery({ queryKey: [...keys.analytics, 'distribution'], queryFn: api.getDistribution })
}
