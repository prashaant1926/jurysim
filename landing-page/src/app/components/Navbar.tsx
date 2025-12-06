import Link from 'next/link'

export default function Navbar() {
  return (
    <div className="fixed top-8 left-20 right-20 z-50">
      <nav>
        <div className="px-8 lg:px-16">
          <div className="py-8">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <Link href="/" className="text-4xl font-bold text-text-primary font-serif tracking-tight">
                Gideon
              </Link>
              
              {/* Navigation Items */}
              <div className="flex items-center gap-12">
                <Link 
                  href="/login" 
                  className="text-lg text-text-secondary hover:text-text-primary transition-colors font-medium"
                >
                  Login
                </Link>
                <Link 
                  href="/demo" 
                  className="btn-primary"
                >
                  Request Demo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </div>
  )
}