import { Badge } from '@mantine/core'
import type { EmploymentStatus } from '../api/types'

export function StatusBadge({ status }: { status: EmploymentStatus }) {
  return (
    <Badge color={status === 'active' ? 'teal' : 'gray'} variant="light">
      {status}
    </Badge>
  )
}
