import Link from 'next/link'
export default function ClosingSection() {
  return (
    <section 
      className="relative overflow-hidden"
      style={{ 
        background: 'linear-gradient(135deg, #7C6F64 0%, #5D4E46 100%)'
      }}
    >
      <div className="container">
        <div style={{ paddingTop: '80px', paddingBottom: '80px' }}>
          <div className="max-w-4xl">
            <h2 
              className="text-4xl md:text-5xl font-bold mb-6"
              style={{ color: '#FFFFFF' }}
            >
              Gideon doesn't just simulate verdicts.
            </h2>
            <p 
              className="text-2xl md:text-3xl mb-10"
              style={{ color: 'rgba(255, 255, 255, 0.9)' }}
            >
              It simulates how people feel, react, and defend those decisions. Start preparing like the deliberation has already begun.
            </p>
            <div>
              <Link 
                href="/demo" 
                className="btn-primary"
                style={{ 
                  padding: '20px 48px',
                  fontSize: '18px',
                  fontWeight: '500',
                  borderRadius: '8px',
                  display: 'inline-block'
                }}
              >
                Request a Simulation
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}