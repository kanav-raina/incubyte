export interface Money {
  minor: number
  currency: string
  amount: string
  formatted: string
}

export interface Country {
  code: string
  name: string
  currency: string
}

export interface Department {
  id: number
  name: string
}

export type EmploymentStatus = 'active' | 'terminated'

export interface Employee {
  id: number
  first_name: string
  last_name: string
  email: string
  country: Country
  department: Department
  role: string
  level: number
  hire_date: string
  status: EmploymentStatus
  manager_id: number | null
  current_salary: Money | null
  salary_in_base: Money | null
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface EmployeeFilters {
  q?: string
  country?: string
  department_id?: number
  level?: number
  status?: EmploymentStatus
  page?: number
  page_size?: number
}

export interface EmployeeCreate {
  first_name: string
  last_name: string
  email: string
  country_code: string
  department_id: number
  role: string
  level: number
  hire_date: string
  salary: string
  status?: EmploymentStatus
  manager_id?: number | null
}

export type EmployeeUpdate = Partial<{
  first_name: string
  last_name: string
  email: string
  country_code: string
  department_id: number
  role: string
  level: number
  status: EmploymentStatus
  manager_id: number | null
  salary: string
}>

export interface Summary {
  base_currency: string
  headcount: number
  total_payroll: Money
  average_salary: Money
  median_salary: Money | null
}

export interface GroupStat {
  key: string
  label: string
  headcount: number
  total: Money
  average: Money
  median: Money | null
}

export interface Grouped {
  base_currency: string
  groups: GroupStat[]
}

export interface LevelBand {
  level: number
  headcount: number
  min: Money
  median: Money | null
  max: Money
}

export interface Distribution {
  base_currency: string
  percentiles: Record<string, Money>
  bands: LevelBand[]
}
