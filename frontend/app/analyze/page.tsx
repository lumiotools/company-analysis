/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import type React from "react";

import { useState } from "react";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { CompanyAnalysis } from "@/components/company-analysis";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { LoadingPopup } from "@/components/loading-popup";
import {
  FileManagerComponent,
  Inject,
  NavigationPane,
  DetailsView,
  Toolbar,
} from "@syncfusion/ej2-react-filemanager";
import { registerLicense } from "@syncfusion/ej2-base";
import { Button } from "@/components/ui/button";
registerLicense(process.env.NEXT_PUBLIC_SYNCFUSION_LICENSE_KEY as string);
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface AnalysisResult {
  company_name: string;
  industry: string;
  headquarters: string;
  source_documents: string[];
  overview: {
    vision_statement: string;
    key_value_proposition: string;
    strategic_initiatives: string[];
  };
  financial_highlights: {
    total_revenues: number;
    gross_profit: number;
    net_income: number;
    total_assets: number;
    total_liabilities: number;
    stockholders_equity: number;
  };
  operational_metrics: {
    key_products: string[];
    deployment_scale: string;
    efficiency_metrics: {
      gross_margin: number;
      net_profit_margin: number;
    };
    market_position: string;
  };
  investment_requirements: {
    amount_required: number;
    funding_sources: string[];
    capital_allocation: Array<{ name: string; value: number }>;
  };
  additional_insights: {
    strategic_risks: string[];
    strategic_opportunities: string[];
    comments: string;
  };
}

// Updated interface for the API response
// Interface for fund analysis document structure
interface FundAnalysis {
  "GENERAL FUND INFORMATION": {
    "Fund Name": string;
    "Fund Location": string;
    "Fund Website URL": string;
  };
  "PRIMARY CONTACT INFORMATION": {
    "Primary Contact Name": string;
    "Primary Contact Position": string;
    "Primary Contact Phone Number": string | null;
    "Primary Contact Email": string;
    "Primary Contact LinkedIn URL": string;
  };
  "FUND-SPECIFIC DETAILS (CURRENT FUND)": {
    "Fundraising Status & Timing": {
      "Currently Fundraising": boolean;
      "Current Fund Number": string;
      "Fund Size (Target & Cap)": string;
      "Already Closed / Committed Amount": string;
      "First Close Date": string;
      "Expected Final Close Date": string;
      "Minimum LP Commitment": string;
      "Capital Call Mechanics": string;
    };
    "Fees, Terms, and Economics": {
      "Management Fee Percentage": number;
      "Carried Interest Percentage": number;
      "Total AUM (for the GP)": string;
    };
    "Sector & Stage Focus": {
      "Sector Preference / Focus": string;
      "Stage Focus": string;
      "Impact Investing": boolean;
    };
    "Investment Strategy": {
      "Preferred Investment Stage": string;
      "Check Size Range": string;
      "Yearly Investment Cadence": number;
      "Target Ownership Percentage": number;
      "Follow-On Reserves": boolean;
      "Active Investment Period": string;
      "Portfolio Company Investment Forecast": string;
      "Target Valuations": string;
    };
    "Governance & Participation": {
      "Board Seat Requests": boolean;
      "Lead Investor Frequency": boolean;
      "LP List": string[];
    };
  };
  "TRACK RECORD (PORTFOLIO COMPANIES)": Array<{
    "Portfolio Company Name"?: string;
    "Company URL"?: string;
    "Investment Fund/Source"?: string;
    "Amount Invested"?: string;
    "Post-Money Valuation"?: string;
    "Stage/Round"?: string;
    "Form of Financing"?: string;
    "Unrealized Value"?: string;
    "Distributed Value"?: string;
    "Total Value"?: string;
    DPI?: number;
    MOIC?: number;
    IRR?: number;
    "Highlighted Co-Investors"?: string[];
  }>;
  "DIVERSITY INFORMATION": {
    "Minority (BIPOC) Partners in GP": boolean;
    "Female Partners in GP": boolean;
  };
  "PAST FUNDS / INVESTMENT VEHICLES": Record<string, unknown>[];
  "ADDITIONAL / MISCELLANEOUS DATA POINTS": {
    "Validation/Proof Cases of Sourcing Methodology": null | string;
    "Due Diligence Scorecard": null | string;
    "Entity Structure": string;
    "Creator of Fund Manager's LPA": string | null;
    "Creator of Subscription Agreement": string | null;
    "Existing Side Letters": boolean;
    "Fund Manager Bio/Career Summary": null | string;
  };
}

interface ApiResponse {
  success: boolean;
  excel: FundData[];
  doc: {
    analysis: FundAnalysis[];
  };
}

type FundData = Record<string, string | number | boolean | null>;

