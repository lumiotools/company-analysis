"use client";

import type React from "react";
import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, Edit2, Save } from "lucide-react";
import { Input } from "@/components/ui/input";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { FundAnalysis } from "./page";

// Helper function to display null or empty values
const formatValue = (value: unknown): string => {
  if (value === null || value === undefined || value === "") {
    return "Not Found";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
};

// Helper function to display array values
const formatArrayValue = (array: unknown[]): string => {
  if (!array || array.length === 0) {
    return "Not Found";
  }

  return array.join(", ");
};

interface FundDetailsViewProps {
  fundData: FundAnalysis;
  onUpdate: (updatedFund: FundAnalysis) => void;
}

const FundDetailsView: React.FC<FundDetailsViewProps> = ({
  fundData,
  onUpdate,
}) => {
  const [editableFields, setEditableFields] = useState<Record<string, string>>(
    {}
  );
  const [isEditing, setIsEditing] = useState<Record<string, boolean>>({});
  const [isPrinting, setIsPrinting] = useState(false);
  const portfolioDetailsRef = useRef<HTMLDetailsElement>(null);

  if (!fundData) return <div>No fund data available</div>;

  const { fund } = fundData;

  const handleEdit = (fieldPath: string) => {
    // Get the current value from the nested path
    const pathParts = fieldPath.split(".");
    let currentValue: unknown = fund;

    for (const part of pathParts) {
      if (currentValue === null || currentValue === undefined) break;

      // Use type assertion with a Record type instead of 'any'
      currentValue = (currentValue as Record<string, unknown>)[part];
    }

    setEditableFields({
      ...editableFields,
      [fieldPath]:
        currentValue === null || currentValue === undefined
          ? ""
          : String(currentValue),
    });
    setIsEditing({
      ...isEditing,
      [fieldPath]: true,
    });
  };

  const handleSave = (fieldPath: string) => {
    // Get the new value from editableFields
    const newValue = editableFields[fieldPath];

    // Create a deep copy of the fund data
    const updatedFund: FundAnalysis = JSON.parse(JSON.stringify(fundData));

    // Update the nested property in the copied fund data
    const pathParts = fieldPath.split(".");
    let current: Record<string, unknown> = updatedFund.fund as Record<
      string,
      unknown
    >;

    // Navigate to the parent object of the field we want to update
    for (let i = 0; i < pathParts.length - 1; i++) {
      if (current[pathParts[i]] === undefined) {
        // Create the object if it doesn't exist
        current[pathParts[i]] = {};
      }
      // Use type assertion to ensure type safety
      current = current[pathParts[i]] as Record<string, unknown>;
    }

    // Update the field with the new value
    current[pathParts[pathParts.length - 1]] = newValue;

    // Call the onUpdate callback with the updated fund data
    if (onUpdate) {
      onUpdate(updatedFund);
    }

    // Update local state
    setIsEditing({
      ...isEditing,
      [fieldPath]: false,
    });
  };

  const handleChange = (fieldPath: string, value: string) => {
    setEditableFields({
      ...editableFields,
      [fieldPath]: value,
    });
  };

  const renderValueWithEdit = (fieldPath: string, value: unknown) => {
    const displayValue = formatValue(value);

    if (isPrinting) {
      return <p className="text-base mt-1">{displayValue}</p>;
    }

    if (isEditing[fieldPath]) {
      return (
        <div className="flex items-center gap-2">
          <Input
            value={editableFields[fieldPath] || ""}
            onChange={(e) => handleChange(fieldPath, e.target.value)}
            className="max-w-xs"
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleSave(fieldPath)}
          >
            <Save className="h-4 w-4 mr-1" />
            Save
          </Button>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2">
        <p className="text-base mt-1">{displayValue}</p>
        {displayValue === "Not Found" && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(fieldPath)}
            className="h-6 px-2"
          >
            <Edit2 className="h-3 w-3 mr-1" />
            Edit
          </Button>
        )}
      </div>
    );
  };

  const downloadAsPDF = async () => {
    setIsPrinting(true);

    if (portfolioDetailsRef.current) {
      portfolioDetailsRef.current.open = false;
    }
    document.getElementById("portfolioName")?.classList.add("hidden");

    setTimeout(async () => {
      const contentElement = document.getElementById("fund-details-content");

      if (!contentElement) {
        console.error("Content element not found");
        setIsPrinting(false);
        return;
      }

      try {
        const pdf = new jsPDF({
          orientation: "portrait",
          unit: "mm",
          format: "a4",
        });

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 10;
        const availableWidth = pageWidth - 2 * margin;

        const addContent = async (
          element: HTMLElement,
          yOffset: number,
          addSpacing = true
        ) => {
          const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            logging: false,
            allowTaint: true,
          });

          const imgData = canvas.toDataURL("image/jpeg", 0.7);
          const imgWidth = availableWidth;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;

          if (yOffset + imgHeight > pageHeight - margin) {
            pdf.addPage();
            yOffset = margin;
          }

          pdf.addImage(imgData, "JPEG", margin, yOffset, imgWidth, imgHeight);
          return yOffset + imgHeight + (addSpacing ? 5 : 0);
        };

        let yOffset = margin;

        // Process all cards including and before portfolio companies
        const cards = contentElement.querySelectorAll(".card");
        let portfolioProcessed = false;
        for (const card of cards) {
          yOffset = await addContent(card as HTMLElement, yOffset);
          if (card.id === "portfolio-companies-card") {
            portfolioProcessed = true;
            break;
          }
        }

        // Process detailed portfolio companies view
        if (portfolioProcessed) {
          const portfolioCompanies = fund.track_record.portfolio_companies;
          if (portfolioCompanies && portfolioCompanies.length > 0) {
            for (let i = 0; i < portfolioCompanies.length; i += 2) {
              const companiesDiv = document.createElement("div");
              companiesDiv.style.display = "grid";
              companiesDiv.style.gridTemplateColumns = "repeat(2, 1fr)";
              companiesDiv.style.gap = "16px";
              companiesDiv.style.padding = "16px";

              const company1 = portfolioCompanies[i];
              const company2 = portfolioCompanies[i + 1];

              const createCompanyHTML = (
                company: (typeof portfolioCompanies)[0]
              ) => `
                <div style="border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                  <h3 style="font-size: 16px; font-weight: bold; margin-bottom: 12px;">${
                    company.name
                  }</h3>
                  <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                    ${Object.entries(company)
                      .filter(([key]) => key !== "name")
                      .map(
                        ([key, value]) => `
                        <div>
                          <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">${key}</div>
                          <div style="font-size: 14px;">${formatValue(
                            value
                          )}</div>
                        </div>
                      `
                      )
                      .join("")}
                  </div>
                </div>
              `;

              companiesDiv.innerHTML = `
                ${createCompanyHTML(company1)}
                ${company2 ? createCompanyHTML(company2) : ""}
              `;

              document.body.appendChild(companiesDiv);
              yOffset = await addContent(companiesDiv, yOffset);
              document.body.removeChild(companiesDiv);
            }
          }
        }

        // Process remaining cards after portfolio companies (Diversity Information and Additional Data)
        let remainingCardsProcessed = false;
        for (const card of cards) {
          if (remainingCardsProcessed) {
            yOffset = await addContent(card as HTMLElement, yOffset);
          }
          if (card.id === "portfolio-companies-card") {
            remainingCardsProcessed = true;
          }
        }

        pdf.save(`${fund.general_information.name || "Fund"}_Details.pdf`);
      } catch (error) {
        console.error("Error generating PDF:", error);
      } finally {
        setIsPrinting(false);
        document.getElementById("portfolioName")?.classList.remove("hidden");

        if (portfolioDetailsRef.current) {
          portfolioDetailsRef.current.open = false;
        }
      }
    }, 100);
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Fund Details</h1>
        <Button onClick={downloadAsPDF} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Download as PDF
        </Button>
      </div>

      <div id="fund-details-content" className="space-y-8">
        {/* General Information */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">General Information</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Fund Name</h4>
                {renderValueWithEdit(
                  "general_information.name",
                  fund.general_information.name
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Location</h4>
                {renderValueWithEdit(
                  "general_information.location",
                  fund.general_information.location
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Website</h4>
                {fund.general_information.website ? (
                  <p className="text-base mt-1">
                    <a
                      href={
                        fund.general_information.website.startsWith("http")
                          ? fund.general_information.website
                          : `https://${fund.general_information.website}`
                      }
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {fund.general_information.website}
                    </a>
                  </p>
                ) : (
                  renderValueWithEdit("general_information.website", null)
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Primary Contact */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Primary Contact</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Name</h4>
                {renderValueWithEdit(
                  "primary_contact.name",
                  fund.primary_contact.name
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Position</h4>
                {renderValueWithEdit(
                  "primary_contact.position",
                  fund.primary_contact.position
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Phone</h4>
                {renderValueWithEdit(
                  "primary_contact.phone",
                  fund.primary_contact.phone
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Email</h4>
                {fund.primary_contact.email ? (
                  <p className="text-base mt-1">
                    <a
                      href={`mailto:${fund.primary_contact.email}`}
                      className="text-blue-600 hover:underline"
                    >
                      {fund.primary_contact.email}
                    </a>
                  </p>
                ) : (
                  renderValueWithEdit("primary_contact.email", null)
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">LinkedIn</h4>
                {renderValueWithEdit(
                  "primary_contact.linkedin",
                  fund.primary_contact.linkedin
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Fundraising Status */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Fundraising Status</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Actively Fundraising
                </h4>
                <p className="text-base mt-1">
                  {fund.fund_details.fundraising_status.actively_fundraising ? (
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      Yes
                    </Badge>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                      No
                    </Badge>
                  )}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Fund Series
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.fund_series",
                  fund.fund_details.fundraising_status.fund_series
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Target Size
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.target_size",
                  fund.fund_details.fundraising_status.target_size
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Cap Size</h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.cap_size",
                  fund.fund_details.fundraising_status.cap_size
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Committed Amount
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.committed_amount",
                  fund.fund_details.fundraising_status.committed_amount
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  First Close Date
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.first_close_date",
                  fund.fund_details.fundraising_status.first_close_date
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Final Close Date
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.final_close_date",
                  fund.fund_details.fundraising_status.final_close_date
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Minimum LP Commitment
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.minimum_lp_commitment",
                  fund.fund_details.fundraising_status.minimum_lp_commitment
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Capital Call Mechanics
                </h4>
                {renderValueWithEdit(
                  "fund_details.fundraising_status.capital_call_mechanics",
                  fund.fund_details.fundraising_status.capital_call_mechanics
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Fees, Terms & Economics */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Fees, Terms & Economics</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Management Fee
                </h4>
                {renderValueWithEdit(
                  "fund_details.fees_terms_economics.management_fee",
                  fund.fund_details.fees_terms_economics.management_fee
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Carried Interest
                </h4>
                {renderValueWithEdit(
                  "fund_details.fees_terms_economics.carried_interest",
                  fund.fund_details.fees_terms_economics.carried_interest
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Total AUM</h4>
                {renderValueWithEdit(
                  "fund_details.fees_terms_economics.total_aum",
                  fund.fund_details.fees_terms_economics.total_aum
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sector & Stage Focus */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Sector & Stage Focus</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Sectors</h4>
                <div className="flex flex-wrap gap-2 mt-2">
                  {fund.fund_details.sector_stage_focus.sectors &&
                  fund.fund_details.sector_stage_focus.sectors.length > 0 ? (
                    fund.fund_details.sector_stage_focus.sectors.map(
                      (sector, index) => (
                        <Badge
                          key={index}
                          className="bg-blue-100 text-blue-800 hover:bg-blue-100"
                        >
                          {sector}
                        </Badge>
                      )
                    )
                  ) : (
                    <div>
                      {renderValueWithEdit(
                        "fund_details.sector_stage_focus.sectors",
                        null
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Stage Focus
                </h4>
                <div className="flex flex-wrap gap-2 mt-2">
                  {fund.fund_details.sector_stage_focus.stage_focus &&
                  fund.fund_details.sector_stage_focus.stage_focus.length >
                    0 ? (
                    fund.fund_details.sector_stage_focus.stage_focus.map(
                      (stage, index) => (
                        <Badge
                          key={index}
                          className="bg-purple-100 text-purple-800 hover:bg-purple-100"
                        >
                          {stage}
                        </Badge>
                      )
                    )
                  ) : (
                    <div>
                      {renderValueWithEdit(
                        "fund_details.sector_stage_focus.stage_focus",
                        null
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Impact Investing
                </h4>
                <p className="text-base mt-1">
                  {fund.fund_details.sector_stage_focus.impact_investing ? (
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      Yes
                    </Badge>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                      No
                    </Badge>
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Investment Strategy */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Investment Strategy</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Preferred Stage
                </h4>
                {fund.fund_details.investment_strategy.preferred_stage &&
                fund.fund_details.investment_strategy.preferred_stage.length >
                  0 ? (
                  <p className="text-base mt-1">
                    {formatArrayValue(
                      fund.fund_details.investment_strategy.preferred_stage
                    )}
                  </p>
                ) : (
                  renderValueWithEdit(
                    "fund_details.investment_strategy.preferred_stage",
                    null
                  )
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Check Size Range
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.check_size_range",
                  fund.fund_details.investment_strategy.check_size_range
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Yearly Investment Cadence
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.yearly_investment_cadence",
                  fund.fund_details.investment_strategy
                    .yearly_investment_cadence
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Target Ownership Percentage
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.target_ownership_percentage",
                  fund.fund_details.investment_strategy
                    .target_ownership_percentage
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Follow-on Reserves
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.follow_on_reserves",
                  fund.fund_details.investment_strategy.follow_on_reserves
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Active Investment Period
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.active_investment_period",
                  fund.fund_details.investment_strategy.active_investment_period
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Portfolio Forecast
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.portfolio_forecast",
                  fund.fund_details.investment_strategy.portfolio_forecast
                )}
              </div>
              <div className="col-span-1 md:col-span-2">
                <h4 className="text-sm font-medium text-gray-500">
                  Target Valuations
                </h4>
                {renderValueWithEdit(
                  "fund_details.investment_strategy.target_valuations",
                  fund.fund_details.investment_strategy.target_valuations
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Governance & Participation */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">
              Governance & Participation
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Board Seat Required
                </h4>
                {renderValueWithEdit(
                  "fund_details.governance_participation.board_seat_required",
                  fund.fund_details.governance_participation.board_seat_required
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Lead Investor Frequency
                </h4>
                {renderValueWithEdit(
                  "fund_details.governance_participation.lead_investor_frequency",
                  fund.fund_details.governance_participation
                    .lead_investor_frequency
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">LP List</h4>
                {fund.fund_details.governance_participation.lp_list &&
                Array.isArray(
                  fund.fund_details.governance_participation.lp_list
                ) &&
                fund.fund_details.governance_participation.lp_list.length >
                  0 ? (
                  <p className="text-base mt-1">
                    {formatArrayValue(
                      fund.fund_details.governance_participation.lp_list
                    )}
                  </p>
                ) : (
                  renderValueWithEdit(
                    "fund_details.governance_participation.lp_list",
                    null
                  )
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Portfolio Companies */}
        {fund.track_record.portfolio_companies &&
          fund.track_record.portfolio_companies.length > 0 && (
            <Card className="card" id="portfolio-companies-card">
              <CardHeader className="bg-gray-50">
                <CardTitle className="text-xl">
                  Portfolio Companies (
                  {fund.track_record.portfolio_companies.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="overflow-x-auto overview-table">
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
                      {fund.track_record.portfolio_companies.map(
                        (company, index) => (
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
                            <TableCell>
                              {formatValue(company.stage_round)}
                            </TableCell>
                            <TableCell>
                              {formatValue(company.post_money_valuation)}
                            </TableCell>
                            <TableCell>{formatValue(company.moic)}</TableCell>
                          </TableRow>
                        )
                      )}
                    </TableBody>
                  </Table>
                </div>

                <div className="mt-6">
                  <details className="group" ref={portfolioDetailsRef}>
                    <summary
                      id="portfolioName"
                      className="cursor-pointer text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                      View Full Portfolio Details
                    </summary>
                    <div className="mt-4 space-y-8">
                      {fund.track_record.portfolio_companies.map(
                        (company, index) => (
                          <div
                            key={index}
                            className="bg-gray-50 p-4 rounded-lg"
                          >
                            <h3 className="text-lg font-semibold mb-3">
                              {formatValue(company.name)}
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {Object.entries(company).map(([key, value]) => (
                                <div key={key}>
                                  <h4 className="text-xs font-medium text-gray-500">
                                    {key}
                                  </h4>
                                  <p className="text-sm">
                                    {formatValue(value)}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </details>
                </div>
              </CardContent>
            </Card>
          )}

        {/* Diversity Information */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Diversity Information</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Minority (BIPOC) Partners
                </h4>
                <p className="text-base mt-1">
                  {fund.diversity_information.minority_partners ? (
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      Yes
                    </Badge>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                      No
                    </Badge>
                  )}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Female Partners
                </h4>
                <p className="text-base mt-1">
                  {fund.diversity_information.female_partners ? (
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      Yes
                    </Badge>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                      No
                    </Badge>
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Additional Data */}
        <Card className="card">
          <CardHeader className="bg-gray-50">
            <CardTitle className="text-xl">Additional Data</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Sourcing Validation
                </h4>
                {renderValueWithEdit(
                  "additional_data.sourcing_validation",
                  fund.additional_data.sourcing_validation
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Due Diligence Scorecard
                </h4>
                {renderValueWithEdit(
                  "additional_data.due_diligence_scorecard",
                  fund.additional_data.due_diligence_scorecard
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Entity Structure
                </h4>
                {renderValueWithEdit(
                  "additional_data.entity_structure",
                  fund.additional_data.entity_structure
                )}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Fund Manager Bio
                </h4>
                {renderValueWithEdit(
                  "additional_data.fund_manager_bio",
                  fund.additional_data.fund_manager_bio
                )}
              </div>
              <div className="col-span-1 md:col-span-2">
                <h4 className="text-sm font-medium text-gray-500">
                  Legal Documents
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
                  <div>
                    <p className="text-xs font-medium text-gray-500">
                      Fund Manager LPA
                    </p>
                    {renderValueWithEdit(
                      "additional_data.legal_documents.fund_manager_lpa",
                      fund.additional_data.legal_documents.fund_manager_lpa
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-500">
                      Subscription Agreement
                    </p>
                    {renderValueWithEdit(
                      "additional_data.legal_documents.subscription_agreement",
                      fund.additional_data.legal_documents
                        .subscription_agreement
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-500">
                      Existing Side Letters
                    </p>
                    {Array.isArray(
                      fund.additional_data.legal_documents.existing_side_letters
                    ) &&
                    fund.additional_data.legal_documents.existing_side_letters
                      .length > 0 ? (
                      <p className="text-sm">
                        {formatArrayValue(
                          fund.additional_data.legal_documents
                            .existing_side_letters
                        )}
                      </p>
                    ) : (
                      renderValueWithEdit(
                        "additional_data.legal_documents.existing_side_letters",
                        null
                      )
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FundDetailsView;
