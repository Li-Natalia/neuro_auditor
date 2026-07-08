import { Card, CardContent, Table, TableBody, TableCell, TableHead, TableRow, Typography, Box, Button } from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import type { AnalysisResult } from '../../types/analysis.types'
import { formatNumber, formatPercent } from '../../utils/formatters'
import { useAnalysis } from '../../hooks/useAnalysis'
import { useThemeStore } from '../../store/slices/uiSlice'

interface Props {
  result: AnalysisResult
}

export function ReportDetails({ result }: Props) {
  const { downloadReport } = useAnalysis()
  const { notify } = useThemeStore()

  const balanceRows = [
    ['Всего активов', result.balanceSheet.totalAssets],
    ['Оборотные активы', result.balanceSheet.currentAssets],
    ['Внеоборотные активы', result.balanceSheet.nonCurrentAssets],
    ['Дебиторская задолженность', result.balanceSheet.accountsReceivable],
    ['Запасы', result.balanceSheet.inventory],
    ['Денежные средства', result.balanceSheet.cash],
    ['Совокупные обязательства', result.balanceSheet.totalLiabilities],
    ['Капитал', result.balanceSheet.equity],
  ] as const

  const ratioRows: Array<[string, number, string?]> = [
    ['Коэффициент текущей ликвидности', result.ratios.currentRatio, '≥ 1.5'],
    ['Коэффициент быстрой ликвидности', result.ratios.quickRatio, '≥ 1.0'],
    ['ROA (рентаб. активов)', result.ratios.roa, '—'],
    ['ROE (рентаб. капитала)', result.ratios.roe, '—'],
    ['ROS (рентаб. продаж)', result.ratios.ros, '—'],
    ['Долг / капитал', result.ratios.debtToEquity, '≤ 1.0'],
    ['Оборачиваемость активов', result.ratios.assetTurnover, '—'],
  ]

  const handleDownload = async () => {
    const blob = await downloadReport(result.id)
    if (blob) {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${result.id}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      notify('Отчёт скачан', 'success')
    }
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Детали отчёта</Typography>
          <Button startIcon={<DownloadIcon />} variant="outlined" onClick={handleDownload}>
            Скачать PDF
          </Button>
        </Box>

        <Typography variant="subtitle2" mb={1}>Баланс</Typography>
        <Table size="small" sx={{ mb: 3 }}>
          <TableHead>
            <TableRow>
              <TableCell>Показатель</TableCell>
              <TableCell align="right">Значение</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {balanceRows.map(([label, value]) => (
              <TableRow key={label}>
                <TableCell>{label}</TableCell>
                <TableCell align="right">{formatNumber(value ?? 0)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <Typography variant="subtitle2" mb={1}>Финансовые коэффициенты</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Показатель</TableCell>
              <TableCell align="right">Значение</TableCell>
              <TableCell align="right">Норма</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ratioRows.map(([label, value, norm]) => (
              <TableRow key={label}>
                <TableCell>{label}</TableCell>
                <TableCell align="right">
                  {label.includes('ROA') || label.includes('ROE') || label.includes('ROS')
                    ? formatPercent(value)
                    : formatNumber(value)}
                </TableCell>
                <TableCell align="right">{norm ?? '—'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default ReportDetails
