import { Alert, Center, Loader } from '@mantine/core'
import { IconAlertCircle } from '@tabler/icons-react'
import type { ReactNode } from 'react'

interface QueryStateProps {
  isLoading: boolean
  error: unknown
  children: ReactNode
}

/** Renders a loader or error alert, otherwise the children. */
export function QueryState({ isLoading, error, children }: QueryStateProps) {
  if (isLoading) {
    return (
      <Center mih={200}>
        <Loader />
      </Center>
    )
  }

  if (error) {
    return (
      <Alert color="red" icon={<IconAlertCircle size={18} />} title="Something went wrong">
        {error instanceof Error ? error.message : 'Failed to load data.'}
      </Alert>
    )
  }

  return <>{children}</>
}
