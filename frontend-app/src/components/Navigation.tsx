import Link from 'next/link';

export function Navigation() {
  return (
    <nav className="bg-gray-900 text-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold">
            FreudLaw
          </Link>
          <div className="flex space-x-6">
            <Link href="/" className="hover:text-gray-300 transition-colors">
              Home
            </Link>
            <Link href="/deliberation" className="hover:text-gray-300 transition-colors">
              Jury Deliberation
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}