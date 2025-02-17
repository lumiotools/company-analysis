import { Card, CardContent } from "@/components/ui/card"
import { BuildingIcon, EyeIcon, LineChartIcon, BarChartIcon, DatabaseIcon, BriefcaseIcon } from 'lucide-react'

export function Features() {
  const features = [
    {
      icon: BuildingIcon,
      title: "Basic Information",
      description: "Comprehensive company profile including structure, history, and key personnel",
      color: "bg-blue-500/10 text-blue-600",
    },
    {
      icon: EyeIcon,
      title: "Overview & Vision",
      description: "Strategic direction, mission statement, and long-term objectives",
      color: "bg-indigo-500/10 text-indigo-600",
    },
    {
      icon: LineChartIcon,
      title: "Financial Highlights",
      description: "Key financial metrics, performance trends, and growth indicators",
      color: "bg-violet-500/10 text-violet-600",
    },
    {
      icon: BarChartIcon,
      title: "Operational Metrics",
      description: "Business performance indicators and operational efficiency metrics",
      color: "bg-purple-500/10 text-purple-600",
    },
    {
      icon: DatabaseIcon,
      title: "Investment Requirements",
      description: "Capital needs assessment and investment opportunity analysis",
      color: "bg-fuchsia-500/10 text-fuchsia-600",
    },
    {
      icon: BriefcaseIcon,
      title: "Additional Insights",
      description: "Market positioning, competitive analysis, and growth opportunities",
      color: "bg-pink-500/10 text-pink-600",
    },
  ]

  return (
    <section className="py-24" id="features">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Comprehensive Analysis</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Our AI platform provides detailed insights across six key dimensions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="border-2 border-gray-100 dark:border-gray-800 hover:border-primary/50 transition-colors"
            >
              <CardContent className="pt-6">
                <div
                  className={`w-12 h-12 ${feature.color} rounded-xl flex items-center justify-center mb-6`}
                >
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
