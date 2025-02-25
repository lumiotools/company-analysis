"use client";

import type React from "react";

import { useState } from "react";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { CompanyAnalysis } from "@/components/company-analysis";
import { Card, CardContent } from "@/components/ui/card";
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

export default function AnalyzePage() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );

  // const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   if (event.target.files) {
  //     setFiles((prevFiles) => [
  //       ...prevFiles,
  //       ...Array.from(event.target.files || []),
  //     ]);
  //   }
  // };

  // const removeFile = (index: number) => {
  //   setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  // };

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
        `${process.env.NEXT_PUBLIC_API_URL}/api/analyze`,
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
  };

  const hostUrl = process.env.NEXT_PUBLIC_FILE_SERVER_HOST;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Analyze Company Documents
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
              <form onSubmit={handleSubmit}>
                <Button className="mx-auto" onClick={handleSubmit}>
                  Start Analysis
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          <CompanyAnalysis
            analysisResult={analysisResult}
            onNewAnalysis={handleNewAnalysis}
          />
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
