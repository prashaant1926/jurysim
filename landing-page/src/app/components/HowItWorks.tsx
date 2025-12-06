import Image from 'next/image'

export default function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Upload Case Materials",
      description: "Add exhibits, testimony, or opening statements."
    },
    {
      number: "2",
      title: "Generate AI Jury Pools",
      description: "Tailor pools using real-world traits like political lean, region, and background."
    },
    {
      number: "3",
      title: "Simulate Deliberations",
      description: "Observe how different groups react, argue, and evolve."
    },
    {
      number: "4",
      title: "Identify What Works",
      description: "Compare outcomes and discover persuasive patterns—before you walk into court."
    }
  ]

  return (
    <section className="min-h-screen flex items-center py-32 bg-[#F8F6F4]">
      <div className="container">
        <div className="max-w-6xl mx-auto">
          <div className="text-left mb-20">
            <span className="section-label inline-block mb-6">HOW IT WORKS</span>
            <h2 className="mb-6">How It Works</h2>
          </div>
          
          <div className="grid grid-cols-1 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="process-card group w-full">
                <div className="flex items-start gap-6">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#FF6B35] to-[#F7461E] rounded-full shadow-lg group-hover:shadow-xl transition-all duration-300" style={{ marginBottom: '0' }}>
                      <span className="text-2xl font-bold text-white flex items-center justify-center h-full">{step.number}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-left mb-3 text-xl font-semibold">{step.title}</h3>
                    <p className="text-left text-text-secondary leading-relaxed text-base">{step.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}