import { useEffect } from 'react'
import {
  Button,
  Group,
  Modal,
  NumberInput,
  Select,
  SimpleGrid,
  TextInput,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { notifications } from '@mantine/notifications'
import { useCountries, useCreateEmployee, useDepartments, useUpdateEmployee } from '../api/hooks'
import type { Employee, EmployeeCreate, EmployeeUpdate, EmploymentStatus } from '../api/types'

interface EmployeeFormModalProps {
  opened: boolean
  onClose: () => void
  employee: Employee | null
}

interface FormValues {
  first_name: string
  last_name: string
  email: string
  country_code: string
  department_id: string
  role: string
  level: string
  hire_date: string
  salary: number | string
  status: EmploymentStatus
}

const LEVEL_OPTIONS = ['1', '2', '3', '4', '5', '6', '7'].map((l) => ({ value: l, label: `L${l}` }))
const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'terminated', label: 'Terminated' },
]

function emptyValues(): FormValues {
  return {
    first_name: '',
    last_name: '',
    email: '',
    country_code: '',
    department_id: '',
    role: '',
    level: '',
    hire_date: '',
    salary: '',
    status: 'active',
  }
}

function valuesFrom(employee: Employee): FormValues {
  return {
    first_name: employee.first_name,
    last_name: employee.last_name,
    email: employee.email,
    country_code: employee.country.code,
    department_id: String(employee.department.id),
    role: employee.role,
    level: String(employee.level),
    hire_date: employee.hire_date,
    salary: employee.current_salary ? Number(employee.current_salary.amount) : '',
    status: employee.status,
  }
}

export function EmployeeFormModal({ opened, onClose, employee }: EmployeeFormModalProps) {
  const isEdit = employee !== null
  const countries = useCountries()
  const departments = useDepartments()
  const createMutation = useCreateEmployee()
  const updateMutation = useUpdateEmployee(employee?.id ?? 0)

  const form = useForm<FormValues>({
    initialValues: emptyValues(),
    validate: {
      first_name: (v) => (v.trim() ? null : 'Required'),
      last_name: (v) => (v.trim() ? null : 'Required'),
      email: (v) => (/^\S+@\S+\.\S+$/.test(v) ? null : 'Invalid email'),
      country_code: (v) => (v ? null : 'Required'),
      department_id: (v) => (v ? null : 'Required'),
      role: (v) => (v.trim() ? null : 'Required'),
      level: (v) => (v ? null : 'Required'),
      hire_date: (v) => (isEdit || v ? null : 'Required'),
      salary: (v) => (Number(v) > 0 ? null : 'Must be greater than 0'),
    },
  })

  // Reset the form whenever the modal opens for a different employee.
  useEffect(() => {
    if (opened) {
      form.setValues(employee ? valuesFrom(employee) : emptyValues())
      form.resetDirty()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [opened, employee])

  const handleSubmit = form.onSubmit(async (values) => {
    try {
      if (isEdit && employee) {
        const payload: EmployeeUpdate = {
          first_name: values.first_name,
          last_name: values.last_name,
          email: values.email,
          country_code: values.country_code,
          department_id: Number(values.department_id),
          role: values.role,
          level: Number(values.level),
          status: values.status,
          salary: String(values.salary),
        }
        await updateMutation.mutateAsync(payload)
        notifications.show({ message: 'Employee updated', color: 'teal' })
      } else {
        const payload: EmployeeCreate = {
          first_name: values.first_name,
          last_name: values.last_name,
          email: values.email,
          country_code: values.country_code,
          department_id: Number(values.department_id),
          role: values.role,
          level: Number(values.level),
          hire_date: values.hire_date,
          salary: String(values.salary),
          status: values.status,
        }
        await createMutation.mutateAsync(payload)
        notifications.show({ message: 'Employee created', color: 'teal' })
      }
      onClose()
    } catch (err) {
      notifications.show({
        message: err instanceof Error ? err.message : 'Save failed',
        color: 'red',
      })
    }
  })

  const selectedCurrency =
    countries.data?.find((c) => c.code === form.values.country_code)?.currency

  return (
    <Modal opened={opened} onClose={onClose} title={isEdit ? 'Edit employee' : 'New employee'} centered>
      <form onSubmit={handleSubmit}>
        <SimpleGrid cols={2}>
          <TextInput label="First name" {...form.getInputProps('first_name')} />
          <TextInput label="Last name" {...form.getInputProps('last_name')} />
        </SimpleGrid>
        <TextInput label="Email" mt="sm" {...form.getInputProps('email')} />
        <SimpleGrid cols={2} mt="sm">
          <Select
            label="Country"
            searchable
            data={(countries.data ?? []).map((c) => ({ value: c.code, label: c.name }))}
            {...form.getInputProps('country_code')}
          />
          <Select
            label="Department"
            data={(departments.data ?? []).map((d) => ({ value: String(d.id), label: d.name }))}
            {...form.getInputProps('department_id')}
          />
        </SimpleGrid>
        <SimpleGrid cols={2} mt="sm">
          <TextInput label="Role" {...form.getInputProps('role')} />
          <Select label="Level" data={LEVEL_OPTIONS} {...form.getInputProps('level')} />
        </SimpleGrid>
        <SimpleGrid cols={2} mt="sm">
          <NumberInput
            label={`Salary${selectedCurrency ? ` (${selectedCurrency})` : ''}`}
            thousandSeparator
            min={0}
            {...form.getInputProps('salary')}
          />
          {isEdit ? (
            <Select label="Status" data={STATUS_OPTIONS} {...form.getInputProps('status')} />
          ) : (
            <TextInput label="Hire date" type="date" {...form.getInputProps('hire_date')} />
          )}
        </SimpleGrid>

        <Group justify="flex-end" mt="lg">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={createMutation.isPending || updateMutation.isPending}>
            {isEdit ? 'Save' : 'Create'}
          </Button>
        </Group>
      </form>
    </Modal>
  )
}
