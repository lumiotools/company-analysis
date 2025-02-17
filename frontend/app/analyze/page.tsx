"use client";

import type React from "react";

import { useState } from "react";
import { Header } from "@/components/common/header";
import { Footer } from "@/components/common/footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, X } from "lucide-react";
import { CompanyAnalysis } from "@/components/company-analysis";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingPopup } from "@/components/loading-popup";

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

export default function AnalyzePage() {
  const [files, setFiles] = useState<File[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState("")
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles((prevFiles) => [...prevFiles, ...Array.from(event.target.files || [])])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (files.length === 0) return

    setIsLoading(true)
    setLoadingProgress(0)

    const messages = [
      "Uploading documents...",
      "Reading and processing documents...",
      "Extracting insights...",
      "Analyzing financial data...",
      "Evaluating market position...",
      "Generating comprehensive report..."
    ]

    let messageIndex = 0
    const startTime = Date.now()

    const updateLoading = () => {
      const elapsedTime = (Date.now() - startTime) / 1000 // time in seconds
      const progress = Math.min(100, 100 * (1 - Math.exp(-elapsedTime / 30))) // exponential progress
      setLoadingProgress(progress)
      setLoadingMessage(messages[messageIndex])
      messageIndex = (messageIndex + 1) % messages.length
    }

    const loadingInterval = setInterval(updateLoading, 2000)

    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      // Replace this with your actual API endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      const data = await response.json()
      if (data.success && data.text) {
        setAnalysisResult(data.text)
      } else {
        throw new Error('Invalid API response')
      }
    } catch (error) {
      console.error('Error during analysis:', error)
      // Handle error (e.g., show error message to user)
    } finally {
      clearInterval(loadingInterval)
      setIsLoading(false)
    }
  }

  const handleNewAnalysis = () => {
    setFiles([])
    setAnalysisResult(null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8 text-center">Analyze Company Documents</h1>
        {!analysisResult ? (
          <Card className="max-w-md mx-auto">
            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="dropzone-file"
                    className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-10 h-10 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">PDF, DOC, DOCX or TXT (MAX. 20MB per file)</p>
                    </div>
                    <Input
                      id="dropzone-file"
                      type="file"
                      className="hidden"
                      onChange={handleFileChange}
                      accept=".pdf,.doc,.docx,.txt"
                      multiple
                    />
                  </label>
                </div>
                {files.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-sm font-medium text-gray-900">Selected files:</h3>
                    <ul className="mt-2 divide-y divide-gray-200">
                      {files.map((file, index) => (
                        <li key={index} className="py-2 flex justify-between items-center">
                          <span className="text-sm text-gray-500">{file.name}</span>
                          <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(index)}>
                            <X className="h-4 w-4" />
                          </Button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <Button type="submit" className="w-full" disabled={files.length === 0 || isLoading}>
                  Start Analysis
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          <CompanyAnalysis analysisResult={analysisResult} onNewAnalysis={handleNewAnalysis} />
        )}
      </main>
      <LoadingPopup isOpen={isLoading} progress={loadingProgress} message={loadingMessage} />
      <Footer />
    </div>
  )
}
