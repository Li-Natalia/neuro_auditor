"""Analysis Pydantic schemas."""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class BalanceSheetSchema(BaseModel):
    totalAssets: float = 0
    currentAssets: float = 0
    nonCurrentAssets: float = 0
    totalLiabilities: float = 0
    currentLiabilities: float = 0
    equity: float = 0
    inventory: Optional[float] = None
    accountsReceivable: Optional[float] = None
    cash: Optional[float] = None


class IncomeStatementSchema(BaseModel):
    revenue: float = 0
    costOfSales: float = 0
    grossProfit: float = 0
    operatingExpenses: float = 0
    operatingProfit: float = 0
    netProfit: float = 0
    interestExpense: Optional[float] = None


class CashFlowStatementSchema(BaseModel):
    operatingCashFlow: float = 0
    investingCashFlow: float = 0
    financingCashFlow: float = 0
    netCashFlow: float = 0


class FinancialRatiosSchema(BaseModel):
    currentRatio: float = 0
    quickRatio: float = 0
    roa: float = 0
    roe: float = 0
    ros: float = 0
    debtToEquity: float = 0
    assetTurnover: float = 0


class RiskOut(BaseModel):
    id: int
    level: str
    title: str
    description: str
    recommendation: str
    metric: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None


class AnalysisResultSchema(BaseModel):
    id: int
    documentId: int
    createdAt: datetime
    balanceSheet: BalanceSheetSchema
    incomeStatement: IncomeStatementSchema
    cashFlowStatement: CashFlowStatementSchema
    ratios: FinancialRatiosSchema
    risks: List[RiskOut] = []
    summary: str = ""


class AnalysisSummarySchema(BaseModel):
    totalDocuments: int
    totalRisks: int
    criticalRisks: int
    averageRiskScore: float
    trend: List[Any] = []


def analysis_to_out(a) -> AnalysisResultSchema:
    """Convert SQLAlchemy Analysis model to AnalysisResultSchema."""
    bs = a.balance_sheet or {}
    inc = a.income_statement or {}
    cf = a.cash_flow_statement or {}
    rat = a.ratios or {}

    risks = []
    for r in (a.risks or []):
        risks.append(RiskOut(
            id=r.id,
            level=r.level.value if hasattr(r.level, "value") else str(r.level),
            title=r.title,
            description=r.description,
            recommendation=r.recommendation,
            metric=r.metric,
            value=r.value,
            threshold=r.threshold,
        ))

    return AnalysisResultSchema(
        id=a.id,
        documentId=a.document_id,
        createdAt=a.created_at,
        balanceSheet=BalanceSheetSchema(**{k: bs.get(k, 0) for k in BalanceSheetSchema.model_fields}),
        incomeStatement=IncomeStatementSchema(**{k: inc.get(k, 0) for k in IncomeStatementSchema.model_fields}),
        cashFlowStatement=CashFlowStatementSchema(**{k: cf.get(k, 0) for k in CashFlowStatementSchema.model_fields}),
        ratios=FinancialRatiosSchema(**{k: rat.get(k, 0) for k in FinancialRatiosSchema.model_fields}),
        risks=risks,
        summary=a.summary or "",
    )
