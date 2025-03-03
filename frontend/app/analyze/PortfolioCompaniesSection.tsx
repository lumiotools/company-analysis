import type React from "react";
import { useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface Company {
  name: string;
  investment_fund: string;
  amount_invested: number;
  stage_round: string;
  post_money_valuation: number;
  moic: number;
}

interface TrackRecord {
  portfolio_companies: Company[];
}

interface Fund {
  track_record: TrackRecord;
}

interface PortfolioCompaniesSectionProps {
  fund: Fund;
}

const PortfolioCompaniesSection: React.FC<PortfolioCompaniesSectionProps> = ({
  fund,
}) => {
  const portfolioDetailsRef = useRef<HTMLDetailsElement>(null);

  const formatValue = (value: string | number | undefined | null): string => {
    if (typeof value === "number") {
      return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    return value?.toString() || "N/A";
  };

  return (
    <Card className="card" id="portfolio-companies-card">
      <CardHeader className="bg-gray-50">
        <CardTitle className="text-xl">
          Portfolio Companies ({fund.track_record.portfolio_companies.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        {/* Overview Table */}
        <div className="overview-table">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Company</TableHead>
                  <TableHead>Fund</TableHead>
                  <TableHead>Investment</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Valuation</TableHead>
                  <TableHead>MOIC</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fund.track_record.portfolio_companies.map((company, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {formatValue(company.name)}
                    </TableCell>
                    <TableCell>
                      {formatValue(company.investment_fund)}
                    </TableCell>
                    <TableCell>
                      {formatValue(company.amount_invested)}
                    </TableCell>
                    <TableCell>{formatValue(company.stage_round)}</TableCell>
                    <TableCell>
                      {formatValue(company.post_money_valuation)}
                    </TableCell>
                    <TableCell>{formatValue(company.moic)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Detailed View */}
        <div className="mt-6">
          <details className="group" ref={portfolioDetailsRef}>
            <summary className="cursor-pointer text-sm font-medium text-blue-600 hover:text-blue-800">
              View Full Portfolio Details
            </summary>
            <div className="mt-4 space-y-8">
              {fund.track_record.portfolio_companies.map((company, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">
                    {formatValue(company.name)}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(company).map(([key, value]) => (
                      <div key={key}>
                        <h4 className="text-xs font-medium text-gray-500">
                          {key}
                        </h4>
                        <p className="text-sm">{formatValue(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </details>
        </div>
      </CardContent>
    </Card>
  );
};

export default PortfolioCompaniesSection;
