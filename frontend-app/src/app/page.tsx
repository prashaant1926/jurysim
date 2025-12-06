export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center py-32 pt-40">
        <div className="container">
          <div className="max-w-5xl mx-auto text-center">
            <span className="section-label">Welcome to FreudLaw</span>
            <h1 className="font-serif text-4xl md:text-6xl font-bold text-text-primary mb-6 tracking-tight leading-tight">
              AI-Powered Legal Services for Modern Law Firms
            </h1>
            <p className="text-xl md:text-2xl text-text-secondary mb-12 leading-relaxed max-w-3xl mx-auto">
              Transform your legal practice with intelligent automation, advanced document analysis, and data-driven insights.
            </p>
            <div className="flex gap-6 justify-center">
              <button className="btn-primary">
                Get Started
              </button>
              <button className="btn-secondary">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 bg-card-bg">
        <div className="container">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="section-label">Features</span>
              <h2 className="font-serif text-3xl md:text-5xl font-bold text-text-primary mb-6">
                Powerful Tools for Legal Excellence
              </h2>
              <p className="text-xl text-text-secondary max-w-3xl mx-auto">
                Our platform combines cutting-edge AI technology with deep legal expertise to deliver unprecedented efficiency.
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="card">
                <h3 className="font-serif text-2xl font-semibold mb-4 text-text-primary">
                  Document Analysis
                </h3>
                <p className="text-text-secondary">
                  Instantly analyze contracts, briefs, and legal documents with AI-powered insights and recommendations.
                </p>
              </div>
              
              <div className="card">
                <h3 className="font-serif text-2xl font-semibold mb-4 text-text-primary">
                  Case Research
                </h3>
                <p className="text-text-secondary">
                  Access comprehensive case law databases and get intelligent research assistance powered by machine learning.
                </p>
              </div>
              
              <div className="card">
                <h3 className="font-serif text-2xl font-semibold mb-4 text-text-primary">
                  Client Management
                </h3>
                <p className="text-text-secondary">
                  Streamline client communications, case tracking, and billing with our integrated practice management tools.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-serif text-3xl md:text-5xl font-bold text-text-primary mb-6">
              Ready to Transform Your Practice?
            </h2>
            <p className="text-xl text-text-secondary mb-12">
              Join thousands of legal professionals who are already using FreudLaw to work smarter, not harder.
            </p>
            <button className="btn-primary">
              Schedule a Demo
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}