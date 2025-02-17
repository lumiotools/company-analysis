import { ArrowRightIcon } from 'lucide-react'

export function ProcessFlow() {
  const steps = [
    {
      title: "Document Upload",
      description: "Upload financial documents, earning calls transcripts, and company reports",
      color: "bg-blue-500",
    },
    {
      title: "AI Analysis",
      description: "Our advanced AI processes and analyzes your documents across multiple dimensions",
      color: "bg-indigo-500",
    },
    {
      title: "Comprehensive Insights",
      description: "Receive detailed analysis covering financials, operations, strategy and more",
      color: "bg-violet-500",
    },
  ]

  return (
    <section className="py-24 bg-[#184678]" id="process">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4 text-white">How It Works</h2>
          <p className="text-xl text-white/80 max-w-2xl mx-auto">
            A simple three-step process to unlock valuable insights about your company
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="text-center">
                <div
                  className={`w-16 h-16 ${step.color} rounded-2xl flex items-center justify-center mx-auto mb-6 transform -rotate-12`}
                >
                  <span className="text-2xl font-bold text-white">{index + 1}</span>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-white">{step.title}</h3>
                <p className="text-white/80">{step.description}</p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-24 right-0 transform translate-x-1/2">
                  <ArrowRightIcon className="text-[#ffda54] w-8 h-8" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