export default function AnalyzePage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [excelData, setExcelData] = useState<FundData[]>([]);
  const [loading, setLoading] = useState(false);
  const handleAnalysisLog = (): string | null => {
    const fileManagerInstance =
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (document.getElementById("overview_file") as any)?.ej2_instances?.[0];

    if (fileManagerInstance) {
      const selectedItems = fileManagerInstance.selectedItems;

      if (selectedItems && selectedItems.length > 0) {
        console.log("Selected item:", selectedItems[0]);

        if (selectedItems.length > 1) {
          console.log(
            "Multiple items selected. Only the first one will be processed."
          );
        }

        return selectedItems[0]; // Return the directory name
      } else {
        console.log("No item selected");
      }
    } else {
      console.log("FileManager instance not found");
    }

    return null; // Return null if no selection
  };
  const handleAnalysisSubmit = async () => {
    setLoading(true);

    try {
      const directoryName = handleAnalysisLog(); // Get the selected directory name

      if (!directoryName) {
        console.error("No directory selected.");
        setLoading(false);
        return;
      }

      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL
        }/api/analyze?directory_name=${encodeURIComponent(directoryName)}`,
        {
          method: "POST",
        }
      );

      const result: ApiResponse = await response.json();
      if (result.success && result.excel) {
        if (result.success && result.excel) {
          setExcelData((prevData) => {
            // If previous data exists, append new data
            if (prevData && prevData.length > 0) {
              return [...prevData, ...result.excel];
            }
            // Otherwise, just use the new data
            return result.excel;
          });
        }
      }
    } catch (error) {
      console.error("Error fetching analysis:", error);
    }

    setLoading(false);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log("button clicked");
    if (files.length === 0) {
      console.log("returned");
      return;
    }

    setIsLoading(true);
    setLoadingProgress(0);

    const messages = [
      "Uploading documents...",
      "Reading and processing documents...",
      "Extracting insights...",
      "Analyzing financial data...",
      "Evaluating market position...",
      "Generating comprehensive report...",
    ];

    let messageIndex = 0;
    const startTime = Date.now();

    const updateLoading = () => {
      const elapsedTime = (Date.now() - startTime) / 1000; // time in seconds
      const progress = Math.min(100, 100 * (1 - Math.exp(-elapsedTime / 30))); // exponential progress
      setLoadingProgress(progress);
      setLoadingMessage(messages[messageIndex]);
      messageIndex = (messageIndex + 1) % messages.length;
    };

    const loadingInterval = setInterval(updateLoading, 2000);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });

      // Replace this with your actual API endpoint
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analyze2`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();
      if (data.success && data.text) {
        setAnalysisResult(data.text);
      } else {
        throw new Error("Invalid API response");
      }
    } catch (error) {
      console.error("Error during analysis:", error);
      // Handle error (e.g., show error message to user)
    } finally {
      clearInterval(loadingInterval);
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setFiles([]);
    setAnalysisResult(null);
    setExcelData([]);
  };

  const hostUrl = process.env.NEXT_PUBLIC_FILE_SERVER_HOST;

  // Get all possible field names from all objects in excelData
  const getFieldNames = () => {
    if (!excelData || excelData.length === 0) return [];
    const fieldSet = new Set<string>();
    excelData.forEach((fund) => {
      Object.keys(fund).forEach((key) => fieldSet.add(key));
    });
    return Array.from(fieldSet);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Analyze Fund Data
        </h1>
        {!analysisResult ? (
          <Card className="max-w-screen-xl mx-auto">
            <CardContent className="pt-6 space-y-4 flex flex-col">
              <FileManagerComponent
                className="rounded-lg overflow-hidden"
                id="overview_file"
                ajaxSettings={{
                  url: hostUrl,
                  uploadUrl: hostUrl + "/Upload",
                  downloadUrl: hostUrl + "/Download",
                  getImageUrl: hostUrl + "/GetImage",
                }}
                uploadSettings={{
                  directoryUpload: true, // Enable folder (directory) upload
                  maxFileSize: 100000000, // 100MB
                }}
                style={{
                  color: "red",
                }}
                toolbarSettings={{
                  items: [
                    "NewFolder",
                    "SortBy",
                    "Cut",
                    "Copy",
                    "Paste",
                    "Delete",
                    "Refresh",
                    "Download",
                    "Rename",
                    "Selection",
                    "View",
                    "Details",
                  ],
                }}
                contextMenuSettings={{
                  file: [
                    "Cut",
                    "Copy",
                    "|",
                    "Delete",
                    "Download",
                    "Rename",
                    "|",
                    "Details",
                  ],
                  layout: [
                    "SortBy",
                    "View",
                    "Refresh",
                    "|",
                    "Paste",
                    "|",
                    "NewFolder",
                    "|",
                    "Details",
                    "|",
                    "SelectAll",
                  ],
                  visible: true,
                }}
                view={"Details"}
              >
                <Inject services={[NavigationPane, DetailsView, Toolbar]} />
              </FileManagerComponent>
              <Button
                className="mx-auto"
                onClick={handleAnalysisSubmit}
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Start Analysis"}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <CompanyAnalysis
            analysisResult={analysisResult}
            onNewAnalysis={handleNewAnalysis}
          />
        )}

        {excelData && excelData.length > 0 && (
          <Card className="w-full mt-8 overflow-hidden">
            <CardHeader>
              <h2 className="text-2xl font-bold">Fund Data Analysis</h2>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="font-bold">Fund</TableHead>
                      {getFieldNames().map((field) => (
                        <TableHead key={field} className="min-w-40 font-medium">
                          {field}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {excelData.map((fund, fundIndex) => (
                      <TableRow key={fundIndex}>
                        <TableCell className="font-medium bg-gray-50">
                          {fund["Fund Manager"]
                            ? fund["Fund Manager"].toString()
                            : `Fund ${fundIndex + 1}`}
                        </TableCell>
                        {getFieldNames().map((field) => (
                          <TableCell key={field}>
                            {fund[field] !== null && fund[field] !== undefined
                              ? typeof fund[field] === "boolean"
                                ? fund[field]
                                  ? "Yes"
                                  : "No"
                                : fund[field].toString()
                              : "N/A"}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
      <LoadingPopup
        isOpen={isLoading}
        progress={loadingProgress}
        message={loadingMessage}
      />
      <Footer />
    </div>
  );
}
