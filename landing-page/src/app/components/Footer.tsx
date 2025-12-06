import Link from 'next/link'

export default function Footer() {
  const footerLinks = {
    product: [
      { name: 'AI Platform', href: '/platform' },
      { name: 'Features', href: '/features' },
      { name: 'Pricing', href: '/pricing' }
    ],
    company: [
      { name: 'About', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Contact', href: '/contact' }
    ],
    legal: [
      { name: 'Privacy', href: '/privacy' },
      { name: 'Terms', href: '/terms' },
      { name: 'Security', href: '/security' }
    ]
  }

  return (
    <footer className="border-t border-border-light" style={{ paddingTop: '100px', paddingBottom: '100px' }}>
      <div className="container">
        <div className="grid md:grid-cols-5 gap-8 mb-12">
          <div className="md:col-span-2">
            <h3 className="text-lg font-medium mb-4 font-serif">Gideon</h3>
            <p className="text-text-muted text-sm">
              AI-powered jury simulation for modern trial lawyers.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-sm">Product</h4>
            <ul className="space-y-3 text-sm">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-text-muted hover:text-text-primary transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-sm">Company</h4>
            <ul className="space-y-3 text-sm">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-text-muted hover:text-text-primary transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4 text-sm">Legal</h4>
            <ul className="space-y-3 text-sm">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-text-muted hover:text-text-primary transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-border-light text-text-muted text-sm">
          <p>© 2025 Gideon AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}