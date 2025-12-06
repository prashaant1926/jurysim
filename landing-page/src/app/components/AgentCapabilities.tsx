import React from 'react'

export default function AgentCapabilities() {
  const capabilities = [
    {
      title: "Unconscious Bias",
      description: "Deep-seated assumptions, shaped by identity and experience",
      letter: "U"
    },
    {
      title: "Repressed Motivation",
      description: "Fear, guilt, or loyalty hiding beneath logic",
      letter: "R"
    },
    {
      title: "Projection",
      description: "Past experiences assigned to current courtroom figures",
      letter: "P"
    },
    {
      title: "Defense Mechanisms",
      description: "Rationalizing away contradiction to maintain internal consistency",
      letter: "D"
    }
  ]

  return (
    <section className="min-h-screen flex items-center py-32 bg-background">
      <div className="container">
        <div className="max-w-6xl mx-auto">
          <div className="text-left mb-20">
            <span className="section-label inline-block mb-6">CAPABILITIES</span>
            <h2 className="mb-6">What Our Agents Simulate</h2>
            <p className="text-lg text-text-secondary max-w-4xl">
              Our AI jurors don't just analyze evidence—they embody the complex psychological patterns that drive real human decision-making
            </p>
          </div>
          
          <div className="grid grid-cols-1 gap-8">
            {capabilities.map((capability, index) => (
              <div key={index} className="capability-card group w-full">
                <div className="flex items-start gap-6">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#FF6B35] to-[#F7461E] rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300">
                      <span className="text-2xl font-bold text-white">{capability.letter}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="capability-title mb-3 text-xl font-semibold">{capability.title}</h3>
                    <p className="text-text-secondary leading-relaxed text-base">{capability.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-16 text-center">
            <div className="bg-gradient-to-r from-[#FF6B35]/10 to-[#F7461E]/10 rounded-2xl p-8 border border-[#FF6B35]/20">
              <h3 className="text-xl font-semibold mb-4 text-[#FF6B35]">The Psychology Behind the Verdict</h3>
              <p className="text-text-secondary leading-relaxed max-w-4xl mx-auto">
                Traditional jury research focuses on demographics and stated opinions. Our AI agents go deeper, 
                modeling the unconscious psychological forces that truly shape how people process evidence and reach decisions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}