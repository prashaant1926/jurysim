import Header from './components/Header'
import HeroSection from './components/HeroSection'
import ValueProposition from './components/ValueProposition'
import ProblemStatement from './components/ProblemStatement'
import HowItWorks from './components/HowItWorks'
import AgentCapabilities from './components/AgentCapabilities'
import ClosingSection from './components/ClosingSection'
import Footer from './components/Footer'

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main>
        <HeroSection />
        <ProblemStatement />
        <ValueProposition />
        <HowItWorks />
        <AgentCapabilities />
        <ClosingSection />
      </main>
      
      <Footer />
    </div>
  )
}