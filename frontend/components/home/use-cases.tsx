import { Card, CardContent } from "@/components/ui/card"
import { BarChartIcon, SearchIcon, TrendingUpIcon } from 'lucide-react'

export function UseCases() {
  const cases = [
    {
      title: "Financial Analysis",
      description: "Deep dive into financial statements and performance metrics",
      icon: BarChartIcon,
    },
    {
      title: "Market Research",
      description: "Analyze market trends and competitive landscape",
      icon: SearchIcon,
    },
    {
      title: "Growth Strategy",
      description: "Identify opportunities and optimize business strategy",
      icon: TrendingUpIcon,
    },
  ]

  return (
    <section className="py-20 bg-secondary/20" id="use-cases">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Use Cases</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Discover how our AI-powered platform can help your business grow
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {cases.map((useCase, index) => (
            <Card key={index} className="border-none shadow-none bg-background">
              <CardContent className="pt-6">
                <useCase.icon className="h-12 w-12 text-primary mb-4" />
                <h3 className="text-xl font-semibold mb-2">{useCase.title}</h3>
                <p className="text-muted-foreground">{useCase.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
