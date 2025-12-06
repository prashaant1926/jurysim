import Image from 'next/image'

export default function ValueProposition() {
  const cards = [
    {
      title: "See Inside the Deliberation Room",
      description: "Understand how personalities, backgrounds, and group dynamics influence every decision in real-time jury simulations.",
      image: "/images/deliberation.png"
    },
    {
      title: "Prepare with Psychological Precision",
      description: "Understand how emotion, identity, and perception influence the verdict. Don't just build a case—build the version that sticks.",
      image: "/images/aiEmotion.png"
    },
    {
      title: "Find What Persuades—And What Backfires",
      description: "Test multiple versions of your case narrative to identify the arguments that resonate most across diverse jury profiles.",
      image: "/images/argument.png"
    }
  ]

  return (
    <section className="min-h-screen flex items-center py-40 bg-[#F8F6F4]">
      <div className="container px-8 lg:px-16">
        <div className="text-center mb-20">
          <h2>Why Gideon AI</h2>
        </div>
        <div className="flex flex-col gap-16 w-full">
          {cards.map((card, index) => {
            const isEven = index % 2 === 0;
            return (
              <div 
                key={index} 
                className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 flex flex-row overflow-hidden mx-4" 
                style={{ height: '80vh' }}
              >
                {isEven ? (
                  // Image on left, text on right
                  <>
                    {card.image && (
                      <div className="relative w-1/2 h-full flex-shrink-0" style={{ padding: '48px' }}>
                        <Image
                          src={card.image}
                          alt={card.title}
                          fill
                          className="object-contain"
                          style={{ transform: 'scale(0.7)' }}
                        />
                      </div>
                    )}
                    <div className="w-1/2 flex flex-col justify-center" style={{ backgroundColor: '#7C6F64', padding: '64px' }}>
                      <h3 className="mb-6 text-left" style={{ color: 'white', fontFamily: 'Playfair Display, serif', fontSize: '2.5rem' }}>{card.title}</h3>
                      <p className="text-sm leading-relaxed text-left mb-8" style={{ color: 'white' }}>
                        {card.description}
                      </p>
                      <a href="#" className="text-white underline hover:no-underline transition-all">
                        Explore Simulation →
                      </a>
                    </div>
                  </>
                ) : (
                  // Text on left, image on right
                  <>
                    <div className="w-1/2 flex flex-col justify-center" style={{ backgroundColor: '#7C6F64', padding: '64px' }}>
                      <h3 className="mb-6 text-left" style={{ color: 'white', fontFamily: 'Playfair Display, serif', fontSize: '2.5rem' }}>{card.title}</h3>
                      <p className="text-sm leading-relaxed text-left mb-8" style={{ color: 'white' }}>
                        {card.description}
                      </p>
                      <a href="#" className="text-white underline hover:no-underline transition-all">
                        Explore Simulation →
                      </a>
                    </div>
                    {card.image && (
                      <div className="relative w-1/2 h-full flex-shrink-0" style={{ padding: '48px' }}>
                        <Image
                          src={card.image}
                          alt={card.title}
                          fill
                          className="object-contain"
                          style={{ transform: 'scale(0.7)' }}
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  )
}