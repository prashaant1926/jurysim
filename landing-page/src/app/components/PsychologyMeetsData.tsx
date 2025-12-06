export default function PsychologyMeetsData() {
  const dataSources = [
    "U.S. Census & ACS microdata",
    "General Social Survey (GSS)",
    "Focus groups & trial transcripts",
    "Regional, attitudinal, and political datasets"
  ]

  return (
    <section className="min-h-screen flex items-center py-32 bg-background">
      <div className="container">
        <div className="max-w-4xl mx-auto">
          <h2 className="mb-12">Psychology Meets Data</h2>
          <p className="mb-12">
            Gideon AI combines Freudian theory with real-world data sources to model how real people make decisions under pressure.
          </p>
          
          <div className="mb-12">
            <p className="font-semibold mb-6">We use:</p>
            <ul className="space-y-4">
              {dataSources.map((source, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-primary mr-3 flex-shrink-0">•</span>
                  <span>{source}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <p className="text-lg lg:text-xl">
            This lets you construct realistic jury pools and explore how different compositions interpret the same case.
          </p>
        </div>
      </div>
    </section>
  )
}