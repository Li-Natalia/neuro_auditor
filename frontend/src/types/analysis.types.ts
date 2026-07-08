import type { RiskLevel } from '../utils/constants'

export interface BalanceSheet {
  totalAssets: number
  currentAssets: number
  nonCurrentAssets: number
  totalLiabilities: number
  currentLiabilities: number
  equity: number
  inventory?: number
  accountsReceivable?: number
  cash?: number
}

export interface IncomeStatement {
  revenue: number
  costOfSales: number
  grossProfit: number
  operatingExpenses: number
  operatingProfit: number
  netProfit: number
  interestExpense?: number
}

export interface CashFlowStatement {
  operatingCashFlow: number
  investingCashFlow: number
  financingCashFlow: number
  netCashFlow: number
}

export interface FinancialRatios {
  currentRatio: number
  quickRatio: number
  roa: number
  roe: number
  ros: number
  debtToEquity: number
  assetTurnover: number
}

export interface Risk {
  id: number
  level: RiskLevel
  title: string
  description: string
  recommendation: string
  metric?: string
  value?: number
  threshold?: number
}

export interface AnalysisResult {
  id: number
  documentId: number
  createdAt: string
  balanceSheet: BalanceSheet
  incomeStatement: IncomeStatement
  cashFlowStatement: CashFlowStatement
  ratios: FinancialRatios
  risks: Risk[]
  summary: string
}

export interface AnalysisSummary {
  totalDocuments: number
  totalRisks: number
  criticalRisks: number
  averageRiskScore: number
  trend: { period: string; value: number }[]
}
