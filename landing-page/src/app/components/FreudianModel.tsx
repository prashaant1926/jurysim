export default function FreudianModel() {
  const concepts = [
    {
      term: "Id —",
      description: "Emotional impulses and reflexes"
    },
    {
      term: "Ego —",
      description: "Conscious reasoning and deliberation"
    },
    {
      term: "Superego —",
      description: "Guilt, morality, and social pressure"
    }
  ]

  return (
    <section className="min-h-screen flex items-center py-32 bg-[#F8F6F4]">
      <div className="container">
        <div className="max-w-4xl mx-auto">
          <h2 className="mb-16">Freudian AI Agents</h2>
          
          <div className="space-y-12 mt-12">
            {concepts.map((concept, index) => (
              <div key={index} className="flex gap-6 items-start">
                <span className="text-primary font-bold flex-shrink-0">{concept.term}</span>
                <p className="text-text-secondary">{concept.description}</p>
              </div>
            ))}
          </div>
          
          <p className="mt-12 text-lg lg:text-xl">
            Our agents reflect the internal tensions that shape real-world verdicts.
          </p>
        </div>
      </div>
    </section>
  )
}