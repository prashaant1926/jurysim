export default function ProblemStatement() {
  return (
    <section 
      className="relative overflow-hidden"
      style={{ 
        background: 'linear-gradient(135deg, #7C6F64 0%, #5D4E46 100%)'
      }}
    >
      {/* Content */}
      <div className="container">
        <div style={{ paddingTop: '80px', paddingBottom: '80px' }}>
          <div className="max-w-4xl">
            <h2 
              className="text-4xl md:text-5xl font-bold mb-6"
              style={{ color: '#FFFFFF' }}
            >
              You only get one jury.
            </h2>
            <h3 
              className="text-3xl md:text-4xl font-light mb-10"
              style={{ color: '#FFFFFF' }}
            >
              Gideon can help you prepare across thousands.
            </h3>
            
            <div className="w-20 h-1 mb-10" style={{ backgroundColor: 'rgba(255, 255, 255, 0.3)' }} />
            
            <p 
              className="text-xl md:text-2xl leading-relaxed"
              style={{ color: 'rgba(255, 255, 255, 0.9)' }}
            >
              Most tools focus on facts. Gideon AI focuses on how people process 
              those facts—emotionally, socially, and unconsciously.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}