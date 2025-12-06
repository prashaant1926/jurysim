import Link from 'next/link'
import Image from 'next/image'

export default function HeroSection() {
  return (
    <section className="min-h-screen flex items-center pt-40 pb-32">
      <div className="container">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          {/* Left Content */}
          <div>
            <h1 className="mb-6">
            Juries Don’t Hear Facts. They Hear Frames.

            </h1>
            
            <p className="mb-12 text-text-secondary text-lg">
              Gideon AI reveals how different juries respond to your case.
              Watch agents deliberate, disagree, and decide—so you can shape your strategy with clarity.
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Link href="/demo" className="btn-primary">
                Request Demo
              </Link>
              <Link href="/watch" className="btn-secondary">
                Watch Deliberation
              </Link>
            </div>
          </div>
          
          {/* Right Visual */}
          <div className="relative">
            <div className="relative w-full h-[500px] lg:h-[600px]">
              <Image
                src="/images/juryAI.png"
                alt="AI Jury Deliberation Visualization"
                fill
                className="object-contain"
                style={{ scale: '3', left: '400px', top: '-300px', zIndex: '0', opacity: '1'}}  
                priority
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}