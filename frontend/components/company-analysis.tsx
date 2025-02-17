import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface AnalysisResult {
  company_name: string
  industry: string
  headquarters: string
  source_documents: string[]
  overview: {
    vision_statement: string
    key_value_proposition: string
    strategic_initiatives: string[]
  }
  financial_highlights: {
    total_revenues: number
    gross_profit: number
    net_income: number
    total_assets: number
    total_liabilities: number
    stockholders_equity: number
  }
  operational_metrics: {
    key_products: string[]
    deployment_scale: string
    efficiency_metrics: {
      gross_margin: number
      net_profit_margin: number
    }
    market_position: string
  }
  investment_requirements: {
    amount_required: number
    funding_sources: string[]
    capital_allocation: Array<{ name: string; value: number }>
  }
  additional_insights: {
    strategic_risks: string[]
    strategic_opportunities: string[]
    comments: string
  }
}

interface CompanyAnalysisProps {
  analysisResult: AnalysisResult
  onNewAnalysis: () => void
}

export function CompanyAnalysis({ analysisResult, onNewAnalysis }: CompanyAnalysisProps) {
  const financialData = [
    { name: "Total Revenues", value: analysisResult.financial_highlights.total_revenues },
    { name: "Gross Profit", value: analysisResult.financial_highlights.gross_profit },
    { name: "Net Income", value: analysisResult.financial_highlights.net_income },
  ]

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(value)
  }

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`
  }

  return (
    <div className="max-w-screen-xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">{analysisResult.company_name} Analysis</h1>
        <Button onClick={onNewAnalysis}>New Analysis</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Company Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm font-medium">Industry</p>
              <p className="text-lg">{analysisResult.industry}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Headquarters</p>
              <p className="text-lg">{analysisResult.headquarters}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Source Documents</p>
              <p className="text-lg">{analysisResult.source_documents.join(", ")}</p>
            </div>
          </div>
          <h3 className="text-lg font-semibold mb-2">Vision Statement</h3>
          <p className="mb-4">{analysisResult.overview.vision_statement}</p>
          <h3 className="text-lg font-semibold mb-2">Key Value Proposition</h3>
          <p className="mb-4">{analysisResult.overview.key_value_proposition}</p>
          <h3 className="text-lg font-semibold mb-2">Strategic Initiatives</h3>
          <ul className="list-disc pl-5">
            {analysisResult.overview.strategic_initiatives.map((initiative, index) => (
              <li key={index}>{initiative}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Financial Highlights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={financialData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip formatter={(value) => formatCurrency(value as number)} />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium">Total Assets</p>
              <p className="text-lg">{formatCurrency(analysisResult.financial_highlights.total_assets)}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Total Liabilities</p>
              <p className="text-lg">{formatCurrency(analysisResult.financial_highlights.total_liabilities)}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Stockholders&apos; Equity</p>
              <p className="text-lg">{formatCurrency(analysisResult.financial_highlights.stockholders_equity)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Operational Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">Key Products/Services</h3>
          <ul className="list-disc pl-5 mb-4">
            {analysisResult.operational_metrics.key_products.map((product, index) => (
              <li key={index}>{product}</li>
            ))}
          </ul>
          <h3 className="text-lg font-semibold mb-2">Deployment Scale</h3>
          <p className="mb-4">{analysisResult.operational_metrics.deployment_scale}</p>
          <h3 className="text-lg font-semibold mb-2">Efficiency Metrics</h3>
          <div className="space-y-2">
            <div>
              <p className="text-sm font-medium">Gross Margin</p>
              <p className="text-lg">
                {formatPercentage(analysisResult.operational_metrics.efficiency_metrics.gross_margin)}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium">Net Profit Margin</p>
              <p className="text-lg">
                {formatPercentage(analysisResult.operational_metrics.efficiency_metrics.net_profit_margin)}
              </p>
            </div>
          </div>
          <h3 className="text-lg font-semibold mt-4 mb-2">Market Position</h3>
          <p>{analysisResult.operational_metrics.market_position}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Investment Requirements</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">Amount Required</h3>
          <p className="mb-4">{formatCurrency(analysisResult.investment_requirements.amount_required)}</p>
          <h3 className="text-lg font-semibold mb-2">Funding Sources</h3>
          <ul className="list-disc pl-5 mb-4">
            {analysisResult.investment_requirements.funding_sources.map((source, index) => (
              <li key={index}>{source}</li>
            ))}
          </ul>
          <h3 className="text-lg font-semibold mb-2">Capital Allocation</h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={analysisResult.investment_requirements.capital_allocation}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(value) => formatCurrency(value)} />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip formatter={(value) => formatCurrency(value as number)} />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Additional Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">Strategic Risks</h3>
          <ul className="list-disc pl-5 mb-4">
            {analysisResult.additional_insights.strategic_risks.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
          <h3 className="text-lg font-semibold mb-2">Strategic Opportunities</h3>
          <ul className="list-disc pl-5 mb-4">
            {analysisResult.additional_insights.strategic_opportunities.map((opportunity, index) => (
              <li key={index}>{opportunity}</li>
            ))}
          </ul>
          <h3 className="text-lg font-semibold mb-2">Comments</h3>
          <p>{analysisResult.additional_insights.comments}</p>
        </CardContent>
      </Card>
    </div>
  )
}

