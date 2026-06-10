import { useMemo, useState } from 'react'
import {
  Group,
  Pagination,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { useDebouncedValue } from '@mantine/hooks'
import { IconSearch } from '@tabler/icons-react'
import { useCountries, useDepartments, useEmployees } from '../api/hooks'
import type { EmployeeFilters, EmploymentStatus } from '../api/types'
import { QueryState } from '../components/QueryState'
import { StatusBadge } from '../components/StatusBadge'

const PAGE_SIZE = 25
const LEVEL_OPTIONS = ['1', '2', '3', '4', '5', '6', '7'].map((l) => ({
  value: l,
  label: `L${l}`,
}))
const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'terminated', label: 'Terminated' },
]

export function EmployeesPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch] = useDebouncedValue(search, 300)
  const [country, setCountry] = useState<string | null>(null)
  const [departmentId, setDepartmentId] = useState<string | null>(null)
  const [level, setLevel] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const countries = useCountries()
  const departments = useDepartments()

  const filters: EmployeeFilters = useMemo(
    () => ({
      q: debouncedSearch || undefined,
      country: country ?? undefined,
      department_id: departmentId ? Number(departmentId) : undefined,
      level: level ? Number(level) : undefined,
      status: (status as EmploymentStatus) ?? undefined,
      page,
      page_size: PAGE_SIZE,
    }),
    [debouncedSearch, country, departmentId, level, status, page],
  )

  const { data, isLoading, error, isFetching } = useEmployees(filters)

  // Any filter change should return to the first page.
  const onFilterChange = <T,>(setter: (value: T) => void) => (value: T) => {
    setter(value)
    setPage(1)
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <Stack>
      <Group justify="space-between" align="flex-end">
        <Title order={2}>Employees</Title>
        {data && (
          <Text c="dimmed" size="sm">
            {data.total.toLocaleString()} employees
          </Text>
        )}
      </Group>

      <Paper withBorder p="md" radius="md">
        <Group align="flex-end" wrap="wrap">
          <TextInput
            label="Search"
            placeholder="Name or email"
            leftSection={<IconSearch size={16} />}
            value={search}
            onChange={(e) => {
              setSearch(e.currentTarget.value)
              setPage(1)
            }}
            w={240}
          />
          <Select
            label="Country"
            placeholder="All"
            clearable
            data={(countries.data ?? []).map((c) => ({ value: c.code, label: c.name }))}
            value={country}
            onChange={onFilterChange(setCountry)}
            w={170}
          />
          <Select
            label="Department"
            placeholder="All"
            clearable
            data={(departments.data ?? []).map((d) => ({ value: String(d.id), label: d.name }))}
            value={departmentId}
            onChange={onFilterChange(setDepartmentId)}
            w={170}
          />
          <Select
            label="Level"
            placeholder="All"
            clearable
            data={LEVEL_OPTIONS}
            value={level}
            onChange={onFilterChange(setLevel)}
            w={110}
          />
          <Select
            label="Status"
            placeholder="All"
            clearable
            data={STATUS_OPTIONS}
            value={status}
            onChange={onFilterChange(setStatus)}
            w={140}
          />
        </Group>
      </Paper>

      <QueryState isLoading={isLoading} error={error}>
        <Paper withBorder radius="md" style={{ opacity: isFetching ? 0.6 : 1 }}>
          <Table.ScrollContainer minWidth={900}>
            <Table highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Name</Table.Th>
                  <Table.Th>Country</Table.Th>
                  <Table.Th>Department</Table.Th>
                  <Table.Th>Role</Table.Th>
                  <Table.Th>Level</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Salary (local)</Table.Th>
                  <Table.Th>Salary (USD)</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {data?.items.map((employee) => (
                  <Table.Tr key={employee.id}>
                    <Table.Td>
                      <Text fw={500}>
                        {employee.first_name} {employee.last_name}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {employee.email}
                      </Text>
                    </Table.Td>
                    <Table.Td>{employee.country.name}</Table.Td>
                    <Table.Td>{employee.department.name}</Table.Td>
                    <Table.Td>{employee.role}</Table.Td>
                    <Table.Td>L{employee.level}</Table.Td>
                    <Table.Td>
                      <StatusBadge status={employee.status} />
                    </Table.Td>
                    <Table.Td>{employee.current_salary?.formatted ?? '—'}</Table.Td>
                    <Table.Td>{employee.salary_in_base?.formatted ?? '—'}</Table.Td>
                  </Table.Tr>
                ))}
                {data?.items.length === 0 && (
                  <Table.Tr>
                    <Table.Td colSpan={8}>
                      <Text c="dimmed" ta="center" py="lg">
                        No employees match these filters.
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                )}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        </Paper>

        <Group justify="center" mt="md">
          <Pagination total={totalPages} value={page} onChange={setPage} />
        </Group>
      </QueryState>
    </Stack>
  )
}
