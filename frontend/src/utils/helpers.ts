import { AxiosError } from 'axios'

export function getErrorMessage(err: unknown, fallback = 'Произошла ошибка'): string {
  const axiosErr = err as AxiosError<{ detail?: string; message?: string }>
  if (axiosErr?.response?.data) {
    return axiosErr.response.data.detail || axiosErr.response.data.message || fallback
  }
  if (err instanceof Error) return err.message
  return fallback
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function classNames(...parts: Array<string | false | undefined | null>): string {
  return parts.filter(Boolean).join(' ')
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
