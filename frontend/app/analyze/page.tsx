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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AnalysisProgress from "@/components/AnalysisProgress";
import FundDetailsView from "./FundDetailsView";

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
export interface FundAnalysis {
  fund: {
    general_information: {
      name: string;
      location: string;
      website: string | null;
    };
    primary_contact: {
      name: string;
      position: string;
      phone: string | null;
      email: string;
      linkedin: string | null;
    };
    fund_details: {
      fundraising_status: {
        actively_fundraising: boolean;
        fund_series: string;
        target_size: string;
        cap_size: string | null;
        committed_amount: string;
        first_close_date: string;
        final_close_date: string;
        minimum_lp_commitment: string | null;
        capital_call_mechanics: string | null;
      };
      fees_terms_economics: {
        management_fee: string;
        carried_interest: string;
        total_aum: string | null;
      };
      sector_stage_focus: {
        sectors: string[];
        stage_focus: string[];
        impact_investing: boolean;
      };
      investment_strategy: {
        preferred_stage: string[];
        check_size_range: string;
        yearly_investment_cadence: number | null;
        target_ownership_percentage: string;
        follow_on_reserves: string;
        active_investment_period: string;
        portfolio_forecast: string | null;
        target_valuations: string | null;
      };
      governance_participation: {
        board_seat_required: boolean;
        lead_investor_frequency: boolean;
        lp_list: string[];
      };
    };
    track_record: {
      portfolio_companies: Array<{
        name: string;
        url: string | null;
        investment_fund: string;
        amount_invested: string;
        post_money_valuation: string;
        stage_round: string;
        form_of_financing: string;
        unrealized_value: string | null;
        distributed_value: string | null;
        total_value: string | null;
        dpi: number | null;
        moic: number;
        irr: number | null;
        co_investors: string[];
      }>;
    };
    diversity_information: {
      minority_partners: boolean;
      female_partners: boolean;
    };
    past_funds: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      funds: any[] | null;
    };
    additional_data: {
      sourcing_validation: string | null;
      due_diligence_scorecard: string | null;
      entity_structure: string | null;
      legal_documents: {
        fund_manager_lpa: string | null;
        subscription_agreement: string | null;
        existing_side_letters: string | null;
      };
      fund_manager_bio: string;
    };
  };
}

interface ApiResponse {
  success: boolean;
  excel: FundData[];
  doc: {
    fund: FundAnalysis["fund"];
  };
  time_taken_seconds: number;
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
  const [docData, setDocData] = useState<FundAnalysis[]>([]);
  const [selectedFundIndex, setSelectedFundIndex] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<string>("excel");
  const [activeFundName, setActiveFundName] = useState("");
  const [timeTaken, setTimeTaken] = useState(0); // Time in seconds, 0 means not started

  const selectedFund =
    docData && docData.length > 0 ? docData[selectedFundIndex] : null;
  const handleFundUpdate = (updatedFund: FundAnalysis) => {
    // Create a new array with the updated fund
    const updatedDocData = [...docData];
    updatedDocData[selectedFundIndex] = updatedFund;

    // Update the state with the new array
    setDocData(updatedDocData);
  };
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
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    // Only display minutes if there are any
    if (mins > 0) {
      return `${mins}min ${secs.toFixed(2)} seconds`;
    } else {
      return `${secs.toFixed(2)} seconds`;
    }
  };
  const handleAnalysisSubmit = async () => {
    setLoading(true);

    try {
      const directoryName = handleAnalysisLog(); // Get the selected directory name
      setActiveFundName(directoryName || "");

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
      if (result.success) {
        if (result.excel) {
          setExcelData((prevData) => {
            // If previous data exists, append new data
            if (prevData && prevData.length > 0) {
              return [...prevData, ...result.excel];
            }
            // Otherwise, just use the new data
            return result.excel;
          });
        }
        setTimeTaken(result.time_taken_seconds);

        // Also handle doc data if it exists
        if (result.doc && result.doc.fund) {
          setDocData((prevDocData) => {
            const newFundAnalysis: FundAnalysis = {
              fund: result.doc.fund,
            };

            // If previous doc data exists, append new data
            if (prevDocData && prevDocData.length > 0) {
              return [...prevDocData, newFundAnalysis];
            }
            // Otherwise, just use the new data
            return [newFundAnalysis];
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
    setDocData([]);
    setSelectedFundIndex(0);
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
                  maxFileSize: 10000000000, // 100MB
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
              {!loading ? (
                <Button
                  className="mx-auto"
                  onClick={handleAnalysisSubmit}
                  disabled={loading}
                >
                  Start Analysis
                </Button>
              ) : (
                <AnalysisProgress fundName={activeFundName} />
              )}
              {!isLoading && timeTaken > 0 && (
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p className="text-lg font-medium">
                    Total time taken:{" "}
                    <span className="font-bold">{formatTime(timeTaken)}</span>
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <CompanyAnalysis
            analysisResult={analysisResult}
            onNewAnalysis={handleNewAnalysis}
          />
        )}

        {(excelData.length > 0 || docData.length > 0) && (
          <div className="mt-8">
            <Tabs
              defaultValue="excel"
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Fund Data Analysis</h2>
                <TabsList>
                  <TabsTrigger value="excel" disabled={excelData.length === 0}>
                    Excel Analysis
                  </TabsTrigger>
                  <TabsTrigger value="doc" disabled={docData.length === 0}>
                    Document Analysis
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="excel" className="mt-0">
                <Card className="w-full overflow-hidden">
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="font-bold">Fund</TableHead>
                            {getFieldNames().map((field) => (
                              <TableHead
                                key={field}
                                className={`font-medium ${
                                  field === "Summary" ? "min-w-96" : "min-w-40"
                                }`}
                              >
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
                                  {fund[field] !== null &&
                                  fund[field] !== undefined
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
              </TabsContent>

              <TabsContent value="doc" className="mt-0">
                <Card className="w-full overflow-hidden">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <h3 className="text-xl font-semibold">Fund Details</h3>
                    <Select
                      onValueChange={(value) => {
                        const index = parseInt(value, 10);
                        setSelectedFundIndex(index);
                      }}
                      defaultValue="0"
                    >
                      <SelectTrigger className="w-[220px]">
                        <SelectValue placeholder="Select a fund" />
                      </SelectTrigger>
                      <SelectContent>
                        {docData.map((fundAnalysis, index) => (
                          <SelectItem key={index} value={index.toString()}>
                            {fundAnalysis.fund.general_information.name ||
                              `Fund ${index + 1}`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </CardHeader>
                  <CardContent className="p-6">
                    {selectedFund && (
                      <FundDetailsView
                        fundData={selectedFund}
                        onUpdate={handleFundUpdate}
                      />
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
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
