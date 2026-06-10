import { useMemo, useState } from 'react'
import {
  ActionIcon,
  Button,
  Group,
  Pagination,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core'
import { useDebouncedValue } from '@mantine/hooks'
import { notifications } from '@mantine/notifications'
import { IconEdit, IconPlus, IconSearch, IconUserOff } from '@tabler/icons-react'
import { useCountries, useDeactivateEmployee, useDepartments, useEmployees } from '../api/hooks'
import type { Employee, EmployeeFilters, EmploymentStatus } from '../api/types'
import { EmployeeFormModal } from '../components/EmployeeFormModal'
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

  const [formOpened, setFormOpened] = useState(false)
  const [editing, setEditing] = useState<Employee | null>(null)

  const countries = useCountries()
  const departments = useDepartments()
  const deactivate = useDeactivateEmployee()

  const openCreate = () => {
    setEditing(null)
    setFormOpened(true)
  }

  const openEdit = (employee: Employee) => {
    setEditing(employee)
    setFormOpened(true)
  }

  const handleDeactivate = (employee: Employee) => {
    if (!window.confirm(`Deactivate ${employee.first_name} ${employee.last_name}?`)) return
    deactivate.mutate(employee.id, {
      onSuccess: () => notifications.show({ message: 'Employee deactivated', color: 'teal' }),
      onError: (err) =>
        notifications.show({
          message: err instanceof Error ? err.message : 'Failed',
          color: 'red',
        }),
    })
  }

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
        <Group>
          <Title order={2}>Employees</Title>
          {data && (
            <Text c="dimmed" size="sm">
              {data.total.toLocaleString()} total
            </Text>
          )}
        </Group>
        <Button leftSection={<IconPlus size={16} />} onClick={openCreate}>
          New employee
        </Button>
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
                  <Table.Th w={90}>Actions</Table.Th>
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
                    <Table.Td>
                      <Group gap="xs" wrap="nowrap">
                        <Tooltip label="Edit">
                          <ActionIcon variant="subtle" onClick={() => openEdit(employee)}>
                            <IconEdit size={16} />
                          </ActionIcon>
                        </Tooltip>
                        <Tooltip label="Deactivate">
                          <ActionIcon
                            variant="subtle"
                            color="red"
                            disabled={employee.status === 'terminated'}
                            onClick={() => handleDeactivate(employee)}
                          >
                            <IconUserOff size={16} />
                          </ActionIcon>
                        </Tooltip>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
                {data?.items.length === 0 && (
                  <Table.Tr>
                    <Table.Td colSpan={9}>
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

      <EmployeeFormModal
        opened={formOpened}
        onClose={() => setFormOpened(false)}
        employee={editing}
      />
    </Stack>
  )
}
