import { Grid, Card, CardContent, Typography } from '@mui/material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  RadialBarChart,
  RadialBar,
} from 'recharts'
import type { AnalysisResult } from '../../types/analysis.types'
import { palette } from '../../themes/tokens'
import { formatNumber } from '../../utils/formatters'

interface Props {
  result: AnalysisResult
}

export function FinancialCharts({ result }: Props) {
  const { balanceSheet, incomeStatement, ratios, risks } = result

  const assetData = [
    { name: 'Оборотные', value: balanceSheet.currentAssets },
    { name: 'Внеоборотные', value: balanceSheet.nonCurrentAssets },
  ]
  const incomeData = [
    { name: 'Выручка', value: incomeStatement.revenue },
    { name: 'Вал. прибыль', value: incomeStatement.grossProfit },
    { name: 'Опер. прибыль', value: incomeStatement.operatingProfit },
    { name: 'Чистая', value: incomeStatement.netProfit },
  ]
  const riskData = [
    { name: 'Критич.', value: risks.filter((r) => r.level === 'critical').length, color: palette.error },
    { name: 'Средние', value: risks.filter((r) => r.level === 'medium').length, color: palette.warning },
    { name: 'Низкие', value: risks.filter((r) => r.level === 'low').length, color: palette.success },
  ]
  const ratioData = [
    { name: 'Тек. ликв.', value: ratios.currentRatio, fill: palette.primary },
    { name: 'Быстр. ликв.', value: ratios.quickRatio, fill: palette.secondary },
    { name: 'ROA %', value: ratios.roa, fill: palette.success },
    { name: 'ROE %', value: ratios.roe, fill: palette.info },
  ]

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" mb={2}>Структура активов</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={assetData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v: number) => formatNumber(v)} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {assetData.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? palette.primary : palette.secondary} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" mb={2}>Отчёт о прибылях и убытках</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={incomeData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v: number) => formatNumber(v)} />
                <Bar dataKey="value" fill={palette.primary} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" mb={2}>Распределение рисков</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={90} label>
                  {riskData.map((d, i) => (
                    <Cell key={i} fill={d.color} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" mb={2}>Финансовые коэффициенты</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <RadialBarChart innerRadius="20%" outerRadius="100%" data={ratioData} startAngle={90} endAngle={-270}>
                <RadialBar dataKey="value" cornerRadius={8} background />
                <Tooltip formatter={(v: number) => formatNumber(v)} />
                <Legend />
              </RadialBarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )
}

export default FinancialCharts
